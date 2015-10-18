from collections import defaultdict
import logging


log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

block_classes_by_name = {}
blocks_by_group = defaultdict(list)


def register_block(code_name, human_title, group, cls):
    """
        Registers block to the toolbox pallet
    """
    block_classes_by_name[code_name] = cls
    blocks_by_group[group].append({
        "name": code_name,
        "title": human_title,
    })


class GroupType(object):
    INPUT_DATA = "01 Input data"
    META_PLUGIN = "02 Meta block"
    PROCESSING = "03 Data processing"
    AGGREGATION = "04 Feature Aggregation"
    TESTING = "05 Significance Testing"
    NORMALIZATION = "06 Data Normalization"
    FILTER = "07 Filter"
    PATTERN_SEARCH = "08 Pattern search"
    SNMNMF = "09 SNMNMF"
    VISUALIZE = "10 Visualize"
    CLASSIFIER = "11 Classifier"



