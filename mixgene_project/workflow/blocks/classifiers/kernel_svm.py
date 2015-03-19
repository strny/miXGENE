__author__ = 'pavel'


class KernelSvm(GenericClassifier):
    block_base_name = "KERNEL_SVM"
    name = "Kernel SVM Classifier"

    classifier_name = "svm"

    C = ParamField(name="C", title="Penalty", order_num=10,
                   input_type=InputType.TEXT, field_type=FieldType.FLOAT, init_val=1.0)

    kernel = ParamField(
        name="kernel", order_num=20,
        title="Kernel type",
        input_type=InputType.SELECT, field_type=FieldType.STR,
        init_val="rbf",
        options={
            "inline_select_provider": True,
            "select_options": [
                ["linear", "Linear"],
                ["poly", "Polynomial"],
                ["rbf", "RBF"],
                ["sigmoid", "Sigmoid"],
            ]
        }
    )
    degree = ParamField(
        name="degree", order_num=21,
        title="Degree of the polynomial kernel",
        input_type=InputType.TEXT, field_type=FieldType.INT
    )

    gamma = ParamField(
        name="gamma", order_num=22,
        title="Kernel coefficient for RBF, Polynomial and Sigmoid",
        input_type=InputType.TEXT, field_type=FieldType.FLOAT
    )

    tol = ParamField(name="tol", order_num=30,
                     title="Tolerance for stopping criteria",
                     input_type=InputType.TEXT, field_type=FieldType.FLOAT, init_val=0.001)

    def collect_options(self):
        self.collect_option_safe("C", float)
        self.collect_option_safe("kernel", str)
        self.collect_option_safe("degree", int)
        self.collect_option_safe("gamma", float)
        self.collect_option_safe("tol", float)