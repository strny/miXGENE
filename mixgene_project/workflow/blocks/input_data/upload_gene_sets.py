__author__ = 'pavel'

from environment.structures import GmtStorage, GeneSets
from workflow.blocks.blocks_pallet import GroupType
from workflow.blocks.fields import ActionsList, ActionRecord, ParamField, InputType, FieldType, OutputBlockField
from workflow.blocks.generic import GenericBlock
import logging


log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)



class UploadGeneSets(GenericBlock):
    block_base_name = "GENE_SETS_UPLOAD"
    block_group = GroupType.INPUT_DATA
    name = "Upload Gene Sets"

    _block_actions = ActionsList([
        ActionRecord("save_params", ["created", "valid_params", "done", "ready"], "validating_params",
                     user_title="Save parameters"),
        ActionRecord("on_params_is_valid", ["validating_params"], "done"),
        ActionRecord("on_params_not_valid", ["validating_params"], "created"),
        ])

    upload_gs = ParamField(
        "upload_gs", title="Gene sets in .gmt format", order_num=10,
        input_type=InputType.FILE_INPUT, field_type=FieldType.CUSTOM
    )

    _gene_sets = OutputBlockField(name="gene_sets", provided_data_type="GeneSets")

    def on_params_is_valid(self, exp, *args, **kwargs):
        try:
            gmt_file = self.upload_gs.get_file()
            gs = GmtStorage.read_inp(gmt_file, "\t")
            gene_sets = GeneSets(exp.get_data_folder(), str(self.uuid))
            gene_sets.store_gs(gs)
            self.set_out_var("gene_sets", gene_sets)
        except Exception as e:
            exp.log(self.uuid, e, severity="CRITICAL")
            log.error(e)

        exp.store_block(self)