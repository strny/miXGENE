__author__ = 'pavel'

from webapp.tasks import wrapper_task
from blocks_pallet import GroupType
from fields import ActionsList, ActionRecord, InputBlockField, ParamField, InputType, FieldType, \
    OutputBlockField
from generic import GenericBlock, execute_block_actions_list
import wrappers.snmnmf.nimfa_snmnmf as ns
from django.conf import settings

# @task(name="wrappers.filter.filter_task")
def nimfa_snmnmf_task(exp,
                      block,
                      mRNA,
                      miRNA,
                      # DNAmethyl,
                      gene2gene,
                      miRNA2gene,
                      # gene2DNAmethylation,
                      params,
                      base_filename
):
    if settings.CELERY_DEBUG:
        import sys
        sys.path.append('/Migration/skola/phd/projects/miXGENE/mixgene_project/wrappers/pycharm-debug.egg')
        import pydevd
        pydevd.settrace('localhost', port=6901, stdoutToServer=True, stderrToServer=True)

    ### factorization ###
    # initialize the factorization
    # mi_rna = mi_rna[mi_rna.columns[0:30]]
    #     m_rna = m_rna[m_rna.columns[0:50]]
    #
    # TODO FULL
    mRNA_matrix = mRNA.get_assay_data_frame()
    mRNA_matrix = mRNA_matrix[mRNA_matrix.columns[0:50]]
    miRNA_matrix = miRNA.get_assay_data_frame()
    miRNA_matrix = miRNA_matrix[miRNA_matrix.columns[0:30]]
    snm = ns.NIMFA_SNMNMF(mRNA=mRNA_matrix, miRNA=miRNA_matrix, DNAmethyl=None,
                          gene2gene=gene2gene.load_matrix(), miRNA2gene=miRNA2gene.load_matrix(),
                          gene2DNAmethylation=None,
                          params=params)

    # run factorization
    snm.run(seed="random_c", rank=params['rank'], max_iter=5)

    W = mRNA.clone(base_filename + "_W")
    W.store_assay_data_frame(snm.W)

    H1_miRNA = mRNA.clone(base_filename + "_H1_miRNA")
    H1_miRNA.store_assay_data_frame(snm.H1_miRNA)

    H2_genes = mRNA.clone(base_filename + "_H2_genes")
    H2_genes.store_assay_data_frame(snm.H2_genes)

    # get factorization performance evaluation
    #    perf = snm.performance.getResults()
    #   H1_perf = mRNA.clone(base_filename+"_H1_perf")
    #   H1_perf.store_assay_data_frame(perf['H0'])
    #   H2_perf = mRNA.clone(base_filename+"_H2_perf")
    #   H2_perf.store_assay_data_frame(perf['H1'])

    return [W, H1_miRNA, H2_genes,
            # H1_perf, H2_perf
           ], {}


class NIMFASNMNMFBlock(GenericBlock):
    block_base_name = "NIMFA_SNMNMF"
    name = "NIMFA SNMNMF"

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

    _m_rna = InputBlockField(name="mRNA", order_num=10, required_data_type="ExpressionSet", required=True)
    _mi_rna = InputBlockField(name="miRNA", order_num=20, required_data_type="ExpressionSet", required=True)
    # _dna_methyl = InputBlockField(name="DNAmethyl", order_num=30, required_data_type="ExpressionSet", required=False)
    _gene2gene = InputBlockField(name="Gene2Gene", order_num=40, required_data_type="BinaryInteraction", required=True)
    _mirna2gene = InputBlockField(name="miRNA2gene", order_num=50, required_data_type="BinaryInteraction",
                                  required=True)
    # _gene2DNAmethylation =  InputBlockField(name="Gene2DNAmethyl", order_num=60, required_data_type="BinaryInteraction", required=False)


    l1 = ParamField(name="l1", order_num=70, title="l1", input_type=InputType.TEXT, field_type=FieldType.FLOAT,
                    init_val=0.1)
    l2 = ParamField(name="l2", order_num=80, title="l2", input_type=InputType.TEXT, field_type=FieldType.FLOAT,
                    init_val=0.1)
    g1 = ParamField(name="g1", order_num=90, title="g1", input_type=InputType.TEXT, field_type=FieldType.FLOAT,
                    init_val=0.1)
    g2 = ParamField(name="g2", order_num=100, title="g2", input_type=InputType.TEXT, field_type=FieldType.FLOAT,
                    init_val=0.1)
    rank = ParamField(name="rank", order_num=110, title="rank", input_type=InputType.TEXT, field_type=FieldType.INT,
                      init_val=50)

    w = OutputBlockField(name="W", provided_data_type="ExpressionSet")
    H1_miRNA = OutputBlockField(name="H1_miRNA", provided_data_type="ExpressionSet")
    H2_genes = OutputBlockField(name="H2_genes", provided_data_type="ExpressionSet")
    # H3_DNAmethyl = OutputBlockField(name="H3_DNAmethyl", provided_data_type="ExpressionSet")

    #H1_perf = OutputBlockField(name="H1_perf", provided_data_type="ExpressionSet")
    #H2_perf = OutputBlockField(name="H2_perf", provided_data_type="ExpressionSet")

    def __init__(self, *args, **kwargs):
        super(NIMFASNMNMFBlock, self).__init__(*args, **kwargs)
        self.celery_task = None

    def execute(self, exp, *args, **kwargs):
        self.clean_errors()
        mRNA = self.get_input_var("mRNA")
        miRNA = self.get_input_var("miRNA")
        #DNAmethyl = self.get_input_var("DNAmethyl")
        Gene2Gene = self.get_input_var("Gene2Gene")
        miRNA2gene = self.get_input_var("miRNA2gene")
        #Gene2DNAmethyl = self.get_input_var("Gene2DNAmethyl")

        self.celery_task = wrapper_task.s(
            nimfa_snmnmf_task,
            exp,
            self,
            mRNA=mRNA,
            miRNA=miRNA,
            #DNAmethyl = DNAmethyl,
            gene2gene=Gene2Gene,
            miRNA2gene=miRNA2gene,
            #gene2DNAmethylation = Gene2DNAmethyl,
            params={'l1': self.l1, 'l2': self.l2, 'g1': self.g1, 'g2': self.g2, 'rank': self.rank},
            base_filename="%s_%s_nimfa_snmnmf" % (self.uuid, self)
        )
        exp.store_block(self)
        self.celery_task.apply_async()

    def success(self, exp, W, H1, H2):
        self.set_out_var("W", W)
        self.set_out_var("H1_miRNA", H1)
        self.set_out_var("H2_genes", H2)
        #self.set_out_var("H1_perf", matrices[3])
        #self.set_out_var("H2_perf", matrices[4])
        exp.store_block(self)
