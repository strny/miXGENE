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


class ComoduleSetView(GenericBlock):
    block_base_name = "CS_VIEW"
    block_group = GroupType.VISUALIZE
    name = "Comodule Set View"

    is_block_supports_auto_execution = False

    _block_actions = ActionsList([
        ActionRecord("save_params", ["created", "valid_params", "done", "ready", "input_bound"], "validating_params",
                     user_title="Save parameters"),
        ActionRecord("on_params_not_valid", ["validating_params"], "created"),
        ActionRecord("on_params_is_valid", ["validating_params"], "valid_params"),
    ])

    input_comodule_set = InputBlockField(name="cs", order_num=10,
                                         required_data_type="ComoduleSet", required=True)
    _table_for_js = BlockField(name="table_js", field_type=FieldType.RAW, is_a_property=True)
    _export_raw_results_url = BlockField(name="export_raw_results_url",
                                         field_type=FieldType.STR, is_a_property=True)
    _export_results_csv_url = BlockField(name="export_results_csv_url",
                                   field_type=FieldType.STR, is_a_property=True)
    elements = BlockField(name="elements", field_type=FieldType.SIMPLE_LIST, init_val=[
        "comodule_set_view.html"
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
        cs = self.get_input_var("cs")
        """:type :ComoduleSet"""
        if cs:
            table = cs.load_set()
            """:type :dict"""
            if isinstance(table[0], set):
                columns = ["values"]
            else:
                columns = ["values", "values"]

            # table_headers = ["#"] + table.columns.tolist()
            table_headers = ["#"] + columns
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
                        dict(zip(fields_list, [idx, value]))
                        for idx, value in
                            table.iteritems()  # [:100]
                ]
            }
        else:
            return None

    def export_json(self, exp, *args, **kwargs):
        ds = self.get_input_var("cs")
        table = ds.load_set()
        return [(idx, list(value)) for idx, value in table.iteritems()]


    def export_csv(self, exp, *args, **kwargs):
        import csv
        import StringIO
        ds = self.get_input_var("cs")
        tab = ds.load_set()
        out = StringIO.StringIO()
        w = csv.writer(out)
        w.writerows(tab.items())
        out.seek(0)
        return out.read()
