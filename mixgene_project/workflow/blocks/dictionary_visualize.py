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

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class DictionarySetView(GenericBlock):
    block_base_name = "DS_VIEW"
    block_group = GroupType.VISUALIZE
    name = "Dictionary Set view"

    is_block_supports_auto_execution = False

    _block_actions = ActionsList([
        ActionRecord("save_params", ["created", "valid_params", "done", "ready", "input_bound"], "validating_params",
                     user_title="Save parameters"),

        ActionRecord("on_params_not_valid", ["validating_params"], "created"),
        ActionRecord("on_params_is_valid", ["validating_params"], "valid_params"),

        #ActionRecord("compute_pca", ["valid_params"], "computing_pca", user_title="Compute PCA"),
        #ActionRecord("pca_done", ["computing_pca"], "done",),

        #ActionRecord("reset_execution", ["*", "done", "execution_error", "ready", "working"], "ready",
        #             user_title="Reset execution")

        #ActionRecord("update", ["input_bound", "ready"], "ready"),
    ])

    _input_dictionary_set = InputBlockField(name="ds", order_num=10,
                               required_data_type="DictionarySet", required=True)

    _table_for_js = BlockField(name="table_js", field_type=FieldType.RAW, is_a_property=True)

    #chart_series = BlockField(name="chart_series", field_type=FieldType.RAW, init_val=[])
    #chart_categories = BlockField(name="chart_categories", field_type=FieldType.SIMPLE_LIST,
    #                              init_val=[])

    _export_raw_results_url = BlockField(name="export_raw_results_url",
                                   field_type=FieldType.STR, is_a_property=True)



    elements = BlockField(name="elements", field_type=FieldType.SIMPLE_LIST, init_val=[
        "dictionary_set_view.html"
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
    def table_js(self):
        cs = self.get_input_var("ds")
        """:type :DictionarySet"""
        if cs:
            table = cs.load_dict()
            table_headers = ['key', 'value']

            column_title_to_code_name = {
                title: "_" + hashlib.md5(title).hexdigest()[:8]
                for title in table_headers
            }
            fields_list = [column_title_to_code_name[title] for title in table_headers]

            return {
                "columns": [
                    {
                        "title": title,
                        "field": column_title_to_code_name[title],
                        "visible": True
                    }
                    for title in table_headers
                ],
                "rows": [
                    dict(zip(fields_list, row))
                    for row in
                    [(k, list(v)) for k, v in table.iteritems()]
                    #table.to_records().tolist() #[:100]
                ]
            }
        else:
            return None

    def export_json(self, exp, *args, **kwargs):
        ds = self.get_input_var("ds")
        dic = ds.load_dict()
        return dic
