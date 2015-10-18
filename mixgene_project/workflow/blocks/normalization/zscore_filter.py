from webapp.tasks import wrapper_task
from workflow.blocks.blocks_pallet import GroupType
from workflow.blocks.fields import ActionsList, ActionRecord, InputBlockField, OutputBlockField
from workflow.blocks.generic import GenericBlock, execute_block_actions_list
from wrappers.filter import zscore_task

__author__ = 'pavel'


class ZScoreBlock(GenericBlock):
    block_base_name = "ZSCORE_NORM"
    name = "Z-score Normalization"

    is_abstract = False
    block_group = GroupType.NORMALIZATION

    is_block_supports_auto_execution = True

    _block_actions = ActionsList([
        ActionRecord("save_params", ["created", "valid_params", "done", "ready"], "validating_params",
                     user_title="Save parameters"),
        ActionRecord("on_params_is_valid", ["validating_params"], "ready"),
        ActionRecord("on_params_not_valid", ["validating_params"], "created"),
        ])
    _block_actions.extend(execute_block_actions_list)


    _es = InputBlockField(name="es", order_num=10, required_data_type="ExpressionSet", required=True)

    flt_es = OutputBlockField(name="flt_zscore_es", provided_data_type="ExpressionSet")

    def __init__(self, *args, **kwargs):
        super(ZScoreBlock, self).__init__(*args, **kwargs)
        self.celery_task = None

    def execute(self, exp, *args, **kwargs):
        self.clean_errors()
        es = self.get_input_var("es")

        self.celery_task = wrapper_task.s(
            zscore_task,
            exp, self,
            es=es,
            base_filename="%s_%s_flt" % (self.uuid, 'zscore')
        )
        exp.store_block(self)
        self.celery_task.apply_async()

    def success(self, exp, flt_es):
        self.set_out_var("flt_zscore_es", flt_es)
        exp.store_block(self)