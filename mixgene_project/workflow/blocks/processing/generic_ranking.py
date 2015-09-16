__author__ = 'pavel'

from environment.structures import TableResult
from webapp.models import Experiment
from webapp.tasks import wrapper_task
from workflow.blocks.blocks_pallet import GroupType
from workflow.blocks.fields import ActionsList, ActionRecord, InputBlockField, ParamField, InputType, FieldType, \
    OutputBlockField
from workflow.blocks.generic import GenericBlock, execute_block_actions_list
import rpy2.robjects as R
import pandas.rpy.common as com
import pandas as pd

from mixgene.util import stopwatch
from environment.structures import TableResult

from django.conf import settings
import logging

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

R_LIB_CUSTOM_PATH = settings.R_LIB_CUSTOM_PATH


def apply_ranking(
        exp, block,
        es, ranking_name,
        result_table,
        pheno_class_column=None, options=None
):
    if not options:
        options = {}
    if not pheno_class_column:
        pheno_class_column = es.pheno_metadata["user_class_title"]

    R.r['source'](R_LIB_CUSTOM_PATH + '/ranking.Methods.r')
    func = R.r[ranking_name]
    if settings.CELERY_DEBUG:
        import sys
        sys.path.append('/Migration/skola/phd/projects/miXGENE/mixgene_project/wrappers/pycharm-debug.egg')
        import pydevd
        pydevd.settrace('localhost', port=6901, stdoutToServer=True, stderrToServer=True)

    assay_df = es.get_assay_data_frame()
    cols = assay_df.columns

    # We must rename cols to be unique for R
    out_genes = {}
    out_cols = []
    for i, g in enumerate(cols):
        g = g.split('.')[0]
        if g in out_genes:
            new_g = g + '__' + str(i)
            out_genes[g].append(new_g)
            out_cols.append(new_g)
        else:
            out_genes[g] = [g]
            out_cols.append(g)
    assay_df.columns = out_cols
    assay_df = assay_df.T

    x = com.convert_to_r_matrix(assay_df)
    y = es.get_pheno_column_as_r_obj(pheno_class_column)
    exp.log(block.uuid, "Computing ranking: `%s` options: `%s`" % (ranking_name, options))
    log.debug("Computing ranking: `%s` options: `%s`", ranking_name, options)
    with stopwatch(name="Computing ranking: `%s` options: `%s`" % (ranking_name, options),
                   threshold=0.01):
        ranking_list = list(func(R.r['t'](x), y, **options))

    ranking_fixed = map(lambda a: int(a - 1), ranking_list)
    df = pd.DataFrame(
        index=assay_df.index,
        data=[len(assay_df)] * len(assay_df), columns=["rank"]
    )
    for rank, row_num in enumerate(ranking_fixed):
        df.ix[row_num, "rank"] = rank

    result_table.store_table(df)
    return [result_table], {}

class GenericRankingBlock(GenericBlock):
    block_base_name = ""
    block_group = GroupType.PROCESSING
    is_abstract = True

    is_block_supports_auto_execution = True

    _block_actions = ActionsList([
        ActionRecord("save_params", ["created", "valid_params", "done", "ready"], "validating_params",
                     user_title="Save parameters"),
        ActionRecord("on_params_is_valid", ["validating_params"], "ready"),
        ActionRecord("on_params_not_valid", ["validating_params"], "created"),
    ])
    _block_actions.extend(execute_block_actions_list)

    _es = InputBlockField(
        name="es", order_num=10,
        required_data_type="ExpressionSet", required=True
    )

    ## TODO: remove from generic ranking
    best = ParamField(
        name="best", title="Consider only best",
        input_type=InputType.TEXT,
        field_type=FieldType.INT, init_val=None
    )

    _result = OutputBlockField(name="result", field_type=FieldType.STR,
                               provided_data_type="TableResult", init_val=None)

    def __init__(self, *args, **kwargs):
        super(GenericRankingBlock, self).__init__(*args, **kwargs)
        self.ranking_name = None
        self.ranking_options = {}
        self.celery_task = None

        exp = Experiment.get_exp_by_id(self.exp_id)
        self.result = TableResult(
            base_dir=exp.get_data_folder(),
            base_filename="%s_gt_result" % self.uuid,
        )
        self.set_out_var("result", self.result)

    def collect_options(self):
        self.ranking_options = {}

    def execute(self, exp, *args, **kwargs):
        self.clean_errors()
        self.collect_options()

        self.celery_task = wrapper_task.s(
            apply_ranking,
            exp=exp, block=self,
            es=self.get_input_var("es"),
            ranking_name=self.ranking_name,
            result_table=self.result,
            options=self.ranking_options
        )
        exp.store_block(self)
        self.celery_task.apply_async()
        exp.log(self.uuid, "Sent ranking computation to queue")
        log.debug("Sent ranking computation to queue")

    def success(self, exp, result, *args, **kwargs):
        self.result = result
        self.set_out_var("result", self.result)
        exp.store_block(self)