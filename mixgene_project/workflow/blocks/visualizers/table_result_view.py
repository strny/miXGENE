# -*- coding: utf-8 -*-

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


log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class TableResultView(GenericBlock):
    block_base_name = "TR_VIEW"
    block_group = GroupType.VISUALIZE
    name = "Table Result view"

    is_block_supports_auto_execution = False

    _block_actions = ActionsList([
        ActionRecord("save_params", ["created", "valid_params", "done", "ready", "input_bound"], "validating_params",
                     user_title="Save parameters"),
        ActionRecord("on_params_not_valid", ["validating_params"], "created"),
        ActionRecord("on_params_is_valid", ["validating_params"], "valid_params"),
    ])

    input_table_result = InputBlockField(name="tr", order_num=10,
                               required_data_type="TableResult", required=True)

    _table_for_js = BlockField(name="table_js", field_type=FieldType.RAW, is_a_property=True)

    elements = BlockField(name="elements", field_type=FieldType.SIMPLE_LIST, init_val=[
        "table_result_view.html"
    ])

    @property
    def table_js(self):
        tr = self.get_input_var("tr")
        """:type :TableResult"""
        if tr:
            table = tr.get_table()
            table_headers = ["#"] + table.columns.tolist()

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
                    table.to_records().tolist() #[:100]
                ]
            }
        else:
            None
