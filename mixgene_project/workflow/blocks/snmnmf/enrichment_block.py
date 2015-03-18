__author__ = 'pavel'


from webapp.tasks import wrapper_task
from blocks_pallet import GroupType
from fields import ActionsList, ActionRecord, InputBlockField, ParamField, InputType, FieldType, \
    OutputBlockField
from generic import GenericBlock, execute_block_actions_list
from environment.structures import DictionarySet
from django.conf import settings
from wrappers.snmnmf.evaluation import EnrichmentInGeneSets


def enrichment_task(exp, block,
                     gs,
                     H2,
                     T,
                     base_filename,
    ):

    if settings.CELERY_DEBUG:
        import sys
        sys.path.append('/Migration/skola/phd/projects/miXGENE/mixgene_project/wrappers/pycharm-debug.egg')
        import pydevd
        pydevd.settrace('localhost', port=6901, stdoutToServer=True, stderrToServer=True)
    gene_set = gs.get_gs()
    h2 = H2.get_assay_data_frame()
    e = EnrichmentInGeneSets(h2)
    ## compute enrichment in GO terms ()
    enrich_bpGO = e.getEnrichmentInGeneSetsWithH(gene_set.genes, h2, T)
    # sort resultst accodring p-values
   # sorted_enrich_bpGO = sorted(enrich_bpGO.iteritems(), key=operator.itemgetter(1))
    er_ratio = e.getEnrichmentRatioInGeneSetsWithH(gene_set.genes, h2, T, enrichment_threshold=0.05, N=10)
    enrich_bpGO['er_ratio'] = er_ratio
    ds = DictionarySet(exp.get_data_folder(), base_filename)
    ds.store_dict(enrich_bpGO)
    return [ds], {}

class EnrichmentBlock(GenericBlock):
    block_base_name = "ENRICHMENT"
    name = "Enrichment"

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
    H = InputBlockField(name="H2_genes", order_num=11, required_data_type="ExpressionSet", required=True)
    _t = ParamField(name="T", order_num=12, title="Parameter T", input_type=InputType.TEXT, field_type=FieldType.FLOAT, init_val="0.1")



    dict = OutputBlockField(name="dictionary_set", provided_data_type="DictionarySet")

    def __init__(self, *args, **kwargs):
        super(EnrichmentBlock, self).__init__(*args, **kwargs)
        self.celery_task = None

    def execute(self, exp, *args, **kwargs):
        self.clean_errors()
        gs = self.get_input_var("gs")
        h2 = self.get_input_var("H2_genes")
        self.celery_task = wrapper_task.s(
            enrichment_task,
            exp, self,
            gs = gs,
            H2 = h2,
            T=self.T,
            base_filename="%s_%s_enrich" % (self.uuid, 'enrichment')
        )
        exp.store_block(self)
        self.celery_task.apply_async()

    def success(self, exp, flt_es):
        self.set_out_var("dictionary_set", flt_es)
        exp.store_block(self)
