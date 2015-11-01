# -*- coding: utf-8 -*-

import json
import sys
import traceback
from environment.structures import ExpressionSet, prepare_phenotype_for_js_from_es
from workflow.blocks.blocks_pallet import GroupType
from workflow.blocks.fields import ActionsList, ActionRecord, ParamField, InputType, FieldType, BlockField, \
    OutputBlockField
from workflow.blocks.generic import GenericBlock
from workflow.common_tasks import fetch_geo_gpl
from webapp.notification import AllUpdated, NotifyMode
from webapp.tasks import wrapper_task
from wrappers.input.utils import find_target_column, find_refseq
import pandas
import re
from django.conf import settings

__author__ = 'pavel'


def convert_to_refseq(assay_df, unit, data_type):
    # features of dataset
    columns_source = set(list(assay_df))
    new_names = {}
    count = 0
    for gene in columns_source:
        new_name = find_refseq(gene)
        if new_name:
            new_names[gene] = new_name
            count += 1
        else:
            new_names[gene] = gene
    assay_df.rename(columns=new_names, inplace=True)
    return assay_df, count


def convert_ids(gpl_file, assay_df, data_type):
    import StringIO
    output = StringIO.StringIO()
    with open(gpl_file.filepath, "r") as f_in:
        parse = False
        for line in f_in:
            if line.startswith("#"):
                parse = True
            if line.startswith("<br>"):
                parse = False
            if (not line.startswith("#")) and parse:
                output.write(line)
    output.seek(0)
    gpl_data = pandas.read_csv(output, delimiter="\t")
    # gpl header
    columns_target = list(gpl_data)
    # features of dataset
    columns_source = set(list(assay_df))

    freqs = {c_t: len(set(map(lambda x: str(x).lower(), gpl_data[c_t].values)).intersection(
        map(lambda x: str(x).lower(), columns_source)))
            for c_t in columns_target}
    #find max key
    max_key = max(freqs.keys(), key=(lambda key: freqs[key]))
    regex = "^[A-Z][A-Z]_[a-zA-Z0-9.]*"
    if data_type == "mi_rna":
        regex = "^(.*-mir)|(.*-.*-.*)"
    target_column = find_target_column(regex, gpl_data)
    new_names = {old_name: new_name
                 for old_name, new_name in gpl_data[[max_key, target_column]].values}
    assay_df.rename(columns=new_names, inplace=True)
    return assay_df, freqs[max_key]


def process_data_frame(exp, block, df, ori, platform, unit, data_type="m_rna"):
    if settings.CELERY_DEBUG:
        import sys
        sys.path.append('/Migration/skola/phd/projects/miXGENE/mixgene_project/wrappers/pycharm-debug.egg')
        import pydevd
        pydevd.settrace('localhost', port=6901, stdoutToServer=True, stderrToServer=True)

    df.set_index(df.columns[0], inplace=True)

    # if matrix is bad oriented, then do transposition
    if ori == "GxS":
        df = df.T
        # df.columns = df.iloc[0]
        # df = df.drop(df.index[0])
    # if isinstance(df.columns[0][0], basestring):

    gpl_file = None
    if platform:
        AllUpdated(
            exp.pk,
            comment=u"Fetching platform %s" % platform,
            silent=False,
            mode=NotifyMode.INFO
        ).send()
        gpl_file = fetch_geo_gpl(exp, block, platform)
        df, matched = convert_ids(gpl_file, df, data_type)
        AllUpdated(
            exp.pk,
            comment=u"Matched %s features for %s dataset" % (matched, data_type),
            silent=False,
            mode=NotifyMode.INFO
        ).send()
    else:
        if unit != "RefSeq":
            AllUpdated(
                exp.pk,
                comment=u"Converting unit %s to RefSeq" % platform,
                silent=False,
                mode=NotifyMode.INFO
            ).send()
            df, matched = convert_to_refseq(df, unit, data_type)
            AllUpdated(
                exp.pk,
                comment=u"Matched %s features for %s dataset" % (matched, data_type),
                silent=False,
                mode=NotifyMode.INFO
            ).send()

    es = ExpressionSet(base_dir=exp.get_data_folder(),
                       base_filename="%s_%s_es" % (block.uuid, data_type))
    es.store_assay_data_frame(df)
    return es, df, gpl_file


