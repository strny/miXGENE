from workflow.blocks.input_data.fetch_gse import FetchGSE
from workflow.blocks.input_data.fetch_bi_gs import GetBroadInstituteGeneSet
from workflow.blocks.meta.crossvalidation import CrossValidation
# from workflow.blocks.processing.merge_gene_set_annotation import MergeGeneSetWithPlatformAnnotation

from workflow.blocks.input_data.upload_gene_sets import UploadGeneSets
from workflow.blocks.input_data.upload_interaction import UploadInteraction
from workflow.blocks.input_data.user_upload_complex import UserUploadComplex
from workflow.blocks.input_data.user_upload import UserUpload

from workflow.blocks.meta.custom_iterator import CustomIterator
from workflow.blocks.meta.mass_upload import MassUpload
from workflow.blocks.meta.multi_features import MultiFeature
# from workflow.blocks.meta.pattern_search import PatternSearch

from workflow.blocks.testing.globaltest import GlobalTest
from workflow.blocks.filters.feature_selection_by_cut import FeatureSelectionByCut
from workflow.blocks.processing.random_ranking import RandomRanking
from workflow.blocks.processing.ttest_ranking import TTestRanking
from workflow.blocks.processing.svmrfe_restricted_ranking import SvmrfeRestrictedRanking
from workflow.blocks.processing.svmrfe_ranking import SvmrfeRanking
from workflow.blocks.processing.expression_sets_merge import MergeExpressionSets

from workflow.blocks.aggregation.gene_set_agg_cv import GeneSetAggCV
from workflow.blocks.aggregation.svd_sub_agg import SubAggregation
from workflow.blocks.aggregation.svd_sub_agg import SvdAggregation
from workflow.blocks.aggregation.gene_set_agg import GeneSetAgg


from workflow.blocks.filters.filter import FilterBlock
from workflow.blocks.normalization.quantile_norm import QuantileNormBlock
from workflow.blocks.normalization.zscore_filter import ZScoreBlock
from workflow.blocks.snmnmf.threshold import ThresholdBlock
from workflow.blocks.filters.filter_by_bi import FilterByInteraction
from workflow.blocks.processing.merge_comodule import MergeComoduleSets

from workflow.blocks.testing.enrichment_no_t_block import EnrichmentNoTBlock
from workflow.blocks.snmnmf.nimfa_snmnmf import NIMFASNMNMFBlock

from workflow.blocks.pattern_search.pattern_search import PatternSearch
from workflow.blocks.filters.pattern_filter import PatternFilter
from workflow.blocks.pattern_search.pattern_edges import PatternEdges

from workflow.blocks.classifiers.ncf import NCF
from workflow.blocks.classifiers.decision_tree import DecisionTree
from workflow.blocks.classifiers.gaussian_nb import GaussianNb
from workflow.blocks.classifiers.kernel_svm import KernelSvm
from workflow.blocks.classifiers.knn_classifier import KnnClassifier
from workflow.blocks.classifiers.linear_svm import LinearSVM
# from workflow.blocks.classifiers.random_forest import RandomForest

from workflow.blocks.visualizers.pattern_visualize import PatternView
from workflow.blocks.visualizers.pca_visualize import PcaVisualize
from workflow.blocks.visualizers.rc_table import RenderTable
from workflow.blocks.visualizers.table_result_view import TableResultView
from workflow.blocks.snmnmf.comodule_visualize import ComoduleSetView
from workflow.blocks.visualizers.dictionary_visualize import DictionarySetView
from workflow.blocks.visualizers.enrichment_visualize import EnrichmentVisualize


from blocks_pallet import block_classes_by_name, blocks_by_group


def get_block_class_by_name(name):
    if name in block_classes_by_name.keys():
        return block_classes_by_name[name]
    else:
        raise KeyError("No such plugin: %s" % name)


# the code below is for compatibility with old mixgene structure!!!
OLD_MODULES = ['aggregation', 'box_plot', 'classifiers', 'comodule_visualize',
               'crossvalidation', 'custom_iterator', 'dictionary_visualize',
               'enrichment_block', 'enrichment_no_t_block', 'enrichment_visualize',
               'expression_sets_merge', 'feature_selection', 'fetch_bi_gs', 'fetch_gse',
               'filter_by_bi', 'globaltest', 'mass_upload', 'merge_comodule',
               'merge_gene_set_annotation', 'meta_block', 'multi_features', 'nimfa_snmnmf',
               'pca_visualize', 'rc_table', 'rc_vizualize',
               'table_result_view', 'user_upload', 'filter', 'threshold']

import sys

import importlib
for old_mod in OLD_MODULES:
    curr_mod = importlib.import_module("workflow.blocks.obsolete_comp.dep_%s" % old_mod)
    sys.modules["workflow.blocks.%s" % old_mod] = curr_mod

# OLD_MODULES = ['meta_block', 'pattern_search', 'globaltest']
# from workflow.blocks.meta import meta_block
# from workflow.blocks.meta import pattern_search
# from workflow.blocks.processing import globaltest
#
#
# sys.modules["workflow.blocks.meta_block"] = meta_block
# sys.modules["workflow.blocks.pattern_search"] = pattern_search
# sys.modules["workflow.blocks.globaltest"] = globaltest





