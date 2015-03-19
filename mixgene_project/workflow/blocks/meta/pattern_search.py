import logging

from workflow.blocks.fields import FieldType, InnerOutputField, InputBlockField, InputType, \
    ParamField, ActionRecord, ActionsList
from workflow.blocks.meta.meta_block import UniformMetaBlock


log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)



class PatternSearch(UniformMetaBlock):
    block_base_name = "PATTERN_SEARCH"
    name = "Pattern Search"

    _cv_actions = ActionsList([
        ActionRecord("become_ready", ["valid_params"], "ready")
    ])

    mRNA = InputBlockField(name="mRNA", order_num=10,
                           required_data_type="ExpressionSet",
                           required=True)
    miRNA = InputBlockField(name="miRNA", order_num=20,
                            required_data_type="ExpressionSet",
                            required=True)

    gene2gene = InputBlockField(name="gene2gene", order_num=30,
                                required_data_type="BinaryInteraction",
                                required=True)
    miRNA2gene = InputBlockField(name="miRNA2gene", order_num=40,
                                 required_data_type="BinaryInteraction",
                                 required=True)

    initial_seed = ParamField(name="initial_seed", order_num=50, title="seed", input_type=InputType.TEXT, field_type=FieldType.STR,
                      init_val="")

    radius = ParamField(name="radius", order_num=60, title="radius", input_type=InputType.TEXT, field_type=FieldType.INT,
                      init_val=4)

    width = ParamField(name="width", order_num=60, title="width", input_type=InputType.TEXT, field_type=FieldType.INT,
                      init_val=3)

    # _seed = InnerOutputField(name="seed", provided_data_type="GeneSets")

    def add_dyn_input_hook(self, exp, dyn_port, new_port):
        """
            @type new_port: InputBlockField
        """
        new_inner_output_seed = InnerOutputField(
            name="%s_seed_i" % new_port.name,
            provided_data_type=new_port.required_data_type
        )
        self.inner_output_es_names_map[new_port.name] = \
            new_inner_output_seed.name

        self.register_inner_output_variables([new_inner_output_seed])

    def execute(self, exp, *args, **kwargs):
        self.clean_errors()

        #
        # self.inner_output_manager.reset()
        # es_dict = {
        #     inp_name: self.get_input_var(inp_name)
        #     for inp_name in self.es_inputs
        # }
        #
        # self.celery_task = wrapper_task.s(
        #     generate_cv_folds,
        #     exp, self,
        #     folds_num=self.folds_num,
        #     repeats_num=self.repeats_num,
        #     es_dict=es_dict,
        #     inner_output_es_names_map=self.inner_output_es_names_map,
        #     success_action="on_folds_generation_success",
        # )
        # exp.store_block(self)
        # self.celery_task.apply_async()

    def mergeSamples(mRNA, miRNA):
        """
        :param mRNA:
        :param miRNA:
        :return:
        """
        mRNA = mRNA.drop('class', 1)
        miRNA = miRNA.drop('class', 1)
        return mRNA.join(miRNA)


    def on_params_is_valid(self, exp, *args, **kwargs):
        super(PatternSearch, self).on_params_is_valid(exp, *args, **kwargs)
        _mRNA = self.get_input_var("mRNA")
        _miRNA = self.get_input_var("miRNA")
        _g2g = self.get_input_var("gene2gene")
        _mi2g = self.get_input_var("miRNA2gene")
        n_mRNA_miRNA = _mRNA.clone("p_s_new_mRNA_miRNA", clone_data_frames=True)
        df1 = _mRNA.get_assay_data_frame()
        df2 = _miRNA.get_assay_data_frame()
        n_mRNA_miRNA.store_assay_data_frame(self.mergeSamples(df1, df2))
        self.do_action("become_ready", exp)

    def become_ready(self, *args, **kwargs):
        pass

    def __init__(self, *args, **kwargs):
        super(PatternSearch, self).__init__(*args, **kwargs)
        self.register_inner_output_variables([InnerOutputField(
            name="seed",
            provided_data_type="GeneSets"
        )])
        self.register_inner_output_variables([InnerOutputField(
            name="mRNA_miRNA",
            provided_data_type="ExpressionSet"
        )])

