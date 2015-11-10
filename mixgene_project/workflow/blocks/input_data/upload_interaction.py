import pandas as pd
from environment.structures import BinaryInteraction
from workflow.blocks.blocks_pallet import GroupType
from workflow.blocks.fields import ActionsList, ActionRecord, ParamField, InputType, FieldType, OutputBlockField
from workflow.blocks.generic import GenericBlock
from wrappers.input.utils import expand_geneset, expand_inters
from webapp.notification import AllUpdated, NotifyMode
from webapp.tasks import wrapper_task
from django.conf import settings


__author__ = 'pavel'

def upload_interaction_task(exp,
                             block
                             ):
    AllUpdated(
        exp.pk,
        comment=u"Processing Upload Interaction block",
        silent=False,
        mode=NotifyMode.INFO
    ).send()
    if settings.CELERY_DEBUG:
        import sys
        sys.path.append('/Migration/skola/phd/projects/miXGENE/mixgene_project/wrappers/pycharm-debug.egg')
        import pydevd
        pydevd.settrace('localhost', port=6901, stdoutToServer=True, stderrToServer=True)

    # Convert to  BinaryInteraction
    sep = getattr(block, "csv_sep", " ")
    if block.header:
        _header = 0
    else:
        _header = None
    interaction_df = block.upload_interaction.get_as_data_frame(sep=sep, header=_header)
    sd = None
    # if self.bi_data_type in ["pairs", "triples", "pairs_diff", "triples_diff"]:
    # we have to find a shape of interaction matrix
    features_1 = interaction_df[interaction_df.columns[0]].tolist()
    features_2 = interaction_df[interaction_df.columns[1]].tolist()
    interactions = []
    if block.bi_data_type in ["triples", "triples_diff"]:
        interactions = zip(features_1, features_2, interaction_df[interaction_df.columns[2]].tolist())
    else:
        interactions = zip(features_1, features_2, [1] * len(features_1))
    # new_inters = [expand_inters(inters_a, inters_b, value) for (inters_a, inters_b, value) in interactions]
    # new_inters = [item for sublist in new_inters for item in sublist] # flatten
    features_1 = [a for [a, _, _] in interactions]
    features_2 = [b for [_, b, _] in interactions]
    values = [c for [_, _, c] in interactions]
    interaction_df = pd.DataFrame()
    interaction_df[0] = features_1
    interaction_df[1] = features_2
    interaction_df[2] = values
    interaction = BinaryInteraction(exp.get_data_folder(), str(block.uuid))
    interaction.store_pairs(interaction_df, block.bi_data_type)
    # interaction.row_units = self.row_units
    # interaction.col_units = self.col_units
    interaction.header = block.header
    AllUpdated(
        exp.pk,
        comment=u"Processing of Upload Interaction block is done",
        silent=False,
        mode=NotifyMode.INFO
    ).send()
    return [interaction], {}


class UploadInteraction(GenericBlock):
    block_base_name = "GENE_INTERACTION"
    block_group = GroupType.INPUT_DATA
    name = "Upload Gene Interaction"

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

    upload_interaction = ParamField("upload_interaction", title="Interaction file", order_num=10,
        input_type=InputType.FILE_INPUT, field_type=FieldType.CUSTOM)


    interaction_type = ParamField("interaction_type", title="Interaction type", order_num=11,
        input_type=InputType.SELECT, field_type=FieldType.STR, required=True,
                                    init_val="PPI",
                                    options={
                                        "inline_select_provider": True,
                                        "select_options": [
                                            ["PPI", "PPI"],
                                            ["miRNA", "miRNA Target"]
                                        ]
                                    })

    x1_unit = ParamField("x1_unit", title="(x1, x2) - x1 unit",
                        order_num=12, input_type=InputType.SELECT, field_type=FieldType.STR, required=True,
                        init_val="RefSeq",
                        options={
                            "inline_select_provider": True,
                            "select_options": [
                                ["RefSeq", "RefSeq"],
                                ["Entrez", "EntrezID"],
                                ["Symbol", "Symbol"],
                                ["mirbase", "miRBase ID"]
                            ]
                        })

    x2_unit = ParamField("x2_unit", title="(x1, x2) - x2 unit",
                        order_num=13, input_type=InputType.SELECT, field_type=FieldType.STR, required=True,
                        init_val="RefSeq",
                        options={
                            "inline_select_provider": True,
                            "select_options": [
                                ["RefSeq", "RefSeq"],
                                ["Entrez", "EntrezID"],
                                ["Symbol", "Symbol"],
                                ["mirbase", "miRBase ID"]
                            ]
                        })


    header = ParamField("header", title="Header",
                           order_num=23, input_type=InputType.CHECKBOX, field_type=FieldType.BOOLEAN, required=False)

    bi_data_type = ParamField(
        "bi_data_type", title="Data type", order_num=40,
        input_type=InputType.SELECT, field_type=FieldType.STR,
        init_val="matrix",
        options={
            "inline_select_provider": True,
            "select_options": [
                # ["matrix", "Matrix"],
                ["pairs", "Pairs"],
                ["pairs_diff", "Pairs - different units in interaction"],
                ["triples", "Triples with values"],
                ["triples_diff", "Triples with values - different units in interaction"]
            ]
        }
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
    _interaction = OutputBlockField(name="interaction", provided_data_type="BinaryInteraction")

    def move_to_exp(self, exp_id):
        interaction = self.get_out_var("interaction")

    def __init__(self, *args, **kwargs):
        super(UploadInteraction, self).__init__(*args, **kwargs)
        self.celery_task = None

    def process_upload(self, exp, *args, **kwargs):
        self.clean_errors()
        self.celery_task = wrapper_task.s(
            upload_interaction_task,
            exp,
            self
        )
        exp.store_block(self)
        self.celery_task.apply_async()

    def success(self, exp, interaction):
        self.set_out_var("interaction", interaction)
        exp.store_block(self)
