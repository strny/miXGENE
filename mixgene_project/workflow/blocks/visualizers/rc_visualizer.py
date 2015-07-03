__author__ = 'pavel'


from mixgene.util import log_timing
from workflow.blocks.blocks_pallet import GroupType
from workflow.blocks.fields import ActionsList, ActionRecord, InputBlockField, FieldType, BlockField, ParamField, \
    InputType
from workflow.blocks.generic import GenericBlock
from wrappers.scoring import metrics_dict
import logging

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class RcVisualizer(GenericBlock):
    block_base_name = "RC_VIZUALIZER"
    is_block_supports_auto_execution = False
    block_group = GroupType.VISUALIZE
    is_abstract = True


    _block_actions = ActionsList([
        ActionRecord("save_params", ["created", "valid_params", "done", "ready", "input_bound"], "validating_params",
                     user_title="Save parameters"),
        ActionRecord("on_params_is_valid", ["validating_params"], "input_bound"),
        ActionRecord("on_params_not_valid", ["validating_params"], "created"),

        ActionRecord("configure_table", ["input_bound", "ready"], "ready"),
    ])

    results_container = InputBlockField(name="results_container",
                                        required_data_type="ResultsContainer",
                                        required=True,
                                        field_type=FieldType.CUSTOM)
    _rc = BlockField(name="rc", field_type=FieldType.CUSTOM, is_a_property=True)
    _available_metrics = BlockField(name="available_metrics",
                                    field_type=FieldType.RAW,
                                    is_a_property=True)

    metric = ParamField(name="metric", title="Metric", field_type=FieldType.STR,
                        input_type=InputType.SELECT, select_provider="available_metrics")

    def __init__(self, *args, **kwargs):
        super(RcVisualizer, self).__init__(*args, **kwargs)

    @property
    @log_timing
    def available_metrics(self):
        try:
            return [
                {"pk": metric_name, "str": metric.title}
                for metric_name, metric in metrics_dict.iteritems()
                if metric.produce_single_number
            ]
        except Exception, e:
            if self.exp_id:
                    exp = Experiment.get_exp_by_id(self.exp_id)
                    exp.log(self.uuid, e, severity="CRITICAL")
            log.exception(e)
            return []

    @property
    def rc(self):
        return self.get_input_var("results_container")