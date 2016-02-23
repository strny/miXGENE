# -*- coding: utf-8 -*-

import json
import logging

# from environment.structures import ExpressionSet
from workflow.blocks.fields import MultiUploadField, FieldType, BlockField, InnerOutputField, \
    InputType, ParamField, ActionRecord, ActionsList
from workflow.blocks.meta.meta_block import UniformMetaBlock
from webapp.tasks import wrapper_task
from workflow.blocks.input_data.user_upload_complex import process_data_frame
from webapp.notification import AllUpdated, NotifyMode

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

# def process_df(exp, block, es_name, pheno_name):


def bunch_upload_task(exp, block):
    seq = []
    for pheno_name, (es_mRNA_name, es_miRNA_name) in block.pheno_by_es_names.iteritems():
        es_mRNA_ufw = block.es_mRNA_matrices[es_mRNA_name]
        es_mRNA_df = es_mRNA_ufw.get_as_data_frame(block.csv_sep_m_rna)
        es_miRNA_ufw = block.es_miRNA_matrices[es_miRNA_name]
        es_miRNA_df = es_miRNA_ufw.get_as_data_frame(block.csv_sep_mi_rna)

        pheno_ufw = block.pheno_matrices[pheno_name]
        pheno_df = pheno_ufw.get_as_data_frame(block.csv_sep)

        es_mRNA, es_mRNA_df, gpl_file = process_data_frame(exp, block, es_mRNA_df, block.es_mRNA_matrices_ori, block.m_rna_platform, block.m_rna_unit, "m_rna")
        es_miRNA, es_miRNA_df, gpl_file = process_data_frame(exp, block, es_miRNA_df, block.es_miRNA_matrices_ori, block.mi_rna_platform, block.mi_rna_unit, "mi_rna")

        pheno_df.set_index(pheno_df.columns[0], inplace=True)
        es_mRNA_sample_names = sorted(es_mRNA_df.index.tolist())
        es_miRNA_sample_names = sorted(es_miRNA_df.index.tolist())

        pheno_sample_names = sorted(pheno_df.index.tolist())
        if es_mRNA_sample_names != pheno_sample_names:
            msg = "Couldn't match `%s` and `%s` due to different sample name sets" % (es_mRNA_name, pheno_name)
            AllUpdated(
                exp.pk,
                comment=msg,
                silent=False,
                mode=NotifyMode.ERROR
            ).send()
            raise RuntimeError(msg)
        if es_miRNA_sample_names != pheno_sample_names:
            msg = "Couldn't match `%s` and `%s` due to different sample name sets" % (es_miRNA_name, pheno_name)
            AllUpdated(
                exp.pk,
                comment=msg,
                silent=False,
                mode=NotifyMode.ERROR
            ).send()
            raise RuntimeError(msg)

        es_mRNA.store_pheno_data_frame(pheno_df)
        es_miRNA.store_pheno_data_frame(pheno_df)

        es_mRNA.pheno_metadata["user_class_title"] = pheno_df.columns[0]
        es_miRNA.pheno_metadata["user_class_title"] = pheno_df.columns[0]

        seq.append({"mRNA_es": es_mRNA, "miRNA_es": es_miRNA, "__label__": es_mRNA_name})
    block.seq = seq
    return [block], {}


