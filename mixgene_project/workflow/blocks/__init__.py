from fetch_gse import FetchGSE
from fetch_bi_gs import GetBroadInstituteGeneSet
from crossvalidation import CrossValidation
from merge_gene_set_annotation import MergeGeneSetWithPlatformAnnotation

from globaltest import GlobalTest
from user_upload import UserUpload, UserUploadComplex, UploadInteraction, UploadGeneSets
from expression_sets_merge import MergeExpressionSets
from aggregation import SubAggregation, SvdAggregation
from aggregation import GeneSetAgg
from classifiers import GaussianNb, DecisionTree, RandomForest, \
    KnnClassifier, LinearSVM, KernelSvm
from custom_iterator import CustomIterator
from filter_by_bi import FilterByInteraction
from mass_upload import MassUpload

from multi_features import MultiFeature
from box_plot import BoxPlot
from pca_visualize import PcaVisualize
from rc_table import RenderTable
from feature_selection import SvmrfeRanking, \
    SvmrfeRestrictedRanking, TTestRanking, RandomRanking, FeatureSelectionByCut
from table_result_view import TableResultView
from filter import FilterBlock


from blocks_pallet import block_classes_by_name, blocks_by_group


def get_block_class_by_name(name):
    if name in block_classes_by_name.keys():
        return block_classes_by_name[name]
    else:
        raise KeyError("No such plugin: %s" % name)

