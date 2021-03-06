from webapp.tasks import wrapper_task
from workflow.blocks.blocks_pallet import GroupType
from workflow.blocks.fields import ActionsList, ActionRecord, InputBlockField, ParamField, InputType, FieldType, \
    OutputBlockField
from workflow.blocks.generic import GenericBlock, execute_block_actions_list
from wrappers.filter import filter_task

__author__ = 'pavel'


class FilterBlock(GenericBlock):
    block_base_name = "FILTER"
    name = "Var/Val Filter"

    is_abstract = False
    block_group = GroupType.FILTER

    is_block_supports_auto_execution = True

    _block_actions = ActionsList([
        ActionRecord("save_params", ["created", "valid_params", "done", "ready"], "validating_params",
                     user_title="Save parameters"),
        ActionRecord("on_params_is_valid", ["validating_params"], "ready"),
        ActionRecord("on_params_not_valid", ["validating_params"], "created"),
        ])
    _block_actions.extend(execute_block_actions_list)


    _es = InputBlockField(name="es", order_num=10, required_data_type="ExpressionSet", required=True)

    filter_method = ParamField(
        "filter_method", title="Filter method", order_num=50,
        input_type=InputType.SELECT, field_type=FieldType.STR,
        init_val="LOW_VAL",
        options={
            "inline_select_provider": True,
            "select_options": [
                ["LOW_VAL", "Low Val Filter"],
                ["VAR", "Var Filter"]
            ]
        }
    )
    q = ParamField(name="q", title="Threshold", input_type=InputType.TEXT, field_type=FieldType.FLOAT, init_val=30.0)

    flt_es = OutputBlockField(name="flt_es", provided_data_type="ExpressionSet")

    def __init__(self, *args, **kwargs):
        super(FilterBlock, self).__init__(*args, **kwargs)
        self.celery_task = None

    def execute(self, exp, *args, **kwargs):
        self.clean_errors()
        es = self.get_input_var("es")

        self.celery_task = wrapper_task.s(
            filter_task,
            exp, self,
            filter_type=self.filter_method,
            q=self.q,
            es=es,
            base_filename="%s_%s_flt" % (self.uuid, self.filter_method)
        )
        exp.store_block(self)
        self.celery_task.apply_async()

    def success(self, exp, flt_es):
        self.set_out_var("flt_es", flt_es)
        exp.store_block(self)