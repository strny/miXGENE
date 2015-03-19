__author__ = 'pavel'

from .generic_classifier import GenericClassifier
from workflow.blocks.fields import InputBlockField, ParamField, InputType, FieldType


class WalkForest(GenericClassifier):
    block_base_name = "WALK_FOREST"
    name = "Walk forest classifier"

    classifier_name = "walk_forest"

    gene2gene = InputBlockField(name="gene2gene", order_num=30,
                                required_data_type="BinaryInteraction",
                                required=True)
    miRNA2gene = InputBlockField(name="miRNA2gene", order_num=40,
                                 required_data_type="BinaryInteraction",
                                 required=True)

    walk_max_length = ParamField(
        name="walk_max_length",
        title="walk_max_length",
        input_type=InputType.TEXT,
        field_type=FieldType.INT,
        init_val="10",
        order_num=41
    )

    eps = ParamField(
        name="eps",
        title="Eps",
        input_type=InputType.TEXT,
        field_type=FieldType.FLOAT,
        init_val="0.1",
        order_num=50
    )

    n_estimators = ParamField(
        name="n_estimators",
        title="n_estimators",
        input_type=InputType.TEXT,
        field_type=FieldType.INT,
        init_val="1000",
        order_num=60
    )

    max_features = ParamField(
        name="max_features",
        title="max_features",
        input_type=InputType.TEXT,
        field_type=FieldType.INT,
        init_val="100",
        order_num=70
    )

    max_depth = ParamField(
        name="max_depth",
        title="max_depth",
        input_type=InputType.TEXT,
        field_type=FieldType.INT,
        init_val="2",
        order_num=80
    )

    min_samples_leaf = ParamField(
        name="min_samples_leaf",
        title="min_samples_leaf",
        input_type=InputType.TEXT,
        field_type=FieldType.INT,
        init_val="2",
        order_num=90
    )

    bootstrap = ParamField(
        name="bootstrap",
        title="bootstrap",
        input_type=InputType.CHECKBOX,
        field_type=FieldType.BOOLEAN,
        required=False,
        order_num=100
    )

    def collect_options(self):
        self.classifier_options["gene2gene"] = self.get_input_var("gene2gene")
        self.classifier_options["miRNA2gene"] = self.get_input_var("miRNA2gene")
        self.classifier_options['walk_lengths'] = range(1, int(self.walk_max_length))
        self.collect_option_safe("eps")
        self.collect_option_safe("n_estimators")
        self.collect_option_safe("max_features")
        self.collect_option_safe("max_depth")
        self.collect_option_safe("min_samples_leaf")
        self.classifier_options["bootstrap"] = self.bootstrap