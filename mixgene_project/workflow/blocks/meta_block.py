# -*- coding: utf-8 -*-

from copy import deepcopy
import logging

import redis_lock

from mixgene.redis_helper import ExpKeys
from mixgene.util import get_redis_instance
from webapp.models import Experiment
from environment.structures import SequenceContainer
from webapp.scope import ScopeRunner, ScopeVar

from generic import InnerOutputField
from workflow.blocks.generic import GenericBlock, ActionsList, save_params_actions_list, BlockField, FieldType, \
    ActionRecord, ParamField, InputType, OutputBlockField, InputBlockField, IteratedInnerFieldManager


log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class UniformMetaBlock(GenericBlock):
    create_new_scope = True
    is_block_supports_auto_execution = True

    _block_actions = ActionsList([])
    _block_actions.extend(ActionsList([
        ActionRecord("save_params", ["created", "valid_params", "done", "ready"], "validating_params",
                     user_title="Save parameters"),
        ActionRecord("on_params_is_valid", ["validating_params"], "valid_params"),
        ActionRecord("on_params_not_valid", ["validating_params"], "created"),

        ActionRecord("on_feature_selection_updated", ["valid_params", "ready", "done"], "ready"),

        ActionRecord("execute", ["ready"], "generating_folds", user_title="Run block"),

        ActionRecord("on_folds_generation_success", ["generating_folds"], "ready_to_run_sub_scope", reload_block_in_client=True),
        ActionRecord("continue_collecting_sub_scope", ["ready_to_run_sub_scope"],
                     "sub_scope_executing"),

        ActionRecord("run_sub_scope", ["ready_to_run_sub_scope"], "sub_scope_executing"),
        ActionRecord("on_sub_scope_done", ["sub_scope_executing"], "ready_to_run_sub_scope"),

        ActionRecord("success", ["working", "ready_to_run_sub_scope"], "done",
                     propagate_auto_execution=True, reload_block_in_client=True),
        ActionRecord("error", ["ready", "working", "sub_scope_executing",
                               "generating_folds", "ready_to_run_sub_scope"],
                     "execution_error", reload_block_in_client=True),

        ActionRecord("reset_execution", ["*", "done", "sub_scope_executing", "ready_to_run_sub_scope",
                                         "generating_folds", "execution_error"], "ready",
                     user_title="Reset execution"),
        ]))

    _input_es_dyn = InputBlockField(
        name="es_inputs", required_data_type="ExpressionSet",
        required=True, multiply_extensible=True
    )

    _res_seq = OutputBlockField(name="res_seq", provided_data_type="SequenceContainer",
                                field_type=FieldType.CUSTOM, init_val=SequenceContainer())

    def __init__(self, *args, **kwargs):
        super(UniformMetaBlock, self).__init__(*args, **kwargs)
        self.auto_exec_status_working.update(["sub_scope_executing", "ready_to_run_sub_scope",
                                              "generating_folds"])

        self.inner_output_manager = IteratedInnerFieldManager()
        self.features = []
        self.inner_output_es_names_map = {}
        self.celery_task = None

        self.set_out_var("res_seq", SequenceContainer())

    @property
    def is_sub_pages_visible(self):
        if self.state in ['valid_params', 'done', 'ready']:
            return True
        return False

    def get_fold_labels(self):
        pass

    def get_inner_out_var(self, name):
        return self.inner_output_manager.get_var(name)

    def run_sub_scope(self, exp, *args, **kwargs):
        self.reset_execution_for_sub_blocks()

        exp.store_block(self)
        sr = ScopeRunner(exp, self.sub_scope_name)
        sr.execute()

    def on_sub_scope_done(self, exp, *args, **kwargs):
        """
            @type exp: Experiment

            This action should be called by ScopeRunner
            when all blocks in sub-scope have exec status == done
        """
        r = get_redis_instance()
        with redis_lock.Lock(r, ExpKeys.get_metablock_collect_lock_key(self.exp_id, self.uuid)):
            res_seq = self.get_out_var("res_seq")
            cell = res_seq.sequence[self.inner_output_manager.iterator]
            for name, scope_var in self.collector_spec.bound.iteritems():
                var = exp.get_scope_var_value(scope_var)
                log.debug("Collected %s from %s", var, scope_var.title)
                if var is not None:
                    cell[name] = deepcopy(var)

            res_seq.sequence[self.inner_output_manager.iterator] = cell
            self.set_out_var("res_seq", res_seq)
            exp.store_block(self)

        # print "Collected fold results: %s " % cell
        if len(cell) < len(res_seq.fields):
            self.do_action("continue_collecting_sub_scope", exp)
        else:
            try:
                self.inner_output_manager.next()
                self.do_action("run_sub_scope", exp)
            except StopIteration, e:
                # All folds was processed without errors
                self.do_action("success", exp)

    def continue_collecting_sub_scope(self, exp, *args, **kwargs):
        pass

    def on_folds_generation_success(self, exp, sequence, *args, **kwargs):
        self.inner_output_manager.sequence = sequence
        self.inner_output_manager.next()

        res_seq = self.get_out_var("res_seq")
        res_seq.clean_content()
        res_seq.sequence = [{"__label__": label} for label in self.get_fold_labels()]
        self.set_out_var("res_seq", res_seq)

        exp.store_block(self)
        self.do_action("run_sub_scope", exp)

    def success(self, exp, *args, **kwargs):
        pass

    def add_collector_var(self, exp, *args, **kwargs):
        super(UniformMetaBlock, self).add_collector_var(exp, *args, **kwargs)
        res_seq = self.get_out_var("res_seq")
        res_seq.fields = {
            name: var.data_type
            for name, var in self.collector_spec.bound.iteritems()
        }
        exp.store_block(self)


