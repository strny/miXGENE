from workflow.blocks.processing.generic_ranking import GenericRankingBlock

__author__ = 'pavel'


class SvmrfeRanking(GenericRankingBlock):
    block_base_name = "SVMRFE_RANK"
    name = "SVMRFE ranking"

    def __init__(self, *args, **kwargs):
        super(SvmrfeRanking, self).__init__(*args, **kwargs)
        self.ranking_name = "SVMRFE"
        self.result.headers = ["rank"]