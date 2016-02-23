from workflow.blocks.blocks_pallet import GroupType
from workflow.blocks.generic import GenericBlock, save_params_actions_list, execute_block_actions_list
from wrappers.sk_classifiers import apply_ncf_classifier

__author__ = 'pavel'

from workflow.blocks.fields import InputBlockField, ParamField, InputType, FieldType, ActionsList, OutputBlockField
from webapp.tasks import wrapper_task

class NCF(GenericBlock):
    block_group = GroupType.CLASSIFIER

    block_base_name = "NCF"
    name = "Network-Constrained Forest"

    classifier_name = "ncf"

    is_abstract = False

    is_block_supports_auto_execution = True

    # Block behavior
    _block_actions = ActionsList([])
    _block_actions.extend(save_params_actions_list)
    _block_actions.extend(execute_block_actions_list)

    gene2gene = InputBlockField(name="gene2gene", order_num=30,
                                required_data_type="BinaryInteraction",
                                required=True)
    miRNA2gene = InputBlockField(name="miRNA2gene", order_num=31,
                                 required_data_type="BinaryInteraction",
                                 required=True)

    # User defined parameters
    # Input ports definition
    _m_train_es = InputBlockField(name="mRNA_train_es", order_num=10,
                                  required_data_type="ExpressionSet",
                                  required=True)
    _m_test_es = InputBlockField(name="mRNA_test_es", order_num=20,
                                 required_data_type="ExpressionSet",
                                 required=True)
    _mi_train_es = InputBlockField(name="miRNA_train_es", order_num=21,
                                   required_data_type="ExpressionSet",
                                   required=True)
    _mi_test_es = InputBlockField(name="miRNA_test_es", order_num=22,
                                  required_data_type="ExpressionSet",
                                  required=True)


    # Provided outputs
    _result = OutputBlockField(name="result", field_type=FieldType.CUSTOM,
                               provided_data_type="ClassifierResult", init_val=None)

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

    def __init__(self, *args, **kwargs):
        super(NCF, self).__init__(*args, **kwargs)

        self.celery_task = None
        self.classifier_options = {}
        self.fit_options = {}

    def execute(self, exp, *args, **kwargs):
        self.set_out_var("result", None)
        self.collect_options()

        mRNA_train_es = self.get_input_var("mRNA_train_es")
        mRNA_test_es = self.get_input_var("mRNA_test_es")

        miRNA_train_es = self.get_input_var("miRNA_train_es")
        miRNA_test_es = self.get_input_var("miRNA_test_es")

        self.celery_task = wrapper_task.s(
            apply_ncf_classifier,
            exp=exp, block=self,

            mRNA_train_es=mRNA_train_es, mRNA_test_es=mRNA_test_es,
            miRNA_train_es=miRNA_train_es, miRNA_test_es=miRNA_test_es,

            classifier_name=self.classifier_name,
            classifier_options=self.classifier_options,
            fit_options=self.fit_options,

            base_folder=exp.get_data_folder(),
            base_filename="%s_%s" % (self.uuid, self.classifier_name),
        )
        exp.store_block(self)
        self.celery_task.apply_async()

    def success(self, exp, result, *args, **kwargs):
        # We store obtained result as an output variable
        self.set_out_var("result", result)
        exp.store_block(self)

    def reset_execution(self, exp, *args, **kwargs):
        self.clean_errors()
        # self.get_scope().remove_temp_vars()
        self.set_out_var("result", None)
        exp.store_block(self)

    def get_option_safe(self, name, target_type=None):
        if hasattr(self, name):
            raw = getattr(self, name)
            if raw:
                if target_type:
                    try:
                        return target_type(raw)
                    except:
                        pass
                else:
                    return raw
        return None

    def collect_option_safe(self, name, target_type=None, target_name=None):
        value = self.get_option_safe(name, target_type)
        # from celery.contrib import rdb; rdb.set_trace()
        if value:
            if target_name:
                self.classifier_options[target_name] = value
            else:
                self.classifier_options[name] = value
        return value

    def collect_options(self):
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
