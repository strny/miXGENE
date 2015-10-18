__author__ = 'pavel'

from .generic_classifier import GenericClassifier
from workflow.blocks.fields import FieldType, BlockField, OutputBlockField, InputBlockField, InputType, ParamField, \
    ActionRecord, ActionsList


class LinearSVM(GenericClassifier):
    block_base_name = "LIN_SVM"
    name = "Linear SVM"

    classifier_name = "linear_svm"

    C = ParamField(name="C", title="Penalty", order_num=10,
                   input_type=InputType.TEXT, field_type=FieldType.FLOAT, init_val=1.0)

    tol = ParamField(name="tol", order_num=20,
                 title="Tolerance for stopping criteria",
                 input_type=InputType.TEXT, field_type=FieldType.FLOAT, init_val=0.0001)

    loss = ParamField(
        name="loss", order_num=30,
        title="The loss function",
        input_type=InputType.SELECT, field_type=FieldType.STR,
        options={
            "inline_select_provider": True,
            "select_options": [
                ["l1", "Hinge loss"],
                ["l2", "Squared hinge loss"],
            ]
        }
    )

    def collect_options(self):
        self.collect_option_safe("C", float)
        self.collect_option_safe("tol", float)
        self.collect_option_safe("loss", str)