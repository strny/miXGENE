from workflow.blocks.processing.generic_ranking import GenericRankingBlock

__author__ = 'pavel'


class RandomRanking(GenericRankingBlock):
    block_base_name = "RANDOM_RANK"
    name = "Random ranking"

    def __init__(self, *args, **kwargs):
        super(RandomRanking, self).__init__(*args, **kwargs)
        self.ranking_name = "RandomRanking"
        self.result.headers = ["rank"]

    def collect_options(self):
        super(RandomRanking, self).collect_options()
        if hasattr(self, "best"):
            try:
                best = int(self.best)
                if best > 0:
                    self.ranking_options["best"] = best
            except:
                pass