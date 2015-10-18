__author__ = 'pavel'


from webapp.tasks import wrapper_task
from workflow.blocks.blocks_pallet import GroupType
from workflow.blocks.fields import ActionsList, ActionRecord, InputBlockField, ParamField, InputType, FieldType, \
    OutputBlockField
from workflow.blocks.generic import GenericBlock, execute_block_actions_list
from environment.structures import ComoduleSet
from django.conf import settings
from pandas import merge
import numpy as np
import pandas as pd
from pandas import Series
#@task(name="wrappers.filter.merge_comodules_task")
def merge_comodules_task(exp, block,
                     cs_1,
                     cs_2,
                     cs_1_name,
                     cs_2_name,
                     base_filename,
    ):

    if settings.CELERY_DEBUG:
        import sys
        sys.path.append('/Migration/skola/phd/projects/miXGENE/mixgene_project/wrappers/pycharm-debug.egg')
        import pydevd
        pydevd.settrace('localhost', port=6901, stdoutToServer=True, stderrToServer=True)


    CS1 = cs_1.load_set()
    CS2 = cs_2.load_set()
    df = merge(CS1, CS2, left_index=True, right_index=True, how='outer')
    df.columns = [cs_1_name, cs_2_name]
    # df = CS1.join(CS2)
    # df = pd.DataFrame({'genes':CS1.values, 'miRNAs':CS2.values}, index=CS1.index)
    print(df.info())
    cs = ComoduleSet(exp.get_data_folder(), base_filename)
    cs.store_set(df)
    return [cs], {}

class MergeComoduleSets(GenericBlock):
    block_base_name = "MERGE_COMODULE_SETS"
    name = "Merge Comodule Sets"

    is_abstract = False
    block_group = GroupType.PROCESSING

    is_block_supports_auto_execution = True

    _block_actions = ActionsList([
        ActionRecord("save_params", ["created", "valid_params", "done", "ready"], "validating_params",
                     user_title="Save parameters"),
        ActionRecord("on_params_is_valid", ["validating_params"], "ready"),
        ActionRecord("on_params_not_valid", ["validating_params"], "created"),
        ])
    _block_actions.extend(execute_block_actions_list)

    _cs_1 = InputBlockField(name="cs_1", order_num=10, required_data_type="ComoduleSet", required=True)
    _cs_1_name = ParamField(name="cs_1_name", order_num=11, title="Comodule 1 name", input_type=InputType.TEXT, field_type=FieldType.STR, init_val="genes")


    _cs_2 = InputBlockField(name="cs_2", order_num=20, required_data_type="ComoduleSet", required=True)
    _cs_2_name = ParamField(name="cs_2_name", order_num=21, title="Comodule 2 name", input_type=InputType.TEXT, field_type=FieldType.STR, init_val="genes")


    flt_es = OutputBlockField(name="comodule_set", provided_data_type="ComoduleSet")

    def __init__(self, *args, **kwargs):
        super(MergeComoduleSets, self).__init__(*args, **kwargs)
        self.celery_task = None

    def execute(self, exp, *args, **kwargs):
        self.clean_errors()
        cs_1 = self.get_input_var("cs_1")
        cs_2 = self.get_input_var("cs_2")

        self.celery_task = wrapper_task.s(
            merge_comodules_task,
            exp, self,
            cs_1=cs_1,
            cs_2=cs_2,
            cs_1_name=self.cs_1_name,
            cs_2_name=self.cs_2_name,
            base_filename="%s_%s_thr" % (self.uuid, 'merge_cs')
        )
        exp.store_block(self)
        self.celery_task.apply_async()

    def success(self, exp, flt_es):
        self.set_out_var("comodule_set", flt_es)
        exp.store_block(self)
