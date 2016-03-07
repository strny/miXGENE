__author__ = 'pavel'


import pandas as pd
from webapp.tasks import wrapper_task
from workflow.blocks.blocks_pallet import GroupType
from workflow.blocks.fields import FieldType, BlockField, OutputBlockField, InputBlockField, InputType, ParamField, \
    ActionRecord, ActionsList

from workflow.blocks.generic import GenericBlock, save_params_actions_list, execute_block_actions_list

from converters.gene_set_tools import map_gene_sets_to_probes
from django.conf import settings
from wrappers.pattern_search.pattern_search import DifferentialPatternSearcher
from environment.structures import ComoduleSet, GS, GeneSets
import scipy.sparse as sp
from wrappers.pattern_search.utils import mergeNetworks
from scipy.stats import zscore
from webapp.notification import AllUpdated, NotifyMode
from scipy.sparse import hstack
from pandas import SparseDataFrame


def sparse_df_to_saprse_matrix(sparse_df):
    # sparse_df = sparse_df.to_sparse()
    index_list = sparse_df.index.values.tolist()
    matrix_columns = []
    sparse_matrix = None
    for column in sparse_df.columns:
        sps_series = sparse_df[column]
        sps_series.index = pd.MultiIndex.from_product([index_list, [column]])
        curr_sps_column, rows, cols = sps_series.to_coo()
        if sparse_matrix is not None:
            sparse_matrix = hstack([sparse_matrix, curr_sps_column])
        else:
            sparse_matrix = curr_sps_column
        matrix_columns.extend(cols)
    return sparse_matrix, index_list, matrix_columns


def pattern_search(exp, block,
            m_rna_es,
            mi_rna_es,
            gene2gene,
            miRNA2gene,
            # gene_platform,
            # miRNA_platform,
            radius,
            min_imp,
            metric,
            base_filename):
    """
        @type m_rna_es: ExpressionSet
        @type mi_rna_es: ExpressionSet
        @type gene2gene: BinaryInteraction
        @type miRNA2gene: BinaryInteraction
        @type radius: int
        @type min_imp: double
    """

    AllUpdated(
        exp.pk,
        comment=u"Initializing data...",
        silent=False,
        mode=NotifyMode.INFO
    ).send()

    exp.log(block.uuid, "Initializing data...")

    mData = m_rna_es.get_assay_data_frame()
    gene_platform = list(mData.columns)
    AllUpdated(
        exp.pk,
        comment=u"Transforming interaction matrix",
        silent=False,
        mode=NotifyMode.INFO
    ).send()

    gene2gene = gene2gene.get_matrix_for_platform(exp, gene_platform, symmetrize=True, identifiers=False)

    AllUpdated(
        exp.pk,
        comment=u"Transforming interaction matrix done",
        silent=False,
        mode=NotifyMode.INFO
    ).send()

    # TODO fix pattern search
    # if miRNA2gene is not None:
    #     miRNA2gene = miRNA2gene.load_matrix().T
    #     miRNA2gene = sp.coo_matrix(miRNA2gene.values)
    # if mi_rna_es is not None:
    #     miData = mi_rna_es.get_assay_data_frame()
    #     mir2gene = miRNA2gene
    #     mir2gene = sp.coo_matrix(mir2gene.values).T
    #     nw = mergeNetworks(gene2gene, mir2gene)
    # else:
    # gene2gene = gene2gene.load_matrix()
    # nw = sparse_df_to_saprse_matrix(gene2gene)
    nw = gene2gene.tocsr()
    # data = mData.ix[1:]
    data = mData
    data.set_index(data.columns[0], inplace=True, drop=True)

    data = zscore(data)
    pheno = m_rna_es.get_pheno_data_frame()
    classes = pheno['User_class'].values
    if settings.CELERY_DEBUG:
        import sys
        sys.path.append('/Migration/skola/phd/projects/miXGENE/mixgene_project/wrappers/pycharm-debug.egg')
        import pydevd
        pydevd.settrace('localhost', port=6901, stdoutToServer=True, stderrToServer=True)

    exp.log(block.uuid, "Data ready. Running Pattern Search")

    # inicializace objektu metric=metric,
    searcher = DifferentialPatternSearcher(nw, radius=radius, min_improve=min_imp,
                                           base_dir="orig_interactions/", verbose=True)

    #vlastni search
    res = searcher.search(data, classes)
    exp.log(block.uuid, "Pattern search finished.")

    # res ... list patternu,
    # tj. pro nase potreby:
    comodule_set = map(lambda pattern: [gene_platform[gene] for gene in pattern.genes], res)

    # cs = ComoduleSet(exp.get_data_folder(), base_filename)
    gene_sets = GeneSets(exp.get_data_folder(), "%s_ps_gene_sets" % str(block.uuid))
    result = {key: value for key, value in enumerate(comodule_set)}
    gs = GS(result, result)
    gene_sets.store_gs(gs)

    # self.set_out_var("gene_sets", gene_sets)
    # result = {key: value for key, value in enumerate(comodule_set)}
    # cs.store_set(result)
    # exp.log(block.uuid, "ComoduleSet stored.")

    return [gene_sets], {}


