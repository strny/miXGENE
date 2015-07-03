__author__ = 'pavel'

from abc import abstractmethod
import logging

from environment.structures import TableResult
from webapp.tasks import wrapper_task
from workflow.blocks.blocks_pallet import GroupType
from workflow.blocks.fields import FieldType, BlockField, OutputBlockField, InputBlockField, InputType, ParamField, \
    ActionRecord, ActionsList
from workflow.blocks.generic import GenericBlock, save_params_actions_list, execute_block_actions_list

from wrappers.sk_classifiers import apply_classifier

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class GenericClassifier(GenericBlock):
    block_group = GroupType.CLASSIFIER
    is_abstract = True

    is_block_supports_auto_execution = True
    classifier_name = ""
    # Block behavior
    _block_actions = ActionsList([])
    _block_actions.extend(save_params_actions_list)
    _block_actions.extend(execute_block_actions_list)

    # User defined parameters
    # Input ports definition
    _train_es = InputBlockField(name="train_es", order_num=10,
                                required_data_type="ExpressionSet",
                                required=True)
    _test_es = InputBlockField(name="test_es", order_num=20,
                               required_data_type="ExpressionSet",
                               required=True)

    # Provided outputs
    _result = OutputBlockField(name="result", field_type=FieldType.CUSTOM,
                               provided_data_type="ClassifierResult", init_val=None)

    def __init__(self, *args, **kwargs):
        super(GenericClassifier, self).__init__(*args, **kwargs)

        self.celery_task = None
        self.classifier_options = {}
        self.fit_options = {}

    @abstractmethod
    def collect_options(self):
        """
            Should populate `self.classifier_options` and `self.fit_options`
            from block parameters.
        """
        pass

    def get_option_safe(self, name, target_type=None):
        if hasattr(self, name):
            raw = getattr(self, name)
            if raw:
                if target_type:
                    try:
                        return target_type(raw)
                    except:
                        pass
                else:
                    return raw
        return None

    def collect_option_safe(self, name, target_type=None, target_name=None):
        value = self.get_option_safe(name, target_type)
        # from celery.contrib import rdb; rdb.set_trace()
        if value:
            if target_name:
                self.classifier_options[target_name] = value
            else:
                self.classifier_options[name] = value
        return value

    def execute(self, exp,  *args, **kwargs):
        self.set_out_var("result", None)
        self.collect_options()

        train_es = self.get_input_var("train_es")
        test_es = self.get_input_var("test_es")

        self.celery_task = wrapper_task.s(
            apply_classifier,
            exp=exp, block=self,

            train_es=train_es, test_es=test_es,

            classifier_name=self.classifier_name,
            classifier_options=self.classifier_options,
            fit_options=self.fit_options,

            base_folder=exp.get_data_folder(),
            base_filename="%s_%s" % (self.uuid, self.classifier_name),
        )
        exp.store_block(self)
        self.celery_task.apply_async()

    def success(self, exp, result, *args, **kwargs):
        # We store obtained result as an output variable
        self.set_out_var("result", result)
        exp.store_block(self)

    def reset_execution(self, exp, *args, **kwargs):
        self.clean_errors()
        # self.get_scope().remove_temp_vars()
        self.set_out_var("result", None)
        exp.store_block(self)
