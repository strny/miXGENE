# -*- coding: utf-8 -*-

import json
import sys
import traceback
from environment.structures import ExpressionSet, prepare_phenotype_for_js_from_es
from workflow.blocks.blocks_pallet import GroupType
from workflow.blocks.fields import ActionsList, ActionRecord, ParamField, InputType, FieldType, BlockField, \
    OutputBlockField
from workflow.blocks.generic import GenericBlock

__author__ = 'pavel'


class UserUploadComplex(GenericBlock):
    block_base_name = "UPLOAD_CMPLX"
    block_group = GroupType.INPUT_DATA
    name = "Upload mRna/miRna/methyl dataset"

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

    m_rna_matrix = ParamField("m_rna_matrix", title="mRNA expression", order_num=10,
                         input_type=InputType.FILE_INPUT, field_type=FieldType.CUSTOM)
    m_rna_platform = ParamField("m_rna_platform", title="Platform ID", order_num=11,
                               input_type=InputType.TEXT, field_type=FieldType.STR, required=False)
    m_rna_unit = ParamField("m_rna_unit", title="Working unit [used when platform is unknown]", init_val=None,
                           order_num=12, input_type=InputType.TEXT, field_type=FieldType.STR, required=False)

    m_rna_matrix_ori = ParamField(
        "m_rna_matrix_ori", title="Matrix orientation", order_num=13,
        input_type=InputType.SELECT, field_type=FieldType.STR,
        init_val="SxG",
        options={
            "inline_select_provider": True,
            "select_options": [
                ["SxG", "Samples x Genes"],
                ["GxS", "Genes x Samples"]
            ]
        }
    )


    mi_rna_matrix = ParamField("mi_rna_matrix", title=u"μRNA expression", order_num=20,
                          input_type=InputType.FILE_INPUT, field_type=FieldType.CUSTOM, required=False)

    mi_rna_matrix_ori = ParamField(
        "mi_rna_matrix_ori", title="Matrix orientation", order_num=21,
        input_type=InputType.SELECT, field_type=FieldType.STR,
        init_val="SxG",
        options={
            "inline_select_provider": True,
            "select_options": [
                ["SxG", "Samples x Genes"],
                ["GxS", "Genes x Samples"]
            ]
        }
    )
    methyl_matrix = ParamField("methyl_matrix", title="Methylation expression", order_num=30,
                          input_type=InputType.FILE_INPUT, field_type=FieldType.CUSTOM, required=False)

    methyl_matrix_ori = ParamField(
        "methyl_matrix_ori", title="Matrix orientation", order_num=31,
        input_type=InputType.SELECT, field_type=FieldType.STR,
        init_val="SxG",
        options={
            "inline_select_provider": True,
            "select_options": [
                ["SxG", "Samples x Genes"],
                ["GxS", "Genes x Samples"]
            ]
        }
    )

    pheno_matrix = ParamField("pheno_matrix", title="Phenotype matrix", order_num=40,
                              input_type=InputType.FILE_INPUT, field_type=FieldType.CUSTOM, required=False)

    csv_sep = ParamField(
        "csv_sep", title="CSV separator symbol", order_num=50,
        input_type=InputType.SELECT, field_type=FieldType.STR, init_val=",",
        options={
            "inline_select_provider": True,
            "select_options": [
                [" ", "space ( )"],
                [",", "comma  (,)"],
                ["\t", "tab (\\t)"],
                [";", "semicolon (;)"],
                [":", "colon (:)"],
            ]
        }
    )

    _is_sub_pages_visible = BlockField("is_sub_pages_visible", FieldType.RAW, is_a_property=True)

    _m_rna_es = OutputBlockField(name="m_rna_es", field_type=FieldType.HIDDEN,
        provided_data_type="ExpressionSet")
    _m_rna_annotation = OutputBlockField(name="m_rna_annotation", field_type=FieldType.HIDDEN,
        provided_data_type="PlatformAnnotation")
    _mi_rna_es = OutputBlockField(name="mi_rna_es", field_type=FieldType.HIDDEN,
                                provided_data_type="ExpressionSet")
    _methyl_es = OutputBlockField(name="methyl_es", field_type=FieldType.HIDDEN,
                                 provided_data_type="ExpressionSet")

    pages = BlockField("pages", FieldType.RAW, init_val={
        "assign_phenotype_classes": {
            "title": "Assign phenotype classes",
            "resource": "assign_phenotype_classes",
            "widget": "widgets/assign_phenotype_classes.html"
        },
    })

    @property
    def is_sub_pages_visible(self):
        if self.state in ['source_was_preprocessed', 'sample_classes_assigned', 'ready', 'done']:
            return True
        return False

    def process_upload(self, exp, *args, **kwargs):
        """
            @param exp: Experiment
        """
        # TODO: move to celery
        self.clean_errors()
        sep = getattr(self, "csv_sep", " ")

        try:
            if not self.pheno_matrix:
                self.warnings.append(Exception("Phenotype is undefined"))
                pheno_df = None
            else:
                pheno_df = self.pheno_matrix.get_as_data_frame(sep)
                pheno_df.set_index(pheno_df.columns[0])

                # TODO: solve somehow better: Here we add empty column with user class assignment
                pheno_df[ExpressionSet(None, None).pheno_metadata["user_class_title"]] = ""

            if self.m_rna_matrix is not None:
                m_rna_assay_df = self.m_rna_matrix.get_as_data_frame(sep)

                # if matrix is bad oriented, then do transposition
                if self.m_rna_matrix_ori == "GxS":
                    m_rna_assay_df = m_rna_assay_df.T

                m_rna_es = ExpressionSet(base_dir=exp.get_data_folder(),
                                        base_filename="%s_m_rna_es" % self.uuid)
                m_rna_es.store_assay_data_frame(m_rna_assay_df)
                if pheno_df:
                    m_rna_es.store_pheno_data_frame(pheno_df)
                m_rna_es.working_unit = self.m_rna_unit

                self.set_out_var("m_rna_es", m_rna_es)

                # TODO: fetch GPL annotation if GPL id was provided

            if self.mi_rna_matrix is not None:
                mi_rna_assay_df = self.mi_rna_matrix.get_as_data_frame(sep)

                # if matrix is bad oriented, then do transposition
                if self.mi_rna_matrix_ori == "GxS":
                    mi_rna_assay_df = mi_rna_assay_df.T

                mi_rna_es = ExpressionSet(base_dir=exp.get_data_folder(),
                                        base_filename="%s_mi_rna_es" % self.uuid)
                mi_rna_es.store_assay_data_frame(mi_rna_assay_df)

                if pheno_df:
                    mi_rna_es.store_pheno_data_frame(pheno_df)

                self.set_out_var("mi_rna_es", mi_rna_es)

            if self.methyl_matrix is not None:

                methyl_assay_df = self.methyl_matrix.get_as_data_frame(sep)

                # if matrix is bad oriented, then do transposition
                if self.mi_rna_matrix_ori == "GxS":
                    methyl_assay_df = methyl_assay_df.T

                methyl_es = ExpressionSet(base_dir=exp.get_data_folder(),
                                          base_filename="%s_methyl_es" % self.uuid)
                methyl_es.store_assay_data_frame(methyl_assay_df)
                if pheno_df:
                    methyl_es.store_pheno_data_frame(pheno_df)

                self.set_out_var("methyl_es", methyl_es)

            self.do_action("success", exp)
        except Exception as e:
            ex_type, ex, tb = sys.exc_info()
            traceback.print_tb(tb)
            self.do_action("error", exp, e)
        # self.celery_task_fetch.apply_async()

    def phenotype_for_js(self, exp, *args, **kwargs):
        m_rna_es = self.get_out_var("m_rna_es")
        mi_rna_es = self.get_out_var("mi_rna_es")
        methyl_es = self.get_out_var("methyl_es")
        es = None
        if m_rna_es is not None:
            es = m_rna_es
        elif mi_rna_es is not None:
            es = mi_rna_es
        elif methyl_es is not None:
            es = methyl_es

        if es is None:
            raise Exception("No data was stored before")

        return prepare_phenotype_for_js_from_es(es)

    def update_user_classes_assignment(self, exp, request, *args, **kwargs):
        m_rna_es = self.get_out_var("m_rna_es")
        mi_rna_es = self.get_out_var("mi_rna_es")
        methyl_es = self.get_out_var("methyl_es")
        es = None
        if m_rna_es is not None:
            es = m_rna_es
        elif mi_rna_es is not None:
            es = mi_rna_es
        elif methyl_es is not None:
            es = methyl_es

        if es is None:
            raise Exception("No data was stored before")

        pheno_df = es.get_pheno_data_frame()

        received = json.loads(request.body)

        pheno_df[received["user_class_title"]] = received["classes"]

        for work_es in [m_rna_es, mi_rna_es, methyl_es]:
            if work_es is not None:
                work_es.pheno_metadata["user_class_title"] = received["user_class_title"]
                work_es.store_pheno_data_frame(pheno_df)

        # import ipdb; ipdb.set_trace()
        exp.store_block(self)

    def success(self, exp, *args, **kwargs):
        pass