class PatternSearch(GenericBlock):
    block_base_name = "PattSearch"
    name = "Pattern Search"
    block_group = GroupType.PATTERN_SEARCH

    is_block_supports_auto_execution = True

    _block_actions = ActionsList([
        ActionRecord("save_params", ["created", "valid_params", "done", "ready"], "validating_params",
                     user_title="Save parameters"),
        ActionRecord("on_params_is_valid", ["validating_params"], "ready"),
        ActionRecord("on_params_not_valid", ["validating_params"], "created"),
        ])
    _block_actions.extend(execute_block_actions_list)

    _m_rna = InputBlockField(name="mRNA", order_num=10, required_data_type="ExpressionSet", required=True)
    _mi_rna = InputBlockField(name="miRNA", order_num=20, required_data_type="ExpressionSet", required=False)

    gene2gene = InputBlockField(name="gene2gene", order_num=30,
                                required_data_type="BinaryInteraction",
                                required=True)
    miRNA2gene = InputBlockField(name="miRNA2gene", order_num=31,
                                 required_data_type="BinaryInteraction",
                                 required=False)

    # upload_gene2gene_platform = ParamField("upload_gene2gene_platform", title="PPI platform", order_num=32,
    #                                        input_type=InputType.FILE_INPUT, field_type=FieldType.CUSTOM)

    # upload_mirna_platform = ParamField("upload_mirna_platform", title="miRNA platform", order_num=33,
    #                                    input_type=InputType.FILE_INPUT, field_type=FieldType.CUSTOM, required=False)

    d = ParamField(name="d", order_num=70, title="d", input_type=InputType.TEXT, field_type=FieldType.INT,
                    init_val=2)
    min_imp = ParamField(name="min_imp", order_num=80, title="Minimal improvement", input_type=InputType.TEXT, field_type=FieldType.FLOAT,
                    init_val=0.06)

    _metric = ParamField(
        "metric", title="Metric", order_num=40,
        input_type=InputType.SELECT, field_type=FieldType.STR,
        init_val="mutual_information",
        options={
            "inline_select_provider": True,
            "select_options": [
                ["mutual_information", "Mutual Information"],
                ['normed_mutual_information', "Normed Mutual Information"],
                ['square_error', "Square Error"],
                ['correlation', "Correlation"],
                ['t-test', "TTest"],
                ['wilcoxon', "Wilcoxon"]
            ]
        }
    )
    patterns = OutputBlockField(name="patterns", provided_data_type="GeneSets")

    def __init__(self, *args, **kwargs):
        super(PatternSearch, self).__init__(*args, **kwargs)
        self.celery_task = None

    def execute(self, exp, *args, **kwargs):
        self.clean_errors()
        exp.log(self.uuid, "Execute called")

        self.celery_task = wrapper_task.s(
            pattern_search,
            exp, self,
            m_rna_es = self.get_input_var("mRNA"),
            mi_rna_es = self.get_input_var("miRNA"),
            gene2gene=self.get_input_var("gene2gene"),
            miRNA2gene=self.get_input_var("miRNA2gene"),
            radius=self.d,
            min_imp=self.min_imp,
            metric=self.get_input_var("metric"),
            base_filename="%s_comodule_sets" % self.uuid,
        )
        exp.store_block(self)
        self.celery_task.apply_async()

    def success(self, exp, gs):
        exp.log(self.uuid, "Success")
        self.set_out_var("patterns", gs)
        exp.store_block(self)
