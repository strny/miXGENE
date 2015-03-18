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


class EnrichmentVisualize(GenericBlock):
    block_base_name = "EV_VIEW"
    block_group = GroupType.VISUALIZE
    name = "Enrichment Visualize"

    is_block_supports_auto_execution = False

    _block_actions = ActionsList([
        ActionRecord("save_params", ["created", "valid_params", "done", "ready", "input_bound"], "validating_params",
                     user_title="Save parameters"),
        ActionRecord("on_params_not_valid", ["validating_params"], "created"),
        ActionRecord("on_params_is_valid", ["validating_params"], "valid_params")
    ])

    _input_dictionary_set = InputBlockField(name="ds", order_num=10,
                               required_data_type="DictionarySet", required=True)

    _table_for_js = BlockField(name="table_js", field_type=FieldType.RAW, is_a_property=True)

    _export_raw_results_url = BlockField(name="export_raw_results_url",
                                   field_type=FieldType.STR, is_a_property=True)

    _export_results_csv_url = BlockField(name="export_results_csv_url",
                                   field_type=FieldType.STR, is_a_property=True)


    elements = BlockField(name="elements", field_type=FieldType.SIMPLE_LIST, init_val=[
        "enrichment_view.html"
    ])

    @property
    def export_results_csv_url(self):
        return reverse("block_field_formatted", kwargs={
            "exp_id": self.exp_id,
            "block_uuid": self.uuid,
            "field": "export_csv",
            "format": "csv"
        })

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
            table_headers = ['comodule','(term, p-val)','genes']

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
                    [(k, v[1], v[0]) for k, v in table.iteritems()]
                    #table.to_records().tolist() #[:100]
                ]
            }
        else:
            return None

    def export_json(self, exp, *args, **kwargs):
        ds = self.get_input_var("ds")
        dic = ds.load_dict()
        return dic

    def export_csv(self, exp, *args, **kwargs):
        import csv
        import StringIO
        ds = self.get_input_var("ds")
        dic = ds.load_dict()
        out = StringIO.StringIO()
        w = csv.writer(out)
        w.writerows(dic.items())
        out.seek(0)
        return out.read()
