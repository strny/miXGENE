# -*- coding: utf-8 -*-
"""
Created on Thu Jul 10 10:59:34 2014

@author: holecm
"""


from .. import nimfa_snmnmf as ns
import snmnmf
from evaluation import EnrichmentInGeneSets
import operator

if __name__ == "__main__":
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



    ## vyber nahodna data
    #import random
    #from scipy.sparse import csr_matrix
    #import nimfa
    #
    #random.sample(set([1, 2, 3, 4, 5, 6]), 2)
    #
    #
    ##### NAHODNA DATA
    #
    ## miRNA
    #V = csr_matrix((np.array([1,2,3,4,5,6]), np.array([0,2,2,0,1,2]), np.array([0,2,3,6])), shape=(3,3))
    #V = V.todense()
    #
    ## mRNA
    #V1=  np.array([[ 0,  1,  2,  3,  4],
    #               [ 5,  6,  7,  8,  9],
    #               [10, 11, 12, 13, 14]])
    #
    ## gene 2 gene
    #A = abs(sp.sparse.rand(V1.shape[1], V1.shape[1], density = 0.7, format = 'csr')).todense()
    ##  miRNA 2 gene
    #B = abs(sp.sparse.rand(V.shape[1], V1.shape[1], density = 0.7, format = 'csr')).todense()
    #
    #### RUN FACTORIZATION WITH RANDOM DATA
    #snm = ns.NIMFA_SNMNMF(mRNA = DataFrame(V1), miRNA = DataFrame(V), DNAmethyl = DataFrame(None), gene2gene = DataFrame(A)\
    #, miRNA2gene = DataFrame(B), gene2DNAmethylation = None, params={'l1':0.1,'l2':0.1,'g1':0.1,'g2':0.1})
    #snm.run(seed = "random_c", rank = 2, max_iter = 5)
    #snm.performance.getResults()
    #
    ##### NAHODNA DATA + missing values
    #
    ## miRNA
    #V = csr_matrix((np.array([1,2,3,4,5,6]), np.array([0,2,2,0,1,2]), np.array([0,2,3,6])), shape=(3,3)).todense()
    #
    ## mRNA
    #V1=  np.array([[ np.nan  ,  1,  2,  3,  4],
    #               [ 5,  6,  7,  8,  9],
    #               [10, 11, 12, 13, 14]])
    #
    #
    #
    ## gene 2 gene
    #A = abs(sp.sparse.rand(V1.shape[1], V1.shape[1], density = 0.7, format = 'csr')).todense()
    ##  miRNA 2 gene
    #B = abs(sp.sparse.rand(V.shape[1], V1.shape[1], density = 0.7, format = 'csr')).todense()
    #
    ## A[0,0]=np.nan
    #
    #### RUN FACTORIZATION with MISSING DATA
    #snm = ns.NIMFA_SNMNMF(mRNA = DataFrame(V1), miRNA = DataFrame(V), DNAmethyl = DataFrame(None), gene2gene = DataFrame(A)\
    #, miRNA2gene = DataFrame(B), gene2DNAmethylation = None, params={'l1':0.1,'l2':0.1,'g1':0.1,'g2':0.1})
    #snm.run(seed = "random_c", rank = 2, max_iter = 5)
    #snm.performance.getResults()
    #
    #
    #### RUN FACTORIZATION WITH NO DATA
    #snm = ns.NIMFA_SNMNMF(mRNA = DataFrame(None), miRNA = DataFrame(None), DNAmethyl = DataFrame(None), gene2gene = DataFrame(A)\
    #, miRNA2gene = DataFrame(B), gene2DNAmethylation = None, params={'l1':0.1,'l2':0.1,'g1':0.1,'g2':0.1})
    #snm.run(seed = "random_c", rank = 2, max_iter = 5)
    #snm.performance.getResults()
    #
    #
    ##TODO: experimenty s prazdnymi genesety
    #
    #
    #
    ##TODO: vadne identifikatory
    #
