__author__ = 'pavel'

from webapp.tasks import wrapper_task
from workflow.blocks.blocks_pallet import GroupType
from workflow.blocks.fields import ActionsList, ActionRecord, InputBlockField, BlockField, FieldType, ParamField, \
    InputType, OutputBlockField
from workflow.blocks.generic import GenericBlock, execute_block_actions_list
from operator import ge, gt, lt, le
from django.conf import settings


def cmp_func(direction):
    if direction == "<":
        return lt
    elif direction == "<=":
        return le
    elif direction == ">=":
        return ge
    elif direction == ">":
        return gt


def feature_selection_by_cut(
        exp, block,
        src_es, base_filename,
        rank_table,
        cut_property, threshold, cut_direction
):
    """
        @type src_es: ExpressionSet
        @type rank_table: TableResult

        @param cut_direction: either {"<", "<=", ">=", ">"}
    """
    if settings.CELERY_DEBUG:
        import sys
        sys.path.append('/Migration/skola/phd/projects/miXGENE/mixgene_project/wrappers/pycharm-debug.egg')
        import pydevd
        pydevd.settrace('localhost', port=6901, stdoutToServer=True, stderrToServer=True)

    df = src_es.get_assay_data_frame()
    es = src_es.clone(base_filename)
    es.store_pheno_data_frame(src_es.get_pheno_data_frame())

    rank_df = rank_table.get_table()

    selection = rank_df[cut_property]
    mask = cmp_func(cut_direction)(selection, threshold)
    new_df = df[list(mask.select(lambda x: mask[x]).index)]

    es.store_assay_data_frame(new_df)

    return [es], {}


class FeatureSelectionByCut(GenericBlock):
    block_base_name = "FS_BY_CUT"
    block_group = GroupType.FILTER
    name = "Feature Selection by Ranking"

    is_block_supports_auto_execution = True

    _block_actions = ActionsList([
        ActionRecord("save_params", ["created", "valid_params", "done", "ready"], "validating_params",
                     user_title="Save parameters"),
        ActionRecord("on_params_is_valid", ["validating_params"], "ready"),
        ActionRecord("on_params_not_valid", ["validating_params"], "created"),
    ])
    _block_actions.extend(execute_block_actions_list)

    _es = InputBlockField(
        name="es", order_num=10,
        required_data_type="ExpressionSet", required=True
    )

    _rank_table = InputBlockField(
        name="rank_table", order_num=20,
        required_data_type="TableResult", required=True
    )

    _cut_property_options = BlockField(
        name="cut_property_options", field_type=FieldType.RAW, is_a_property=True)
    cut_property = ParamField(
        name="cut_property",
        title="Ranking property to use",
        # input_type=InputType.SELECT,
        input_type=InputType.TEXT,
        field_type=FieldType.STR,
        #select_provider="cut_property_options",
        order_num=10,
    )
    threshold = ParamField(
        name="threshold",
        title="Threshold for cut",
        order_num=20,
        input_type=InputType.TEXT,
        field_type=FieldType.INT,
    )
    _cut_direction_options = BlockField(name="cut_direction_options",
                                        field_type=FieldType.RAW)
    cut_direction_options = ["<", "<=", ">=", ">"]
    cut_direction = ParamField(
        name="cut_direction",
        title="Direction of cut",
        input_type=InputType.SELECT,
        field_type=FieldType.STR,
        select_provider="cut_direction_options",
        order_num=30,
        options={
            "inline_select_provider": True,
            "select_options": [
                [op, op] for op in
                ["<", "<=", ">=", ">"]
            ]
        }
    )

    es = OutputBlockField(name="es", provided_data_type="ExpressionSet")

    def __init__(self, *args, **kwargs):
        super(FeatureSelectionByCut, self).__init__(*args, **kwargs)
        self.celery_task = None

    @property
    def cut_property_options(self):
        # import ipdb; ipdb.set_trace()
        rank_table = self.get_input_var("rank_table")
        if rank_table and hasattr(rank_table, "headers"):
            return [
                {"pk": header, "str": header}
                for header in rank_table.headers
            ]

    def execute(self, exp, *args, **kwargs):
        self.clean_errors()
        self.celery_task = wrapper_task.s(
            feature_selection_by_cut,
            exp=exp, block=self,
            src_es=self.get_input_var("es"),
            rank_table=self.get_input_var("rank_table"),
            cut_property=self.cut_property,
            threshold=self.threshold,
            cut_direction=self.cut_direction,
            base_filename="%s_feature_selection" % self.uuid,
        )
        exp.store_block(self)
        self.celery_task.apply_async()

    def success(self, exp, es):
        self.set_out_var("es", es)
        exp.store_block(self)