def user_upload_complex_task(exp,
                             block
                             ):
    sep_m_rna = getattr(block, "csv_sep_m_rna", " ")
    sep_mi_rna = getattr(block, "csv_sep_mi_rna", " ")
    sep_methyl = getattr(block, "csv_sep_methyl", " ")
    sep_pheno = getattr(block, "csv_sep_pheno", " ")

    AllUpdated(
        exp.pk,
        comment=u"Processing UserUploadComplex block",
        silent=False,
        mode=NotifyMode.INFO
    ).send()

    if not block.pheno_matrix:
        block.warnings.append(Exception("Phenotype is undefined"))
        AllUpdated(
            exp.pk,
            comment=u"Phenotype is undefined",
            silent=False,
            mode=NotifyMode.INFO
        ).send()

        pheno_df = None
    else:
        pheno_df = block.pheno_matrix.get_as_data_frame(sep_pheno)
        pheno_df.set_index(pheno_df.columns[0])

        # TODO: solve somehow better: Here we add empty column with user class assignment
        pheno_df[ExpressionSet(None, None).pheno_metadata["user_class_title"]] = ""

    m_rna_es = None
    mi_rna_es = None
    methyl_es = None
    if block.m_rna_matrix is not None:
        m_rna_assay_df = block.m_rna_matrix.get_as_data_frame(sep_m_rna)
        m_rna_es, mi_rna_assay_df, gpl_file = process_data_frame(exp, block, m_rna_assay_df, block.m_rna_matrix_ori,
                                                                 block.m_rna_platform, block.m_rna_unit, "m_rna")
        block.m_rna_gpl_file = gpl_file

        if pheno_df is not None:
            m_rna_es.store_pheno_data_frame(pheno_df)
        m_rna_es.working_unit = block.m_rna_unit

    if block.mi_rna_matrix is not None:
        mi_rna_assay_df = block.mi_rna_matrix.get_as_data_frame(sep_mi_rna)
        mi_rna_es, mi_rna_assay_df, gpl_file = process_data_frame(exp, block, mi_rna_assay_df, block.mi_rna_matrix_ori,
                                                                  block.mi_rna_platform, block.mi_rna_unit, "mi_rna")
        block.mi_rna_gpl_file = gpl_file

        if pheno_df is not None:
            mi_rna_es.store_pheno_data_frame(pheno_df)
        mi_rna_es.working_unit = block.mi_rna_unit

    if block.methyl_matrix is not None:
        methyl_assay_df = block.methyl_matrix.get_as_data_frame(sep_methyl)
        methyl_es, methyl_assay_df, gpl_file = process_data_frame(exp, block, methyl_assay_df, block.methyl_matrix_ori,
                                                                  block.methyl_platform, "methyl")
        block.methyl_gpl_file = gpl_file

        if pheno_df is not None:
            methyl_es.store_pheno_data_frame(pheno_df)
        methyl_es.working_unit = block.methyl_unit

    AllUpdated(
        exp.pk,
        comment=u"Finished processing of UserUploadComplex",
        silent=False,
        mode=NotifyMode.INFO
    ).send()

    return [m_rna_es, mi_rna_es, methyl_es
            ], {}

class UserUploadComplex(GenericBlock):
    # unit_options =
    block_base_name = "UPLOAD_CMPLX"
    block_group = GroupType.INPUT_DATA
    name = "Upload mRna/miRna/methyl"

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

    m_rna_unit = ParamField("m_rna_unit", title="Working unit [used when platform is unknown]",
                            order_num=12, input_type=InputType.SELECT, field_type=FieldType.STR, required=False,
                            init_val="RefSeq",
                            options={
                                "inline_select_provider": True,
                                "select_options": [
                                    ["RefSeq", "RefSeq"],
                                    ["Entrez", "EntrezID"],
                                    ["Symbol", "Symbol"]
                                ]
                            })

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

    mi_rna_matrix = ParamField("mi_rna_matrix", title=u"μRNA expression", order_num=20,
                          input_type=InputType.FILE_INPUT, field_type=FieldType.CUSTOM, required=False)

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


    mi_rna_matrix_ori = ParamField(
        "mi_rna_matrix_ori", title="Matrix orientation", order_num=23,
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

    methyl_matrix = ParamField("methyl_matrix", title="Methylation expression", order_num=30,
                          input_type=InputType.FILE_INPUT, field_type=FieldType.CUSTOM, required=False)

    methyl_platform = ParamField("methyl_platform", title="Platform ID", order_num=31,
                               input_type=InputType.TEXT, field_type=FieldType.STR, required=False)
    # methyl_unit = ParamField("methyl_unit", title="Working unit [used when platform is unknown]", init_val=None,
    #                        order_num=32, input_type=InputType.TEXT, field_type=FieldType.STR, required=False)

    methyl_matrix_ori = ParamField(
        "methyl_matrix_ori", title="Matrix orientation", order_num=33,
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

    csv_sep_methyl = ParamField(
        "csv_sep_methyl", title="CSV separator symbol", order_num=34,
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

    pheno_matrix = ParamField("pheno_matrix", title="Phenotype matrix", order_num=40,
                              input_type=InputType.FILE_INPUT, field_type=FieldType.CUSTOM, required=False)

    csv_sep_pheno = ParamField(
        "csv_sep_pheno", title="CSV separator symbol", order_num=50,
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
    # _m_rna_annotation = OutputBlockField(name="m_rna_annotation", field_type=FieldType.HIDDEN,
    #     provided_data_type="PlatformAnnotation")
    _mi_rna_es = OutputBlockField(name="mi_rna_es", field_type=FieldType.HIDDEN,
                                provided_data_type="ExpressionSet")
    _methyl_es = OutputBlockField(name="methyl_es", field_type=FieldType.HIDDEN,
                                 provided_data_type="ExpressionSet")

    mrna_gpl_file = BlockField("mrna_gpl_file", FieldType.CUSTOM, None)
    mirna_gpl_file = BlockField("mirna_gpl_file", FieldType.CUSTOM, None)
    methyl_gpl_file = BlockField("methyl_gpl_file", FieldType.CUSTOM, None)

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

    def __init__(self, *args, **kwargs):
        super(UserUploadComplex, self).__init__(*args, **kwargs)
        self.celery_task = None

    def process_upload(self, exp, *args, **kwargs):
        self.clean_errors()
        self.celery_task = wrapper_task.s(
            user_upload_complex_task,
            exp,
            self
        )
        exp.store_block(self)
        self.celery_task.apply_async()

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

    def success(self, exp, m_rna_es, mi_rna_es, methyl_es):
        if m_rna_es:
            self.set_out_var("m_rna_es", m_rna_es)
        if mi_rna_es:
            self.set_out_var("mi_rna_es", mi_rna_es)
        if methyl_es:
            self.set_out_var("methyl_es", methyl_es)
        exp.store_block(self)