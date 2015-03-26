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
    miRNA2gene = InputBlockField(name="miRNA2gene", order_num=31,
                                 required_data_type="BinaryInteraction",
                                 required=True)

    upload_gene2gene_platform = ParamField("upload_gene2gene_platform", title="PPI platform", order_num=32,
                                           input_type=InputType.FILE_INPUT, field_type=FieldType.CUSTOM)

    upload_mirna_platform = ParamField("upload_mirna_platform", title="miRNA platform", order_num=33,
                                       input_type=InputType.FILE_INPUT, field_type=FieldType.CUSTOM)

    n_estimators = ParamField(
        name="n_estimators",
        title="The number of trees in the forest",
        input_type=InputType.TEXT,
        field_type=FieldType.INT,
        init_val="1000",
        order_num=41
    )

    walk_max_length = ParamField(
        name="walk_max_length",
        title="Walk max length",
        input_type=InputType.TEXT,
        field_type=FieldType.INT,
        init_val="10",
        order_num=50
    )

    criterion = ParamField(
        name="criterion",
        title="The function to measure the quality of a split",
        input_type=InputType.SELECT,
        field_type=FieldType.STR,
        order_num=60,
        options={
            "inline_select_provider": True,
            "select_options": [
                ["gini", "Gini impurity"],
                ["entropy", "Information gain"]
            ]
        }
    )

    eps = ParamField(
        name="eps",
        title="Eps",
        input_type=InputType.TEXT,
        field_type=FieldType.FLOAT,
        init_val="0.01",
        order_num=70
    )


    # max_features = ParamField(
    #     name="max_features",
    #     title="max_features",
    #     input_type=InputType.TEXT,
    #     field_type=FieldType.INT,
    #     init_val="100",
    #     order_num=70
    # )

    max_depth = ParamField(
        name="max_depth",
        title="The maximum depth of the tree",
        input_type=InputType.TEXT,
        field_type=FieldType.INT,
        init_val="2",
        order_num=80
    )

    min_samples_split = ParamField(
        name="min_samples_split",
        title="The minimum number of samples to split an internal node",
        input_type=InputType.TEXT,
        field_type=FieldType.INT,
        init_val="2",
        order_num=90,
    )

    min_samples_leaf = ParamField(
        name="min_samples_leaf",
        title="The minimum number of samples to be at a leaf node",
        input_type=InputType.TEXT,
        field_type=FieldType.INT,
        init_val="2",
        order_num=100
    )

    bootstrap = ParamField(
        name="bootstrap",
        title="bootstrap",
        input_type=InputType.CHECKBOX,
        field_type=FieldType.BOOLEAN,
        required=False,
        order_num=110
    )

    def collect_options(self):
        g_p = self.upload_gene2gene_platform.get_file()
        m_p = self.upload_mirna_platform.get_file()
        with open(g_p.path) as f:
            for line in f:
                g_p = line.split(',')
        with open(m_p.path) as f:
            for line in f:
                m_p = line.split(',')

        self.classifier_options["gene_platform"] = g_p
        self.classifier_options["miRNA_platform"] = m_p
        self.classifier_options["gene2gene"] = self.get_input_var("gene2gene")
        self.classifier_options["miRNA2gene"] = self.get_input_var("miRNA2gene")
        self.classifier_options['walk_lengths'] = range(1, int(self.walk_max_length))
        self.collect_option_safe("eps")
        self.collect_option_safe("n_estimators", int)
        # self.collect_option_safe("max_features")
        self.collect_option_safe("max_depth", int)
        self.collect_option_safe("min_samples_leaf", int)
        self.collect_option_safe("min_samples_split", int)
        self.classifier_options["bootstrap"] = self.bootstrap