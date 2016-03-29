# -*- coding: utf-8 -*-

import json
import logging

import pandas as pd

from workflow.blocks.fields import FieldType, BlockField, InnerOutputField, InputBlockField, ActionRecord, ActionsList
from workflow.blocks.meta.meta_block import UniformMetaBlock
from environment.structures import prepare_phenotype_for_js_from_es
from webapp.tasks import wrapper_task


log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

def prepare_folds(exp, block, features, es_dict, inner_output_es_names_map, success_action="success"):
    """
        @type features: list
        @param features: Phenotype features to use as target class

        @type es_dict: dict
        @param es_dict: {input_name -> ExpressionSet}

        @type inner_output_es_names_map: dict
        @param inner_output_es_names_map: input field name -> inner output name
    """
    seq = []
    pheno_df = es_dict.values()[0].get_pheno_data_frame()
    for num, feature in enumerate(features):
        mask = pd.notnull(pheno_df[feature])
        cell = {}
        for input_name, output_name in inner_output_es_names_map.iteritems():
            es = es_dict[input_name]
            modified_es = es.clone(
                base_filename="%s_%s_%s" % (block.uuid, input_name, num),

            )
            modified_pheno_df = pheno_df[mask]

            modified_es.pheno_metadata["user_class_title"] = feature
            modified_es.store_pheno_data_frame(modified_pheno_df)

            assay_df = es.get_assay_data_frame()
            # TODO remove this hack
            # assay_df = assay_df.T
            # Reorder columns to be compatible to phenotype
            assay_df = assay_df.loc[pheno_df.index, :]

            # modified_assay_df = assay_df.loc[assay_df.columns[mask]]
            modified_assay_df = assay_df.loc[assay_df.index[mask]]
            # modified_assay_df = modified_assay_df.T

            modified_es.store_assay_data_frame(modified_assay_df)

            cell[output_name] = modified_es
        seq.append(cell)

    return [seq],{}


class MultiFeature(UniformMetaBlock):
    block_base_name = "MULTI_FEATURE"
    name = "Multi Feature Validation"

    _mf_block_actions = ActionsList([
        ActionRecord("on_feature_selection_updated", ["valid_params", "ready", "done"], "ready"),
    ])

    _input_es_dyn = InputBlockField(
        name="es_inputs", order_num=-10,
        required_data_type="ExpressionSet",
        required=True, multiply_extensible=True
    )

    _is_sub_pages_visible = BlockField(
        "is_sub_pages_visible", FieldType.RAW,
        init_val=False, is_a_property=True
    )

    pages = BlockField("pages", FieldType.RAW, init_val={
        "select_feature": {
            "title": "Select features to examine",
            "resource": "select_feature",
            "widget": "widgets/select_feature.html"
        },
    })

    def __init__(self, *args, **kwargs):
        super(MultiFeature, self).__init__(*args, **kwargs)
        self.features = []

    @property
    def is_sub_pages_visible(self):
        if self.state in ['valid_params', 'done', 'ready']:
            return True
        return False

    def get_fold_labels(self):
        return self.features

    def add_dyn_input_hook(self, exp, dyn_port, new_port):
        """
            @type new_port: InputBlockField
        """
        new_inner_output = InnerOutputField(
            name="%s_i" % new_port.name,
            provided_data_type=new_port.required_data_type
        )
        self.inner_output_es_names_map[new_port.name] = new_inner_output.name
        self.register_inner_output_variables([new_inner_output])

    def execute(self, exp, *args, **kwargs):
        # self.celery_task = wrapper_task.s(
        #
        # )
        self.inner_output_manager.reset()
        es_dict = {
            inp_name: self.get_input_var(inp_name)
            for inp_name in self.es_inputs
        }
        self.celery_task = wrapper_task.s(
            prepare_folds,
            exp, self,
            features=self.features,
            es_dict=es_dict,
            inner_output_es_names_map=self.inner_output_es_names_map,
            success_action="on_folds_generation_success"
        )
        exp.store_block(self)
        self.celery_task.apply_async()

    def phenotype_for_js(self, exp, *args, **kwargs):
        es = None
        for input_name in self.es_inputs:
            es = self.get_input_var(input_name)
            if es is not None:
                break
        res = prepare_phenotype_for_js_from_es(es)
        res["features"] = self.features
        return res

    def update_feature_selection(self, exp, request, *args, **kwargs):
        req = json.loads(request.body)
        self.features = req["features"]
        if self.features:
            self.do_action("on_feature_selection_updated", exp)

    def on_feature_selection_updated(self, *args, **kwargs):
        pass
