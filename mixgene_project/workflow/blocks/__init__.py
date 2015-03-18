from workflow.blocks.input_data.fetch_gse import FetchGSE
from workflow.blocks.input_data.fetch_bi_gs import GetBroadInstituteGeneSet
from workflow.blocks.meta.crossvalidation import CrossValidation
from workflow.blocks.processing.merge_gene_set_annotation import MergeGeneSetWithPlatformAnnotation

from workflow.blocks.processing.globaltest import GlobalTest
from workflow.blocks.input_data.upload_gene_sets import UploadGeneSets
from workflow.blocks.input_data.upload_interaction import UploadInteraction
from workflow.blocks.input_data.user_upload_complex import UserUploadComplex
from workflow.blocks.input_data.user_upload import UserUpload
from workflow.blocks.processing.expression_sets_merge import MergeExpressionSets
from workflow.blocks.meta.custom_iterator import CustomIterator
from workflow.blocks.filters.filter_by_bi import FilterByInteraction
from workflow.blocks.meta.mass_upload import MassUpload

from workflow.blocks.meta.multi_features import MultiFeature
from workflow.blocks.visualizers.pca_visualize import PcaVisualize
from workflow.blocks.visualizers.rc_table import RenderTable
from workflow.blocks.processing.feature_selection_by_cut import FeatureSelectionByCut
from workflow.blocks.processing.random_ranking import RandomRanking
from workflow.blocks.processing.ttest_ranking import TTestRanking
from workflow.blocks.processing.svmrfe_restricted_ranking import SvmrfeRestrictedRanking
from workflow.blocks.processing.svmrfe_ranking import SvmrfeRanking
from workflow.blocks.visualizers.table_result_view import TableResultView
from workflow.blocks.filters.filter import FilterBlock
from workflow.blocks.filters.quantile_norm import QuantileNormBlock
from workflow.blocks.filters.zscore_filter import ZScoreBlock
from workflow.blocks.filters.threshold import ThresholdBlock
from workflow.blocks.visualizers.comodule_visualize import ComoduleSetView
from workflow.blocks.visualizers.dictionary_visualize import DictionarySetView
from workflow.blocks.snmnmf.enrichment_no_t_block import EnrichmentNoTBlock
from workflow.blocks.filters.merge_comodule import MergeComoduleSets
# from enrichment_block import EnrichmentBlock
from workflow.blocks.snmnmf.nimfa_snmnmf import NIMFASNMNMFBlock
from workflow.blocks.visualizers.enrichment_visualize import EnrichmentVisualize
from workflow.blocks.meta.pattern_search import PatternSearch
from blocks_pallet import block_classes_by_name, blocks_by_group


def get_block_class_by_name(name):
    if name in block_classes_by_name.keys():
        return block_classes_by_name[name]
    else:
        raise KeyError("No such plugin: %s" % name)

