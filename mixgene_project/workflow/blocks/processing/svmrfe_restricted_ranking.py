from workflow.blocks.processing.generic_ranking import GenericRankingBlock

__author__ = 'pavel'


class SvmrfeRestrictedRanking(GenericRankingBlock):
    block_base_name = "RESTR_SVMRFE_RANK"
    name = "Restricted SVMRFE ranking"

    def __init__(self, *args, **kwargs):
        super(SvmrfeRestrictedRanking, self).__init__(*args, **kwargs)
        self.ranking_name = "RestrictedSVMRFE"
        self.result.headers = ["rank"]

    def collect_options(self):
        super(SvmrfeRestrictedRanking, self).collect_options()
        if hasattr(self, "best"):
            try:
                best = int(self.best)
                if best > 0:
                    self.ranking_options["best"] = best
            except:
                pass