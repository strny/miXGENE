__author__ = 'pavel'


from webapp.tasks import wrapper_task
from workflow.blocks.blocks_pallet import GroupType
from workflow.blocks.fields import ActionsList, ActionRecord, InputBlockField, ParamField, InputType, FieldType, \
    OutputBlockField
from workflow.blocks.generic import GenericBlock, execute_block_actions_list
from wrappers.aggregation.aggregation import pca_agg_task_cv


class PCAAgg(GenericBlock):

    block_group = GroupType.PROCESSING
    block_base_name = "PCA_AGG_CV"
    name = "PCA aggregation for CV"
    is_block_supports_auto_execution = True

    _block_actions = ActionsList([
        ActionRecord("save_params", ["created", "valid_params", "done", "ready"], "validating_params",
                     user_title="Save parameters"),
        ActionRecord("on_params_is_valid", ["validating_params"], "ready"),
        ActionRecord("on_params_not_valid", ["validating_params"], "created"),
        ])
    _block_actions.extend(execute_block_actions_list)

    _input_train_es = InputBlockField(name="train_es", order_num=10,
                                      required_data_type="ExpressionSet", required=True)
    _input_test_es = InputBlockField(name="test_es", order_num=20,
                                     required_data_type="ExpressionSet", required=True)

    _input_gs = InputBlockField(name="gs", order_num=30,
                                required_data_type="GeneSets", required=True)

    out_train_es = OutputBlockField(name="out_train_es", provided_data_type="ExpressionSet")
    out_test_es = OutputBlockField(name="out_test_es", provided_data_type="ExpressionSet")


    def __init__(self, *args, **kwargs):
        super(PCAAgg, self).__init__(*args, **kwargs)
        self.celery_task = None

    def execute(self, exp, *args, **kwargs):
        self.clean_errors()
        train_es = self.get_input_var("train_es")
        test_es = self.get_input_var("test_es")

        gene_sets = self.get_input_var("gs")

        self.celery_task = wrapper_task.s(
            pca_agg_task_cv,
            exp, self,
            train_es=train_es,
            test_es=test_es,
            gene_sets=gene_sets,
            base_filename="%s_%s_agg" % (self.uuid, "pca_cv")
        )
        exp.store_block(self)
        self.celery_task.apply_async()

    def success(self, exp, out_train_es, out_test_es):
        self.set_out_var("out_train_es", out_train_es)
        self.set_out_var("out_test_es", out_train_es)
        exp.store_block(self)
