from webapp.tasks import wrapper_task
from workflow.blocks.blocks_pallet import GroupType
from workflow.blocks.fields import ActionsList, ActionRecord, InputBlockField, ParamField, InputType, FieldType, \
    OutputBlockField
from workflow.blocks.generic import GenericBlock, execute_block_actions_list
from wrappers.aggregation.aggregation import pca_agg_task_cv
from wrappers.aggregation.aggregation import preprocess_df_gs
import pandas as pd

__author__ = 'pavel'


def agg_task_mean(df, gene_sets, method):
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

    return pd.DataFrame(dict(df_list)).T


def agg_task_cv(
            exp,
            block,
            train_es,
            test_es,
            gene_sets,
            method,
            base_filename):
    """
        @type train_es, test_es: ExpressionSet
        @type gene_sets: GeneSets

    """
    if method == "pca":
        return pca_agg_task_cv(exp, block, train_es, test_es, gene_sets, base_filename)

    df_train = train_es.get_assay_data_frame()
    df_test = test_es.get_assay_data_frame()
    src_gs = gene_sets.get_gs()
    df_train, src_gs_train = preprocess_df_gs(df_train, src_gs)
    df_test, src_gs_test = preprocess_df_gs(df_test, src_gs)

    result_df_train = agg_task_mean(df_train, src_gs_train, method)
    result_df_test = agg_task_mean(df_test, src_gs_train, method)

    result_train = train_es.clone(base_filename + "_train")
    result_train.store_assay_data_frame(result_df_train)
    result_train.store_pheno_data_frame(train_es.get_pheno_data_frame())

    result_test = test_es.clone(base_filename + "_test")
    result_test.store_assay_data_frame(result_df_test)
    result_test.store_pheno_data_frame(test_es.get_pheno_data_frame())

    return [result_train, result_test], {}


class GeneSetAggCV(GenericBlock):
    block_group = GroupType.AGGREGATION
    block_base_name = "CV_GS_A"
    name = "CV Gene Sets Aggregation"
    is_block_supports_auto_execution = True

    _block_actions = ActionsList([
        ActionRecord("save_params", ["created", "valid_params", "done", "ready"], "validating_params",
                     user_title="Save parameters"),
        ActionRecord("on_params_is_valid", ["validating_params"], "ready"),
        ActionRecord("on_params_not_valid", ["validating_params"], "created"),
        ])
    _block_actions.extend(execute_block_actions_list)

    _input_train_es = InputBlockField(name="train_es", order_num=10,
                                      required_data_type="ExpressionSet", required=True)
    _input_test_es = InputBlockField(name="test_es", order_num=20,
                                     required_data_type="ExpressionSet", required=True)

    _input_gs = InputBlockField(name="gs", order_num=30,
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

    out_train_es = OutputBlockField(name="out_train_es", provided_data_type="ExpressionSet")
    out_test_es = OutputBlockField(name="out_test_es", provided_data_type="ExpressionSet")

    def __init__(self, *args, **kwargs):
        super(GeneSetAggCV, self).__init__(*args, **kwargs)
        self.celery_task = None

    def execute(self, exp, *args, **kwargs):
        self.clean_errors()
        train_es = self.get_input_var("train_es")
        test_es = self.get_input_var("test_es")

        gene_sets = self.get_input_var("gs")

        self.celery_task = wrapper_task.s(
            agg_task_cv,
            exp, self,
            train_es=train_es,
            test_es=test_es,
            gene_sets=gene_sets,
            method=self.agg_method,
            base_filename="%s_%s_agg" % (self.uuid, "pca_cv")
        )
        exp.store_block(self)
        self.celery_task.apply_async()

    def success(self, exp, out_train_es, out_test_es):
        self.set_out_var("out_train_es", out_train_es)
        self.set_out_var("out_test_es", out_train_es)
        exp.store_block(self)
