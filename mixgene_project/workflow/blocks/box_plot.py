# -*- coding: utf-8 -*-
import logging
import json

import numpy as np

from environment.structures import TableResult
from mixgene.util import log_timing
from webapp.tasks import wrapper_task
from workflow.blocks.fields import FieldType, BlockField, OutputBlockField, InputBlockField, InputType, ParamField, \
    ActionRecord, ActionsList
from workflow.blocks.generic import GenericBlock, save_params_actions_list, execute_block_actions_list
from workflow.blocks.rc_vizualize import RcVisualizer

from wrappers.boxplot_stats import boxplot_stats
from wrappers.gt import global_test_task
from wrappers.scoring import metrics


log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

import time

class BoxPlot(RcVisualizer):
    block_base_name = "BOX_PLOT"

    boxplot_config = ParamField(name="boxplot_config", title="",
                              input_type=InputType.HIDDEN,
                              field_type=FieldType.RAW)

    plot_inputs = BlockField(name="plot_inputs", field_type=FieldType.RAW, init_val=[])
    chart_series = BlockField(name="chart_series", field_type=FieldType.RAW,
                              init_val=[{"data": [], "name": "ML scores"}])
    chart_categories = BlockField(name="chart_categories", field_type=FieldType.SIMPLE_LIST,
                                  init_val=[])

    elements = BlockField(name="elements", field_type=FieldType.SIMPLE_LIST, init_val=[
        "box_plot.html"
    ])

    def __init__(self, *args, **kwargs):
        super(BoxPlot, self).__init__("Box plot", *args, **kwargs)
        self.boxplot_config = {
            "multi_index_axis_dict": {},
        }

    @log_timing
    def compute_boxplot_stats(self, exp, request=None, *args, **kwargs):
        axis_to_plot = [
            axis for axis, is_selected in
            self.boxplot_config['multi_index_axis_dict'].items() if is_selected
        ]
        rc = self.rc
        if axis_to_plot and rc:
            rc.load()

            df = rc.get_pandas_slice_for_boxplot(axis_to_plot, self.metric)

            categories = []
            for row_id, _ in df.iterrows():
                if type(row_id) == tuple:
                    title = ":".join(map(str, row_id))
                else:
                    title = str(row_id)

                categories.append(title)

            bps = boxplot_stats(np.array(df.T))

            if bps:
                self.chart_series = [{}]
                self.chart_series[0]["data"] = [
                    [
                        rec["whislo"],
                        rec["q1"],
                        rec["med"],
                        rec["q3"],
                        rec["whishi"]
                    ]
                    for rec in bps
                ]
                self.chart_categories = categories

                exp.store_block(self)

    def on_params_is_valid(self, exp, *args, **kwargs):
        super(BoxPlot, self).on_params_is_valid(exp, *args, **kwargs)
        if self.rc is not None:
            for axis in self.rc.axis_list:
                if axis not in self.boxplot_config["multi_index_axis_dict"]:
                    self.boxplot_config["multi_index_axis_dict"][axis] = ""

            self.compute_boxplot_stats(exp)
        exp.store_block(self)
