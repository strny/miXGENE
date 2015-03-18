# -*- coding: utf-8 -*-

import json
import logging

from environment.structures import ExpressionSet
from workflow.blocks.fields import MultiUploadField, FieldType, BlockField, InnerOutputField, \
    InputType, ParamField, ActionRecord, ActionsList
from workflow.blocks.meta.meta_block import UniformMetaBlock


log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

class DataInfo(object):
    def __init__(self, label):
        self.label = label
        self.from_index = None
        self.to_index = None


    def set_indices(self, from_index, to_index):
        self.from_index = from_index
        self.to_index = to_index

    def to_dict(self, *args, **kwargs):
        return {
            "label": self.label,
            "from_index": self.from_index,
            "to_index": self.to_index
        }

    def __hash__(self):
        return hash(self.label)

    def __eq__(self, other):
        if not isinstance(other, DataInfo):
            return False
        if other.label == self.label:
            return True

        return False


class DataInfoList(object):
    def __init__(self):
        self.cells = []

    def remove_by_label(self, label):
        self.cells.remove(DataInfo(label))

    def find_by_label(self, label):
        for cell in self.cells:
            if cell.label == label:
                return cell

    def to_dict(self, *args, **kwargs):
        return {
            "dict": {cell.label: cell.to_dict() for cell in self.cells},
            "list": [cell.to_dict() for cell in self.cells]
        }

class MassUpload(UniformMetaBlock):
    block_base_name = "BunchUpload"
    name = "Mass upload expression sets"

    _bu_block_actions = ActionsList([

        ActionRecord("process_upload", ["valid_params", "processing_upload"],
                     "processing_upload", "Process uploaded data"),

        ActionRecord("error_on_processing", ["processing_upload"], "valid_params"),
        ActionRecord("processing_done", ["processing_upload"], "ready")

        # ActionRecord("success", ["processing_upload"], "done", reload_block_in_client=True),
        # ActionRecord("error", ["processing_upload"], "valid_params"),
    ])

    es_matrices = ParamField(
        "es_matrices", title="Expression sets", order_num=10,
        input_type=InputType.FILE_INPUT, field_type=FieldType.CUSTOM,
        options={"multiple": True},
    )

    es_matrices_ori = ParamField(
        "es_matrices_ori", title="Matrices orientation", order_num=11,
        input_type=InputType.SELECT, field_type=FieldType.STR,
        init_val="SxG",
        options={
            "inline_select_provider": True,
            "select_options": [
                ["SxG", "Samples x Features"],
                ["GxS", "Features x Samples"]
            ]
        }
    )

    pheno_matrices = ParamField(
        "pheno_matrices", title="Phenotypes", order_num=40,
        input_type=InputType.FILE_INPUT, field_type=FieldType.CUSTOM,
        options={"multiple": True},
    )

    csv_sep = ParamField(
        "csv_sep", title="CSV separator symbol", order_num=50,
        input_type=InputType.SELECT, field_type=FieldType.STR, init_val=",",
        options={
            "inline_select_provider": True,
            "select_options": [
                [" ", "space ( )"],
                [",", "comma  (,)"],
                ["\t", "tab (\\t)"],
                [";", "semicolon (;)"],
                [":", "colon (:)"],
            ]
        }
    )

    cells = BlockField(name="cells", field_type=FieldType.CUSTOM, init_val=None)

    elements = BlockField(name="elements", field_type=FieldType.SIMPLE_LIST, init_val=[
        "mass_upload/data_spec.html"
    ])


    def __init__(self, *args, **kwargs):
        super(MassUpload, self).__init__(*args, **kwargs)
        self.es_matrices = MultiUploadField()
        self.pheno_matrices = MultiUploadField()

        self.pheno_by_es_names = {}
        self.labels = []
        self.seq = []
        self.cells = DataInfoList()
        self.register_inner_output_variables([InnerOutputField(
            name="es",
            provided_data_type="ExpressionSet"
        )])

    @property
    def is_sub_pages_visible(self):
        if self.state in ['source_was_preprocessed', 'sample_classes_assigned', 'ready', 'done']:
            return True
        return False


    def add_cell(self, exp, received_block, *args, **kwargs):
        new_cell_dict = received_block.get("cells", {}).get("new")
        if new_cell_dict:
            cell = DataInfo(new_cell_dict["label"])
            self.cells.cells.append(cell)
            exp.store_block(self)

    def remove_cell(self, exp, cell_json, *args, **kwargs):
        try:
            cell = json.loads(cell_json)
            self.cells.remove_by_label(cell["label"])
            exp.store_block(self)
        except:
            pass

    def save_cell(self, exp, cell_json, *args, **kwargs):
        try:
            cell = json.loads(cell_json)
            f = self.cells.find_by_label(cell["label"])
            f.set_indices(int(cell["from_index"]), int(cell["to_index"]))
            exp.store_block(self)
        except:
            pass

    def get_fold_labels(self):
        return self.labels

    def error_on_processing(self, *args, **kwargs):
        pass

    def processing_done(self, *args, **kwargs):
        pass

    def process_upload(self, exp, *args, **kwargs):
        """
            @param exp: Experiment
        """
        # TODO: move to celery
        self.clean_errors()
        seq = []
        sep = getattr(self, "csv_sep", " ")
        try:
            if len(self.pheno_matrices) != len(self.es_matrices):
                raise RuntimeError("Different number of phenotypes and expression sets")

            self.labels = es_matrix_names = sorted(self.es_matrices)
            pheno_matrix_names = sorted(self.pheno_matrices)
            self.pheno_by_es_names = {
                es_name: pheno_name for
                es_name, pheno_name
                in zip(es_matrix_names, pheno_matrix_names)
            }
            for es_name, pheno_name in self.pheno_by_es_names.iteritems():
                es_ufw = self.es_matrices[es_name]
                es_df = es_ufw.get_as_data_frame(sep)

                pheno_ufw = self.pheno_matrices[pheno_name]
                pheno_df = pheno_ufw.get_as_data_frame(sep)

                if self.es_matrices_ori == "GxS":
                    es_df = es_df.T
                es_df.set_index(es_df.columns[0], inplace=True)
                pheno_df.set_index(pheno_df.columns[0], inplace=True)
                es_sample_names = sorted(es_df.index.tolist())
                pheno_sample_names = sorted(pheno_df.index.tolist())
                if es_sample_names != pheno_sample_names:
                    raise RuntimeError("Couldn't match `%s` and `%s` due to "
                                       "different sample name sets" % (es_name, pheno_name))

                es = ExpressionSet(
                    base_dir=exp.get_data_folder(),
                    base_filename="%s_%s" % (self.uuid, es_name)
                )

                es.store_assay_data_frame(es_df)
                es.store_pheno_data_frame(pheno_df)
                for cell in self.cells.cells:
                    es.assay_metadata[cell.label] = {"from_index": cell.from_index,
                                                     "to_index": cell.to_index}
                es.pheno_metadata["user_class_title"] = pheno_df.columns[0]
                seq.append({"es": es, "__label__": es_name})

            self.seq = seq
            exp.store_block(self)
            self.do_action("processing_done", exp, seq)
        except Exception as e:
            log.exception(e)
            self.errors.append(e)
            self.do_action("error_on_processing", exp, e)
            # self.celery_task_fetch.apply_async()

    def execute(self, exp, *args, **kwargs):
        self.inner_output_manager.reset()
        self.do_action("on_folds_generation_success", exp, self.seq)

    # def success(self, exp, *args, **kwargs):
    #     pass