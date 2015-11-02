__author__ = 'pavel'

import pandas as pd

from webapp.tasks import wrapper_task
from workflow.blocks.blocks_pallet import GroupType
from workflow.blocks.fields import ActionsList, ActionRecord, InputBlockField, ParamField, InputType, FieldType, \
    OutputBlockField
from workflow.blocks.generic import GenericBlock, execute_block_actions_list
from wrappers.aggregation.aggregation import pca_agg_task


def do_gs_agg(
    exp, block,
    es, gs, method,
    base_filename
):
    """
        @type es: ExpressionSet
    """
    if method == "pca":
        return pca_agg_task(exp, block, es, gs, base_filename)

    result_es = es.clone(base_filename)
    result_es.store_pheno_data_frame(es.get_pheno_data_frame())
    gene_sets = gs.get_gs()

    df = es.get_assay_data_frame().T

    df_list = []
    df_index_set = set(df.index)

    for set_name, gene_ids in gene_sets.genes.items():
        fixed_gene_ids = [gi for gi in gene_ids if gi in df_index_set]
        if fixed_gene_ids:
            sub_df = df.loc[fixed_gene_ids]
            if method == "mean":
                row = sub_df.mean()
            # TODO: median != mean
            if method == "median":
                row = sub_df.mean()

            df_list.append((set_name, row))

    result_df = pd.DataFrame(dict(df_list))
    result_es.store_assay_data_frame(result_df)

    return [result_es], {}


class GeneSetAgg(GenericBlock):
    block_base_name = "GENE_SET_AGG"
    name = "Gene Sets Aggregation"
    block_group = GroupType.AGGREGATION

    is_block_supports_auto_execution = True

    _block_actions = ActionsList([
        ActionRecord("save_params", ["created", "valid_params", "done", "ready"], "validating_params",
                     user_title="Save parameters"),
        ActionRecord("on_params_is_valid", ["validating_params"], "ready"),
        ActionRecord("on_params_not_valid", ["validating_params"], "created"),
    ])

    _block_actions.extend(execute_block_actions_list)

    _es = InputBlockField(name="es", order_num=10,
        required_data_type="ExpressionSet", required=True)
    _gs = InputBlockField(name="gs", order_num=20,
        required_data_type="GeneSets", required=True)

    agg_method = ParamField(
        "agg_method", title="Aggregate method", order_num=50,
        input_type=InputType.SELECT, field_type=FieldType.STR,
        init_val="mean",
        options={
            "inline_select_provider": True,
            "select_options": [
                ["mean", "Mean"],
                ["median", "Median"],
                ["pca", "PCA"]
            ]
        }
    )

    agg_es = OutputBlockField(name="agg_es", provided_data_type="ExpressionSet")

    def __init__(self, *args, **kwargs):
        super(GeneSetAgg, self).__init__(*args, **kwargs)
        self.celery_task = None

    def execute(self, exp, *args, **kwargs):
        self.clean_errors()
        es = self.get_input_var("es")
        gs = self.get_input_var("gs")

        base_filename = "%s_gs_agg" % (self.uuid, )

        self.celery_task = wrapper_task.s(
            do_gs_agg,
            exp, self,
            es, gs, self.agg_method,
            base_filename
        )

        exp.store_block(self)
        self.celery_task.apply_async()

    def success(self, exp, agg_es):
        self.set_out_var("agg_es", agg_es)
        exp.store_block(self)
