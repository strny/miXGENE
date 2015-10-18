__author__ = 'pavel'

from webapp.tasks import wrapper_task
from workflow.blocks.blocks_pallet import GroupType
from workflow.blocks.fields import ActionsList, ActionRecord, InputBlockField, ParamField, InputType, FieldType, \
    OutputBlockField
from workflow.blocks.generic import GenericBlock, execute_block_actions_list
from environment.structures import ComoduleSet
from django.conf import settings

import numpy as np
import pandas as pd
from pandas import Series
#@task(name="wrappers.filter.threshold_task")
def threshold_task(exp, block,
                     es,
                     T,
                     base_filename,
    ):

    # def removeTemporaryNegativeFeatures(S, indicator_string = 'negative_feature___'):
    #     """Remove elements starting with the indicator_string and remove possible duplicates."""
    #     return S.apply(lambda list_element: set([s.replace(indicator_string, '')  for s in list_element]))

    """Computes co-comodules from matrix H by given threshold T."""
    if settings.CELERY_DEBUG:
        import sys
        sys.path.append('/Migration/skola/phd/projects/miXGENE/mixgene_project/wrappers/pycharm-debug.egg')
        import pydevd
        pydevd.settrace('localhost', port=6901, stdoutToServer=True, stderrToServer=True)


    H = es.get_assay_data_frame()
    print(H)
    # mu = np.mean(H, axis = 1)
    # sigma = np.std(H, axis = 1)
    # Z = H.apply(lambda z: (z-mu)/sigma, axis = 0)
    # S = []
    # S.append(removeTemporaryNegativeFeatures(Z.apply(lambda x: Z.columns[x >= T].tolist(), axis = 1)))
    # S = pd.DataFrame(S)
    # S = S.apply(lambda x: set.union(*x))
    # result = pd.DataFrame(S)
    from wrappers.snmnmf.evaluation import EnrichmentInGeneSets
    z = 1
    x = EnrichmentInGeneSets(z)
    result = x.getGeneSet(H, T)
    cs = ComoduleSet(exp.get_data_folder(), base_filename)
    cs.store_set(result)
    return [cs], {}

class ThresholdBlock(GenericBlock):
    block_base_name = "THRESHOLD"
    name = "Threshold"

    is_abstract = False
    block_group = GroupType.SNMNMF

    is_block_supports_auto_execution = True

    _block_actions = ActionsList([
        ActionRecord("save_params", ["created", "valid_params", "done", "ready"], "validating_params",
                     user_title="Save parameters"),
        ActionRecord("on_params_is_valid", ["validating_params"], "ready"),
        ActionRecord("on_params_not_valid", ["validating_params"], "created"),
        ])
    _block_actions.extend(execute_block_actions_list)

    _es = InputBlockField(name="es", order_num=10, required_data_type="ExpressionSet", required=True)
    t = ParamField(name="T", title="Threshold", input_type=InputType.TEXT, field_type=FieldType.FLOAT, init_val=0.1)


    flt_es = OutputBlockField(name="comodule_set", provided_data_type="ComoduleSet")

    def __init__(self, *args, **kwargs):
        super(ThresholdBlock, self).__init__(*args, **kwargs)
        self.celery_task = None

    def execute(self, exp, *args, **kwargs):
        self.clean_errors()
        es = self.get_input_var("es")
        # T = self.get_input_var("T")
        self.celery_task = wrapper_task.s(
            threshold_task,
            exp, self,
            es=es,
            T=self.T,
            base_filename="%s_%s_thr" % (self.uuid, 'threshold')
        )
        exp.store_block(self)
        self.celery_task.apply_async()

    def success(self, exp, flt_es):
        self.set_out_var("comodule_set", flt_es)
        exp.store_block(self)
