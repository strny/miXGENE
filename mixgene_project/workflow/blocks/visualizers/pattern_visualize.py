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
    InputBlockField
from workflow.blocks.generic import GenericBlock

from django.core.urlresolvers import reverse

from environment.structures import ComoduleSet
from wrappers.pattern_search.pattern_filter import get_patterns
from wrappers.pattern_search.pattern_filter import differential_expression
from scipy.stats import zscore
from wrappers.pattern_search.utils import translate_inters
from wrappers.pattern_search.utils import mergeNetworks
import traceback
import sys

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class PatternView(GenericBlock):
    block_base_name = "PA_VIEW"
    block_group = GroupType.VISUALIZE
    name = "Patterns Visualizer"

    is_block_supports_auto_execution = False

    _block_actions = ActionsList([
        ActionRecord("save_params", ["created", "valid_params", "done", "ready"], "validating_params",
                     user_title="Save parameters"),
        ActionRecord("on_params_is_valid", ["validating_params"], "valid_params"),
        ActionRecord("on_params_not_valid", ["validating_params"], "created"),

        ActionRecord("process_upload", ["valid_params", "processing_upload"],
                     "processing_upload", "Process uploaded data"),
        ActionRecord("success", ["processing_upload"], "done", reload_block_in_client=True),
        ActionRecord("error", ["processing_upload"], "valid_params"),
    ])

    _input_es = InputBlockField(name="es", order_num=10,
        required_data_type="ExpressionSet", required=True)

    _upload_gene2gene_platform = ParamField("upload_gene2gene_platform", title="PPI platform", order_num=12,
                                           input_type=InputType.FILE_INPUT, field_type=FieldType.CUSTOM)

    _input_comodule_set = InputBlockField(name="cs", order_num=20,
                                         required_data_type="ComoduleSet", required=True)

    _gene2gene = InputBlockField(name="gene2gene", order_num=30,
                                required_data_type="BinaryInteraction",
                                required=True)

    _graph_for_js = BlockField(name="graph_js", field_type=FieldType.RAW, is_a_property=True)

    _edges_for_js = BlockField(name="edges", field_type=FieldType.RAW, is_a_property=False)

    _export_raw_results_url = BlockField(name="export_raw_results_url",
                                   field_type=FieldType.STR, is_a_property=True)



    elements = BlockField(name="elements", field_type=FieldType.SIMPLE_LIST, init_val=[
        "pattern_view.html"
    ])


    @property
    def export_raw_results_url(self):
        return reverse("block_field_formatted", kwargs={
            "exp_id": self.exp_id,
            "block_uuid": self.uuid,
            "field": "export_json",
            "format": "json"
        })


    @property
    def graph_js(self):
        scope = self.get_scope()
        scope.load()
        edges = scope.get_temp_var("edges_%s" % self.uuid)
        diff_expr = scope.get_temp_var("diff_expr_%s" % self.uuid)

        cs = self.get_input_var("cs")
        pattern_set = cs.load_set().values()
        import random as rnd
        import math
        if edges:
            # comodule = pattern_set[0]
            # edges_0 = edges[0]
            res = {
                "nodes": [
                    {"id": "%s_%s" % (j, gene),
                    "label": gene,
                    "x": math.cos(2*i*math.pi/len(com)) + 5*math.cos(2*j*math.pi/len(pattern_set)),
                    "y": math.sin(2*i*math.pi/len(com)) + 5*math.sin(2*j*math.pi/len(pattern_set)),
                    "color": "rgb(%s, %s, %s)" % (int(math.floor(((diff_expr[gene] + 1) * 128) - 1)), int(math.floor(255-(((diff_expr[gene] + 1)*128) - 1))), 0),
                    "size": 10}
                    for j, com in enumerate(pattern_set) for i, gene in enumerate(com)
                ],
                "edges": [
                    {"id": "%s_%s_%s" % (k, i, j),
                     "source": "%s_%s" % (k, i),
                     "target": "%s_%s" % (k, j)}
                    for k, graph_edges in enumerate(edges) for i, j in graph_edges
                ]
            }
            return res
            # table_headers = ['key', 'value']
            #
            # column_title_to_code_name = {
            #     title: "_" + hashlib.md5(title).hexdigest()[:8]
            #     for title in table_headers
            # }
            # fields_list = [column_title_to_code_name[title] for title in table_headers]
            #
            # return {
            #     "columns": [
            #         {
            #             "title": title,
            #             "field": column_title_to_code_name[title],
            #             "visible": True
            #         }
            #         for title in table_headers
            #     ],
            #     "rows": [
            #         dict(zip(fields_list, row))
            #         for row in
            #         [(k, list(v)) for k, v in table.iteritems()]
            #         #table.to_records().tolist() #[:100]
            #     ]
            # }
        else:
            return None

    def export_json(self, exp, *args, **kwargs):
        ds = self.get_input_var("es")
        dic = ds.load_set()
        return dic

    def process_upload(self, exp, *args, **kwargs):
        """
            @param exp: Experiment
        """
        # TODO: move to celery
        try:
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

            gene2gene = gene2gene.load_pairs()
            gene2gene = translate_inters(gene2gene, gene_platform, symmetrize=True, tolower=False)
            mData = es.get_assay_data_frame()
            nw = gene2gene
            # data = mData
            mData.set_index(mData.columns[0], inplace=True, drop=True)
            # data = zscore(data)
            pheno = es.get_pheno_data_frame()
            classes = pheno[es.pheno_metadata['user_class_title']].values
            pattern_set = cs.load_set()
            scope = self.get_scope()
            scope.load()
            edges = get_patterns(pattern_set.values(), mData, classes, nw)
            diff_expr = differential_expression(mData, classes)
            scope.set_temp_var("edges_%s" % self.uuid, edges)
            scope.set_temp_var("diff_expr_%s" % self.uuid, diff_expr)
            scope.store()
            self.do_action("success", exp)
        except Exception as e:
            ex_type, ex, tb = sys.exc_info()
            traceback.print_tb(tb)
            self.do_action("error", exp, e)

    def success(self, exp, *args, **kwargs):
        pass