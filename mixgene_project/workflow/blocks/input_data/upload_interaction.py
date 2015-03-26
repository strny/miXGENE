import pandas as pd
from environment.structures import BinaryInteraction
from workflow.blocks.blocks_pallet import GroupType
from workflow.blocks.fields import ActionsList, ActionRecord, ParamField, InputType, FieldType, OutputBlockField
from workflow.blocks.generic import GenericBlock

__author__ = 'pavel'


class UploadInteraction(GenericBlock):
    block_base_name = "GENE_INTERACTION"
    block_group = GroupType.INPUT_DATA
    name = "Upload gene interaction"

    _block_actions = ActionsList([
        ActionRecord("save_params", ["created", "valid_params", "done", "ready"], "validating_params",
                     user_title="Save parameters"),
        ActionRecord("on_params_is_valid", ["validating_params"], "done"),
        ActionRecord("on_params_not_valid", ["validating_params"], "created"),
    ])

    upload_interaction = ParamField("upload_interaction", title="Interaction matrix", order_num=10,
        input_type=InputType.FILE_INPUT, field_type=FieldType.CUSTOM)
    row_units = ParamField("row_units", title="Row units",
        order_num=11, input_type=InputType.TEXT, field_type=FieldType.STR, required=False)
    col_units = ParamField("col_units", title="Column units",
                           order_num=12, input_type=InputType.TEXT, field_type=FieldType.STR, required=False)
    header = ParamField("header", title="Header",
                           order_num=13, input_type=InputType.CHECKBOX, field_type=FieldType.BOOLEAN, required=False)

    bi_data_type = ParamField(
        "bi_data_type", title="Data type", order_num=40,
        input_type=InputType.SELECT, field_type=FieldType.STR,
        init_val="matrix",
        options={
            "inline_select_provider": True,
            "select_options": [
                ["matrix", "Matrix"],
                ["pairs", "Pairs"],
                ["pairs_diff", "Pairs - different units in interaction"],
                ["triples", "Triples with values"],
                ["triples_diff", "Triples with values - different units in interaction"]
            ]
        }
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
    _interaction = OutputBlockField(name="interaction", provided_data_type="BinaryInteraction")

    def on_params_is_valid(self, exp, *args, **kwargs):
        # Convert to  BinaryInteraction
        sep = getattr(self, "csv_sep", " ")
        if self.header:
            _header = 0
        else:
            _header = None
        interaction_df = self.upload_interaction.get_as_data_frame(sep=sep, header=_header)
        sd = None
        if self.bi_data_type in ["pairs", "triples", "pairs_diff", "triples_diff"]:
            # we have to find a shape of interaction matrix
            if self.bi_data_type in ["pairs", "triples"]:
                features = list(set(interaction_df[interaction_df.columns[0]].tolist() + interaction_df[interaction_df.columns[1]].tolist()))
                sd = pd.DataFrame(index=features, columns=features).to_sparse(fill_value=0)
            else:
                features_1 = list(set(interaction_df[interaction_df.columns[0]].tolist()))
                features_2 = list(set(interaction_df[interaction_df.columns[1]].tolist()))
                sd = pd.DataFrame(index=features_1, columns=features_2).to_sparse(fill_value=0)
            # optimization
            if self.bi_data_type in ["pairs", "pairs_diff"]:
                for index, cols in interaction_df.iterrows():
                    sd[cols[1]][cols[0]] = 1
            else:
                for index, cols in interaction_df.iterrows():
                    sd[cols[1]][cols[0]] = cols[3]
            sd = sd.to_dense()
            sd.reset_index(level=0, inplace=True)
            # interaction_df = sd

        interaction = BinaryInteraction(exp.get_data_folder(), str(self.uuid))
        if self.bi_data_type in ["pairs", "triples", "pairs_diff", "triples_diff"]:
            interaction.store_pairs(interaction_df)
            interaction.store_matrix(sd)
        else:
            interaction.store_matrix(interaction_df)
            # todo convert to pairs

        interaction.row_units = self.row_units
        interaction.col_units = self.col_units
        interaction.header = self.header

        self.set_out_var("interaction", interaction)
        exp.store_block(self)