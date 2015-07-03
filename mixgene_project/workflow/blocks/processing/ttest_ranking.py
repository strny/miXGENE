from workflow.blocks.processing.generic_ranking import GenericRankingBlock

__author__ = 'pavel'


class TTestRanking(GenericRankingBlock):
    block_base_name = "TTEST_RANK"
    name = "TTest ranking"

    def __init__(self, *args, **kwargs):
        super(TTestRanking, self).__init__(*args, **kwargs)
        self.ranking_name = "TTestRanking"
        self.result.headers = ["rank"]

    def collect_options(self):
        super(TTestRanking, self).collect_options()
        if hasattr(self, "best"):
            try:
                best = int(self.best)
                if best > 0:
                    self.ranking_options["best"] = best
            except:
                pass