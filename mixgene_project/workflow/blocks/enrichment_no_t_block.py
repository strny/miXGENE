__author__ = 'pavel'


from webapp.tasks import wrapper_task
from blocks_pallet import GroupType
from fields import ActionsList, ActionRecord, InputBlockField, ParamField, InputType, FieldType, \
    OutputBlockField
from generic import GenericBlock, execute_block_actions_list
from environment.structures import DictionarySet
from django.conf import settings
from pandas import merge
import numpy as np
import pandas as pd
from pandas import Series
from wrappers.snmnmf.evaluation import EnrichmentInGeneSets
import operator


#@task(name="wrappers.filter.enrichment_task")
def enrichment_no_t_task(exp, block,
                     T,
                     gs,
                     cs,
                     base_filename,
    ):

    if settings.CELERY_DEBUG:
        import sys
        sys.path.append('/Migration/skola/phd/projects/miXGENE/mixgene_project/wrappers/pycharm-debug.egg')
        import pydevd
        pydevd.settrace('localhost', port=6901, stdoutToServer=True, stderrToServer=True)
    gene_set = gs.get_gs()
    cs = cs.load_set()
    e = EnrichmentInGeneSets(cs)
    enrich = e.getModuleEnrichmentInGeneSets(cs, gene_set.genes, pval_threshold=T)
    # enrich = [(mod, genes, map(lambda x: (x[0], x[1]), terms)) for (mod, (genes, terms)) in enrich.items()]
    enrich = dict((mod, (genes, map(lambda x: (gene_set.description[x[0]], x[0], x[1])), terms)) for (mod, (genes, terms)) in enrich.items())
    # enrich = [(mod, map(lambda x: (gene_set.description[x[0]], x[1]), terms), genes) for (mod, [terms, genes]) in enrich]
    # enrich = [z[0] for z in x[1] for x in enrich.items()]
    ds = DictionarySet(exp.get_data_folder(), base_filename)
    ds.store_dict(enrich)
    return [ds], {}

class EnrichmentNoTBlock(GenericBlock):
    block_base_name = "ENRICHMENT_CONT"
    name = "Contingency Enrichment"

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

    _cs_1 = InputBlockField(name="gs", order_num=10, required_data_type="GeneSets", required=True)
    H = InputBlockField(name="cs", order_num=11, required_data_type="ComoduleSet", required=True)
    _t = ParamField(name="T", order_num=12, title="Enrichment threshold", input_type=InputType.TEXT, field_type=FieldType.FLOAT, init_val="0.05")

    dict = OutputBlockField(name="dictionary_set", provided_data_type="DictionarySet")

    def __init__(self, *args, **kwargs):
        super(EnrichmentNoTBlock, self).__init__(*args, **kwargs)
        self.celery_task = None

    def execute(self, exp, *args, **kwargs):
        self.clean_errors()
        gs = self.get_input_var("gs")
        cs = self.get_input_var("cs")
        self.celery_task = wrapper_task.s(
            enrichment_no_t_task,
            exp, self,
            T = self.T,
            gs = gs,
            cs = cs,
            base_filename="%s_%s_enrich" % (self.uuid, 'enrichment_cont')
        )
        exp.store_block(self)
        self.celery_task.apply_async()

    def success(self, exp, flt_es):
        self.set_out_var("dictionary_set", flt_es)
        exp.store_block(self)
