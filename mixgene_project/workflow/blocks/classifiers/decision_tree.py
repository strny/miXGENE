__author__ = 'pavel'

from .generic_classifier import GenericClassifier
from workflow.blocks.fields import FieldType, BlockField, OutputBlockField, InputBlockField, InputType, ParamField, \
    ActionRecord, ActionsList


class DecisionTree(GenericClassifier):
    block_base_name = "DT"
    name = "Decision tree"

    classifier_name = "DT"

    criterion = ParamField(
        name="criterion",
        title="The function to measure the quality of a split",
        input_type=InputType.SELECT,
        field_type=FieldType.STR,
        order_num=11,
        options={
            "inline_select_provider": True,
            "select_options": [
                ["gini", "Gini impurity"],
                ["entropy", "Information gain"]
            ]
        }
    )

    max_features_mode = ParamField(
        name="max_features_mode",
        title="Max features for split, mode",
        input_type=InputType.SELECT,
        field_type=FieldType.STR,
        options={
            "inline_select_provider": True,
            "select_options": [
                ["int", "Fixed number"],
                ["float", "Ratio of the features number [0.0 .. 1.0]"],
                ["sqrt", "sqrt(number of features)"],
                ["log2", "log2(number of features)"],
            ]
        },
        order_num=20,
    )

    max_features_value = ParamField(
        name="max_features_value",
        title="Value for the chosen max feature mode",
        input_type=InputType.TEXT,
        field_type=FieldType.STR,
        order_num=30,
    )

    max_depth = ParamField(
        name="max_depth",
        title="The maximum depth of the tree",
        input_type=InputType.TEXT,
        field_type=FieldType.INT,
        order_num=40,
    )

    min_samples_split = ParamField(
        name="min_samples_split",
        title="The minimum number of samples to split an internal node",
        input_type=InputType.TEXT,
        field_type=FieldType.INT,
        order_num=50,
    )

    min_samples_leaf = ParamField(
        name="min_samples_leaf",
        title="The minimum number of samples to be at a leaf node",
        input_type=InputType.TEXT,
        field_type=FieldType.INT,
        order_num=60,
    )

    def collect_options(self):
        max_features_mode = self.get_option_safe("max_features_mode", str)
        if max_features_mode in ["sqrt", "log2"]:
            self.classifier_options["max_features"] = max_features_mode
        elif max_features_mode == "int":
            self.collect_option_safe("max_features_value", int, target_name="max_features")
        elif max_features_mode == "float":
            self.collect_option_safe("max_features_value", float, target_name="max_features")

        self.collect_option_safe("max_depth", int)
        self.collect_option_safe("min_samples_split", int)
        self.collect_option_safe("min_samples_leaf", int)