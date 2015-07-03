import json
import pandas as pd
from environment.structures import prepare_phenotype_for_js_from_es, ExpressionSet
from workflow.blocks.blocks_pallet import GroupType
from workflow.blocks.fields import ActionsList, ActionRecord, ParamField, InputType, FieldType, BlockField, \
    OutputBlockField
from workflow.blocks.generic import GenericBlock

__author__ = 'pavel'


class UserUpload(GenericBlock):
    block_base_name = "UPLOAD"
    block_group = GroupType.INPUT_DATA
    is_abstract = True

    _block_actions = ActionsList([
        ActionRecord("save_params", ["created", "valid_params", "done", "ready"], "validating_params",
                     user_title="Save parameters"),
        ActionRecord("on_params_is_valid", ["validating_params"], "valid_params"),
        ActionRecord("on_params_not_valid", ["validating_params"], "created"),

        ActionRecord("process_upload", ["valid_params", "processing_upload"],
                     "processing_upload", "Process uploaded data", reload_block_in_client=True),
        ActionRecord("success", ["processing_upload"], "done", reload_block_in_client=True),
        ActionRecord("error", ["processing_upload"], "valid_params", reload_block_in_client=True),
    ])

    es_matrix = ParamField("es_matrix", title="Expression set matrix", order_num=0,
        input_type=InputType.FILE_INPUT, field_type=FieldType.CUSTOM)
    es_matrix_ori = ParamField(
        "es_matrix_ori", title="Matrix orientation", order_num=1,
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
    pheno_matrix = ParamField("pheno_matrix", title="Phenotype matrix", order_num=10,
        input_type=InputType.FILE_INPUT, field_type=FieldType.CUSTOM)
    gpl_platform = ParamField("gpl_platform", title="Platform ID", order_num=20,
        input_type=InputType.TEXT, field_type=FieldType.STR, required=False)
    working_unit = ParamField("working_unit", title="Working unit [used when platform is unknown]",
        order_num=3, input_type=InputType.TEXT, field_type=FieldType.STR, required=False)
    # TODO: add sub page field
    # pages = BlockField("pages", FieldType.RAW, init_val={
    #     "assign_sample_classes": {
    #         "title": "Assign sample classes",
    #         "resource": "assign_sample_classes",
    #         "widget": "widgets/fetch_gse/assign_sample_classes.html"
    #     },
    # })
    _is_sub_pages_visible = BlockField("is_sub_pages_visible", FieldType.RAW, is_a_property=True)

    ### PARAMETERS
    _expression_set = OutputBlockField(name="expression_set", field_type=FieldType.HIDDEN,
                                       provided_data_type="ExpressionSet")
    _gpl_annotation = OutputBlockField(name="gpl_annotation", field_type=FieldType.HIDDEN,
                                       provided_data_type="PlatformAnnotation")

    # TODO: COPY PASTE from fetch_gse block
    pages = BlockField("pages", FieldType.RAW, init_val={
        "assign_phenotype_classes": {
            "title": "Assign phenotype classes",
            "resource": "assign_phenotype_classes",
            "widget": "widgets/assign_phenotype_classes.html"
        },
    })

    def __init__(self, *args, **kwargs):
        super(UserUpload, self).__init__("User upload", *args, **kwargs)


    @property
    def is_sub_pages_visible(self):
        if self.state in ['source_was_preprocessed', 'sample_classes_assigned', 'ready', 'done']:
            return True
        return False

    def phenotype_for_js(self, exp, *args, **kwargs):
        return prepare_phenotype_for_js_from_es(self.get_out_var("expression_set"))

    def update_user_classes_assignment(self, exp, request, *args, **kwargs):
        es = self.get_out_var("expression_set")
        pheno_df = es.get_pheno_data_frame()

        received = json.loads(request.body)
        es.pheno_metadata["user_class_title"] = received["user_class_title"]
        pheno_df[received["user_class_title"]] = received["classes"]

        es.store_pheno_data_frame(pheno_df)
        exp.store_block(self)

    def process_upload(self, exp, *args, **kwargs):
        """
            @param exp: Experiment
        """
        self.clean_errors()

        assay_df = pd.DataFrame.from_csv(self.es_matrix.get_file())

        es = ExpressionSet(base_dir=exp.get_data_folder(),
                           base_filename="%s_annotation" % self.uuid)

        pheno_df = pd.DataFrame.from_csv(self.pheno_matrix.get_file())
        pheno_df.set_index(pheno_df.columns[0])

        user_class_title = es.pheno_metadata["user_class_title"]
        if user_class_title not in pheno_df.columns:
            pheno_df[es.pheno_metadata["user_class_title"]] = ""

        # if matrix is bad oriented, then do transposition
        if self.es_matrix_ori == "GxS":
            assay_df = assay_df.T

        es.store_assay_data_frame(assay_df)
        es.store_pheno_data_frame(pheno_df)

        if self.working_unit:
            es.working_unit = self.working_unit

        self.set_out_var("expression_set", es)

        exp.store_block(self)

        self.do_action("success", exp)
        # self.celery_task_fetch.apply_async()

    def success(self, exp, *args, **kwargs):
        pass