__author__ = 'pavel'

import pandas as pd
from webapp.tasks import wrapper_task
from workflow.blocks.blocks_pallet import GroupType
from workflow.blocks.fields import FieldType, BlockField, OutputBlockField, InputBlockField, InputType, ParamField, \
    ActionRecord, ActionsList

from workflow.blocks.generic import GenericBlock, save_params_actions_list, execute_block_actions_list

from converters.gene_set_tools import map_gene_sets_to_probes
from django.conf import settings
from wrappers.pattern_search.pattern_filter import pattern_filter
from environment.structures import ComoduleSet
import scipy.sparse as sp
# from wrappers.pattern_search.utils import translate_inters
from wrappers.pattern_search.utils import mergeNetworks
from wrappers.pattern_search.pattern_filter import pattern_filter
from environment.structures import GS, GeneSets
from scipy.stats import zscore

def pattern_filter_task(exp, block,
            m_rna_es,
            mi_rna_es,
            gene_sets,
            metric,
            n_best,
            base_filename):
    """
        @type m_rna_es: ExpressionSet
        @type mi_rna_es: ExpressionSet
        @type comodule_set: ComoduleSet
        @type metric: metric
        @type n_best: int
    """
    if settings.CELERY_DEBUG:
        import sys
        sys.path.append('/Migration/skola/phd/projects/miXGENE/mixgene_project/wrappers/pycharm-debug.egg')
        import pydevd
        pydevd.settrace('localhost', port=6901, stdoutToServer=True, stderrToServer=True)


    mData = m_rna_es.get_assay_data_frame()
    pheno = m_rna_es.get_pheno_data_frame()
    classes = pheno['User_class'].values

    data = mData
    data.set_index(data.columns[0], inplace=True, drop=True)

    # data = zscore(data)
    com_set = comodule_set.load_set()

    result = pattern_filter(com_set.values(), data, classes, n_best, metric)

    result = {key: value for key, value in enumerate(result)}
    gs = GS(None, result)
    cs = GeneSets(exp.get_data_folder(), base_filename)

    cs.store_set(gs)

    return [cs], {}


class PatternFilter(GenericBlock):
    block_base_name = "PattFilter"
    name = "Pattern Filter"
    block_group = GroupType.FILTER

    is_block_supports_auto_execution = True

    _block_actions = ActionsList([
        ActionRecord("save_params", ["created", "valid_params", "done", "ready"], "validating_params",
                     user_title="Save parameters"),
        ActionRecord("on_params_is_valid", ["validating_params"], "ready"),
        ActionRecord("on_params_not_valid", ["validating_params"], "created"),
        ])
    _block_actions.extend(execute_block_actions_list)

    _m_rna = InputBlockField(name="mRNA", order_num=10, required_data_type="ExpressionSet", required=True)
    _mi_rna = InputBlockField(name="miRNA", order_num=20, required_data_type="ExpressionSet", required=False)

    _gs = InputBlockField(name="gs", order_num=30, required_data_type="GeneSets", required=True)


    _metric = ParamField(
        "metric", title="Metric", order_num=40,
        input_type=InputType.SELECT, field_type=FieldType.STR,
        init_val="mutual_information",
        options={
            "inline_select_provider": True,
            "select_options": [
                ["mutual_information", "Mutual Information"],
                ['normed_mutual_information', "Normed Mutual Information"],
                ['square_error', "Square Error"],
                ['correlation', "Correlation"],
                ['t-test', "TTest"],
                ['wilcoxon', "Wilcoxon"]

            ]
        }
    )

    n_best = ParamField(name="n_best", order_num=50, title="# of best", input_type=InputType.TEXT, field_type=FieldType.INT, init_val=10)

    patterns = OutputBlockField(name="patterns", provided_data_type="GeneSets")

    def __init__(self, *args, **kwargs):
        super(PatternFilter, self).__init__(*args, **kwargs)
        self.celery_task = None

    def execute(self, exp, *args, **kwargs):
        self.clean_errors()

        self.celery_task = wrapper_task.s(
            pattern_filter_task,
            exp, self,
            m_rna_es = self.get_input_var("mRNA"),
            mi_rna_es = self.get_input_var("miRNA"),
            gene_sets = self.get_input_var("gs"),
            metric = self.metric,
            n_best = self.n_best,
            base_filename="%s_comodule_sets" % self.uuid
        )
        exp.store_block(self)
        self.celery_task.apply_async()

    def success(self, exp, gs):
        self.set_out_var("patterns", gs)
        exp.store_block(self)
