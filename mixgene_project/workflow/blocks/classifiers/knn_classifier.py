__author__ = 'pavel'

from .generic_classifier import GenericClassifier
from workflow.blocks.fields import BlockField, ParamField, InputType, FieldType


class KnnClassifier(GenericClassifier):
    block_base_name = "KNN"
    name = "Knn classifier"

    classifier_name = "knn"

    n_neighbors = ParamField(
        name="n_neighbors",
        title="Number of neighbors",
        input_type=InputType.TEXT,
        field_type=FieldType.INT,
        init_val=1,
        order_num=10,
    )

    algorithm = ParamField(
        name="algorithm",
        title="Algorithm [optional]",
        input_type=InputType.SELECT,
        field_type=FieldType.STR,
        order_num=20,
        options={
            "inline_select_provider": True,
            "select_options": [
                 ["ball_tree", "BallTree"],
                 ["kd_tree", "KDTree"],
                 ["brute", "Brute force search"],
                 ["auto", "Auto guess algorithm"],
            ]
        }
    )

    leaf_size = ParamField(
        name="leaf_size",
        title="Leaf size for BallTree or KDTree [optional]",
        input_type=InputType.TEXT,
        field_type=FieldType.INT,
        order_num=30,
    )

    _metric_options = BlockField(name="metric_options", field_type=FieldType.RAW)
    metric_options = [
        {"pk": "euclidean", "str": "Euclidean Distance"},
        {"pk": "manhattan", "str": "Manhattan Distance"},
        {"pk": "chebyshev", "str": "Chebyshev Distance"},
    ]
    metric = ParamField(
        name="metric",
        title="The distance metric to use for the tree [optional]",
        input_type=InputType.SELECT,
        field_type=FieldType.STR,
        select_provider="metric_options",
        order_num=40,
        options={
            "inline_select_provider": True,
            "select_options": [
                ["euclidean", "Euclidean Distance"],
                ["manhattan", "Manhattan Distance"],
                ["chebyshev", "Chebyshev Distance"],
            ]
        }
    )

    def collect_options(self):
        self.collect_option_safe("n_neighbors", int)
        self.collect_option_safe("algorithm")
        self.collect_option_safe("leaf_size", int)
        self.collect_option_safe("metric")