class MassUpload(UniformMetaBlock):
    block_base_name = "BunchUpload"
    name = "Mass Upload Expression Sets"

    _bu_block_actions = ActionsList([

        ActionRecord("process_upload", ["valid_params", "processing_upload"],
                     "processing_upload", "Process uploaded data"),

        ActionRecord("error_on_processing", ["processing_upload"], "valid_params"),
        ActionRecord("processing_done", ["processing_upload"], "ready")

        # ActionRecord("success", ["processing_upload"], "done", reload_block_in_client=True),
        # ActionRecord("error", ["processing_upload"], "valid_params"),
    ])

    es_mRNA_matrices = ParamField(
        "es_mRNA_matrices", title="mRNA Expression sets", order_num=10,
        input_type=InputType.FILE_INPUT, field_type=FieldType.CUSTOM,
        options={"multiple": True},
    )

    es_mRNA_matrices_ori = ParamField(
        "es_mRNA_matrices_ori", title="Matrices orientation", order_num=11,
        input_type=InputType.SELECT, field_type=FieldType.STR,
        init_val="SxG",
        options={
            "inline_select_provider": True,
            "select_options": [
                ["SxG", "Samples x Features"],
                ["GxS", "Features x Samples"]
            ]
        }
    )

    m_rna_platform = ParamField("m_rna_platform", title="Platform ID", order_num=12,
                                input_type=InputType.TEXT, field_type=FieldType.STR, required=False)

    m_rna_unit = ParamField("m_rna_unit", title="Working unit [used when platform is unknown]",
                            order_num=13, input_type=InputType.SELECT, field_type=FieldType.STR, required=False,
                            init_val="RefSeq",
                            options={
                                "inline_select_provider": True,
                                "select_options": [
                                    ["RefSeq", "RefSeq"],
                                    ["Entrez", "EntrezID"],
                                    ["Symbol", "Symbol"]
                                ]
                            })

    csv_sep_m_rna = ParamField(
        "csv_sep_m_rna", title="CSV separator symbol", order_num=14,
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

    es_miRNA_matrices = ParamField(
        "es_miRNA_matrices", title="miRNA Expression sets", order_num=15,
        input_type=InputType.FILE_INPUT, field_type=FieldType.CUSTOM,
        options={"multiple": True},
    )

    mi_rna_platform = ParamField("mi_rna_platform", title="Platform ID", order_num=21,
                                 input_type=InputType.TEXT, field_type=FieldType.STR, required=False)
    mi_rna_unit = ParamField("mi_rna_unit", title="Working unit [used when platform is unknown]",
                             order_num=22, input_type=InputType.SELECT, field_type=FieldType.STR, required=False,
                             init_val="RefSeq",
                             options={
                                 "inline_select_provider": True,
                                 "select_options": [
                                     ["RefSeq", "RefSeq"],
                                     ["mirbase", "miRBase ID"]
                                 ]
                             })

    es_miRNA_matrices_ori = ParamField(
        "es_miRNA_matrices_ori", title="Matrices orientation", order_num=23,
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
    csv_sep_mi_rna = ParamField(
        "csv_sep_mi_rna", title="CSV separator symbol", order_num=24,
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

    pheno_matrices = ParamField(
        "pheno_matrices", title="Phenotypes", order_num=40,
        input_type=InputType.FILE_INPUT, field_type=FieldType.CUSTOM,
        options={"multiple": True},
    )

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

    # cells = BlockField(name="cells", field_type=FieldType.CUSTOM, init_val=None)

    # elements = BlockField(name="elements", field_type=FieldType.SIMPLE_LIST, init_val=[
    #     "mass_upload/data_spec.html"
    # ])

    def __init__(self, *args, **kwargs):
        super(MassUpload, self).__init__(*args, **kwargs)
        self.es_mRNA_matrices = MultiUploadField()
        self.es_miRNA_matrices = MultiUploadField()

        self.pheno_matrices = MultiUploadField()

        self.pheno_by_es_names = {}

        self.labels = []
        self.seq = []
        self.register_inner_output_variables([InnerOutputField(
            name="mRNA_es",
            provided_data_type="ExpressionSet"
        ), InnerOutputField(
            name="miRNA_es",
            provided_data_type="ExpressionSet"
        )])

    @property
    def is_sub_pages_visible(self):
        if self.state in ['source_was_preprocessed', 'sample_classes_assigned', 'ready', 'done']:
            return True
        return False

    def get_fold_labels(self):
        return self.labels

    def error_on_processing(self, *args, **kwargs):
        pass

    def processing_done(self, exp, block):
        exp.store_block(block)

    def process_upload(self, exp, *args, **kwargs):
        """
            @param exp: Experiment
        """
        self.clean_errors()
        try:
            if len(self.pheno_matrices) != len(self.es_mRNA_matrices):
                raise RuntimeError("Different number of phenotypes and mRNA expression sets")
            if self.es_miRNA_matrices:
                if len(self.pheno_matrices) != len(self.es_miRNA_matrices):
                    raise RuntimeError("Different number of phenotypes and miRNA expression sets")
            self.labels = es_mRNA_matrix_names = sorted(self.es_mRNA_matrices)
            es_miRNA_matrix_names = sorted(self.es_miRNA_matrices)
            pheno_matrix_names = sorted(self.pheno_matrices)
            if len(es_miRNA_matrix_names) == 0:
                es_miRNA_matrix_names = len(es_mRNA_matrix_names) * [None]
            self.pheno_by_es_names = {
                pheno_name: es_name for
                es_name, pheno_name
                in zip(zip(es_mRNA_matrix_names, es_miRNA_matrix_names), pheno_matrix_names)
            }

            self.clean_errors()
            self.celery_task = wrapper_task.s(
                bunch_upload_task,
                exp,
                self,
                success_action="processing_done",
                error_action="error_on_processing"
            )
            exp.store_block(self)
            self.celery_task.apply_async()
        except Exception as e:
            exp.log(self.uuid, e, severity="CRITICAL")
            log.exception(e)
            self.errors.append(e)
            self.do_action("error_on_processing", exp, e)
            # self.celery_task_fetch.apply_async()

    def execute(self, exp, *args, **kwargs):
        self.inner_output_manager.reset()
        self.do_action("on_folds_generation_success", exp, self.seq)

    def get_repeat_labels(self):
        pass
