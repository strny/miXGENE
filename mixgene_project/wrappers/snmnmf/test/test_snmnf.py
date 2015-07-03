__author__ = 'pavel'

import unittest
import mixgene_project.wrappers.snmnmf.nimfa_snmnmf as ns
import mixgene_project.wrappers.snmnmf.snmnmf as snmnmf
from mixgene_project.wrappers.snmnmf.evaluation import EnrichmentInGeneSets
import operator


class SNMNMFTestCase(unittest.TestCase):
    def test_snmnmf(self):
                #import scipy  as sp
        #import numpy as np
        #from pandas import DataFrame, Series
        ### get testing data ###
        m_rna, mi_rna, m2g_intction, pp_intction, bpGO = snmnmf.loadData(full = False)

        ### factorization ###
        # initialize the factorization
        snm = ns.NIMFA_SNMNMF(mRNA = m_rna, miRNA = mi_rna, DNAmethyl = None, gene2gene = pp_intction\
        , miRNA2gene = m2g_intction, gene2DNAmethylation = None, params={'l1':0.1,'l2':0.1,'g1':0.1,'g2':0.1})
        # run factorization
        snm.run(seed = "random_c", rank = 50, max_iter = 5)
        # get factorization performance evaluation
        snm.performance.getResults()

        ### Results evaluation ###
        e = EnrichmentInGeneSets(snm)
        # get co-modules
        i = e.getGeneSets(T=1)
        ## compute enrichment in GO terms ()
        enrich_bpGO = e.getEnrichmentInGeneSets(bpGO, T = 0.1)
        # sort resultst accodring p-values
        sorted_enrich_bpGO = sorted(enrich_bpGO.iteritems(), key=operator.itemgetter(1))
        # print results
        for key in sorted_enrich_bpGO:
            print key[0] +"\t:\t" + str(key[1])
        ## compute enrichment ratio for different
        er_ratio = [e.getEnrichmentRatioInGeneSets(bpGO, T = 0.1, enrichment_threshold = 0.05, N = 100) \
         for T in [0.1, 0.2, 0.5, 0.8, 1, 2, 5]]



if __name__ == '__main__':
    unittest.main()
