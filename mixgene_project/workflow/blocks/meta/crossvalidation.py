import logging

from webapp.tasks import wrapper_task
from workflow.blocks.fields import FieldType, BlockField, InnerOutputField, InputBlockField, InputType, \
    ParamField, ActionRecord, ActionsList
from workflow.blocks.meta.meta_block import UniformMetaBlock
from workflow.common_tasks import generate_cv_folds
from environment.result_container import ResultsContainer
from django.conf import settings


# class CrossValidationForm(forms.Form):
#     folds_num = forms.IntegerField(min_value=2, max_value=100)
#     #split_ratio = forms.FloatField(min_value=0, max_value=1)
#

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class CrossValidation(UniformMetaBlock):
    block_base_name = "CROSS_VALID"
    name = "Cross Validation K-fold"

    _cv_actions = ActionsList([
        ActionRecord("become_ready", ["valid_params"], "ready")
    ])
    elements = BlockField(name="elements", field_type=FieldType.SIMPLE_LIST, init_val=[
        "cv_info.html"
    ])

    _input_es_dyn = InputBlockField(
        name="es_inputs", required_data_type="ExpressionSet",
        required=True, multiply_extensible=True,
        order_num=-1
    )

    folds_num = ParamField(name="folds_num", title="Folds number", order_num=10,
                           input_type=InputType.TEXT, field_type=FieldType.INT, init_val=5)
    repeats_num = ParamField(name="repeats_num", title="Repeats number", order_num=20,
                             input_type=InputType.TEXT, field_type=FieldType.INT, init_val=1)

    def get_fold_labels(self):
        out = []
        for repeat in range(self.repeats_num):
            for num in range(self.folds_num):
                out.append("fold_%s_%s" % (repeat + 1, num + 1))
        return out   # ["fold_%s_%s" % (repeat + 1, num + 1) for num in range(self.folds_num) for repeat in range(self.repeats_num)]

    def get_repeat_labels(self):
        return ["repeat_%s" % (repeat + 1) for repeat in range(self.repeats_num)]

    def add_dyn_input_hook(self, exp, dyn_port, new_port):
        """
            @type new_port: InputBlockField
        """
        new_inner_output_train = InnerOutputField(
            name="%s_train_i" % new_port.name,
            provided_data_type=new_port.required_data_type
        )
        new_inner_output_test = InnerOutputField(
            name="%s_test_i" % new_port.name,
            provided_data_type=new_port.required_data_type
        )
        self.inner_output_es_names_map[new_port.name] = \
            (new_inner_output_train.name, new_inner_output_test.name)

        self.register_inner_output_variables([new_inner_output_train, new_inner_output_test])

    def execute(self, exp, *args, **kwargs):
        self.clean_errors()

        self.inner_output_manager.reset()
        es_dict = {
            inp_name: self.get_input_var(inp_name)
            for inp_name in self.es_inputs
        }

        self.celery_task = wrapper_task.s(
            generate_cv_folds,
            exp, self,
            folds_num=self.folds_num,
            repeats_num=self.repeats_num,
            es_dict=es_dict,
            inner_output_es_names_map=self.inner_output_es_names_map,
            success_action="on_folds_generation_success",
        )
        exp.store_block(self)
        self.celery_task.apply_async()

    def on_params_is_valid(self, exp, *args, **kwargs):
        super(CrossValidation, self).on_params_is_valid(exp, *args, **kwargs)
        self.do_action("become_ready", exp)

    def become_ready(self, *args, **kwargs):
        pass

    def build_result_collection(self, exp):
        if settings.CELERY_DEBUG:
            import sys
            sys.path.append('/Migration/skola/phd/projects/miXGENE/mixgene_project/wrappers/pycharm-debug.egg')
            import pydevd
            pydevd.settrace('localhost', port=6901, stdoutToServer=True, stderrToServer=True)

        rc = ResultsContainer(
            base_dir=exp.get_data_folder(),
            base_filename="%s" % self.uuid
        )
        res_seq = self.res_seq


        def create_new_dim_rc(local_rc, axis_meta_block, axis_meta_block_labels):
            local_rc.axis_list = [axis_meta_block]
            local_rc.labels_dict[axis_meta_block] = axis_meta_block_labels
            local_rc.init_ar()
            local_rc.update_label_index()

        # WARNING: We only support homogeneous results, so we only check first element
        res_seq_field_name, data_type = res_seq.fields.iteritems().next()
        if data_type == "ClassifierResult":
            fold_labels = self.get_fold_labels()
            single_rc_list = []
            for field_name in res_seq.fields:
                run_num = 0
                loc_list = []
                for idx, res_seq_cell in enumerate(res_seq.sequence):
                    if (idx % self.folds_num) == 0:
                        rc_run = ResultsContainer("", "")
                        create_new_dim_rc(rc_run, self.base_name + "_folds", ["fold_%s" % fold_num for fold_num in range(self.folds_num)])
                        loc_list.append(rc_run)
                        run_num += 1
                    rc_run.ar[idx % self.folds_num] = res_seq_cell[field_name]
                rc_single = ResultsContainer("", "")
                rc_single.add_dim_layer(loc_list, self.base_name, self.get_repeat_labels())
                single_rc_list.append(rc_single)
            rc.add_dim_layer(single_rc_list, self.collector_spec.label, res_seq.fields.keys())

        elif data_type == "ResultsContainer":
            if len(res_seq.fields) > 1:
                raise Exception("Meta block only support single output of type ResultsContainer")

            else:
                rc_list = []
                for cell in res_seq.sequence:
                    sub_rc = cell[res_seq_field_name]
                    sub_rc.load()
                    rc_list.append(sub_rc)

                rc.add_dim_layer(rc_list, self.base_name, self.get_fold_labels())

        elif data_type == "SequenceContainer":
            # TODO remove this check
            pass
        else:
            raise Exception("Meta blocks only support ClassifierResult "
                            "or ResultsContainer in the output collection. "
                            " Instead got: %s" % data_type)

        rc.store()
        rc.ar = None
        self.set_out_var("results_container", rc)
