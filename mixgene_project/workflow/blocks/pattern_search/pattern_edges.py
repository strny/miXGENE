__author__ = 'pavel'

__author__ = 'pavel'


from collections import defaultdict
import hashlib
import logging

import numpy as np
from sklearn import decomposition

from mixgene.util import log_timing
from webapp.tasks import wrapper_task
from workflow.blocks.blocks_pallet import GroupType
from workflow.blocks.fields import FieldType, BlockField, InputType, ParamField, ActionsList, ActionRecord, \
    InputBlockField, OutputBlockField
from workflow.blocks.generic import GenericBlock, save_params_actions_list, execute_block_actions_list

from django.core.urlresolvers import reverse

from environment.structures import Edges, DiffExpr
from wrappers.pattern_search.pattern_filter import get_patterns
from wrappers.pattern_search.pattern_filter import differential_expression
from scipy.stats import zscore
from wrappers.pattern_search.utils import translate_inters
from wrappers.pattern_search.utils import mergeNetworks
import traceback
import sys

from django.conf import settings


log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

def compute_edges(exp, block,
            m_rna_es,
            comodule_set,
            gene2gene,
            gene_platform,
            base_filename):
    """
        @type m_rna_es: ExpressionSet
        @type mi_rna_es: ExpressionSet
        @type comodule_set: ComoduleSet
        @type gene2gene: BinaryInteraction
    """
    if settings.CELERY_DEBUG:
        import sys
        sys.path.append('/Migration/skola/phd/projects/miXGENE/mixgene_project/wrappers/pycharm-debug.egg')
        import pydevd
        pydevd.settrace('localhost', port=6901, stdoutToServer=True, stderrToServer=True)

    es = m_rna_es
    cs = comodule_set
    gene2gene = gene2gene.load_pairs()
    gene2gene = translate_inters(gene2gene, gene_platform, symmetrize=True, tolower=False)
    mData = es.get_assay_data_frame()
    nw = gene2gene
    mData.set_index(mData.columns[0], inplace=True, drop=True)
    pheno = es.get_pheno_data_frame()
    classes = pheno[es.pheno_metadata['user_class_title']].values
    pattern_set = cs.load_set()

    edges = get_patterns(pattern_set.values(), mData, classes, nw)
    edges_type = Edges(exp.get_data_folder(), base_filename)
    edges_type.store_edges(edges)

    diff_expr = differential_expression(mData, classes)
    diff_type = DiffExpr(exp.get_data_folder(), base_filename)
    diff_type.store_expr(diff_expr)

    return [edges_type, diff_type], {}


class PatternEdges(GenericBlock):
    block_base_name = "PA_EDGES"
    block_group = GroupType.PATTERN_SEARCH
    name = "Patterns Edges"

    is_block_supports_auto_execution = True

    _block_actions = ActionsList([
        ActionRecord("save_params", ["created", "valid_params", "done", "ready"], "validating_params",
                     user_title="Save parameters"),
        ActionRecord("on_params_is_valid", ["validating_params"], "ready"),
        ActionRecord("on_params_not_valid", ["validating_params"], "created"),
        ])
    _block_actions.extend(execute_block_actions_list)

    _input_es = InputBlockField(name="es", order_num=10,
        required_data_type="ExpressionSet", required=True)

    _upload_gene2gene_platform = ParamField("upload_gene2gene_platform", title="PPI platform", order_num=12,
                                           input_type=InputType.FILE_INPUT, field_type=FieldType.CUSTOM)

    _input_comodule_set = InputBlockField(name="cs", order_num=20,
                                         required_data_type="ComoduleSet", required=True)

    _gene2gene = InputBlockField(name="gene2gene", order_num=30,
                                required_data_type="BinaryInteraction",
                                required=True)

    edges = OutputBlockField(name="edges", provided_data_type="Edges")

    diff_expr = OutputBlockField(name="diff_expr", provided_data_type="DiffExpr")

    def execute(self, exp, *args, **kwargs):
        self.clean_errors()
        cs = self.get_input_var("cs")
        """:type :ComoduleSet"""
        es = self.get_input_var("es")
        """:type :ExpressionSet"""
        gene_platform = self.upload_gene2gene_platform
        gene2gene = self.get_input_var("gene2gene")
        """:type :BinaryInteraction"""
        gene_platform = gene_platform.get_file()
        with open(gene_platform.path) as f:
            for line in f:
                gene_platform = line.split(',')
                self.clean_errors()

        self.celery_task = wrapper_task.s(
            compute_edges,
            exp, self,
            m_rna_es = es,
            comodule_set = cs,
            gene2gene = gene2gene,
            gene_platform = gene_platform,
            base_filename="%s_pattern_edges" % self.uuid
        )
        exp.store_block(self)
        self.celery_task.apply_async()



    # def export_json(self, exp, *args, **kwargs):
    #     ds = self.get_input_var("es")
    #     dic = ds.load_set()
    #     return dic

    def process_upload(self, exp, *args, **kwargs):
        """
            @param exp: Experiment
        """
        try:
            self.do_action("success", exp)
        except Exception as e:
            ex_type, ex, tb = sys.exc_info()
            traceback.print_tb(tb)
            self.do_action("error", exp, e)

    def success(self, exp, edges, diff_expr):
        self.set_out_var("edges", edges)
        self.set_out_var("diff_expr", diff_expr)
        exp.store_block(self)
