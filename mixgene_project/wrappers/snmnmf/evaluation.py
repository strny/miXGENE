# -*- coding: utf-8 -*-
"""
Created on Thu Jul 10 10:59:00 2014

@author: holecm
"""

import scipy.stats  as sp
import numpy as np
from pandas import Series, DataFrame
from operator import or_
import math

class SNMNMNMFEvaluation(object):
    
    snmnmf = None   
    
    def __init__(self, snmnmf):
        self. snmnmf = snmnmf   
    
    def removeTemporaryNegativeFeatures(self, S, indicator_string = 'negative_feature___'):
        """Remove elements starting with the indicator_string and remove possible duplicates."""
        return S.apply(lambda list_element: set([s.replace(indicator_string, '')  for s in list_element]))  
  
class EnrichmentInGeneSets(SNMNMNMFEvaluation):
    """getEnrichmentRatioInGeneSets(geneSets, T, enrichment_threshold = 0.05, N = 100) computes enrichment ratio between 
    genuine and randomly generated co-module genes (see Zhang2011 for more details).
    
    getEnrichmentInGeneSets(geneSets, T): Computes enrichment of the co-modules for given genesets and threshold T.
    
    getGeneSets(T): Returns co-modules for given threshold T.
    """
    
    def __init__(self, snmnmf):        
        SNMNMNMFEvaluation. __init__(self, snmnmf)        

    def getGeneSet(self, H_matrix, T):
        S = []
        for H in [H_matrix]:
            if isinstance(H, DataFrame):
                S.append(self.removeTemporaryNegativeFeatures(self.getCommoduleMembers(H, T)))
        print(S)
        S = DataFrame(S)
        return S


    def getGeneSets(self, T):
        H1 = self.snmnmf.H1_miRNA
        print(H1)
        H2 = self.snmnmf.H2_genes
        H3 = self.snmnmf.H3_DNAmethyl
        S = []
        for H in [H1, H2, H3]:
            if isinstance(H, DataFrame):                
                S.append(self.removeTemporaryNegativeFeatures(self.getCommoduleMembers(H, T)))
        print(S)
        S = DataFrame(S)
        return S.apply(lambda x: set.union(*x))

    def getEnrichmentRatioInGeneSetsWithH(self, geneSets, H, T, enrichment_threshold = 0.05, N = 100):
           S = self.removeTemporaryNegativeFeatures(self.getCommoduleMembers(H, T))
           cm_set = reduce(or_, S)
           tmp = self.computeEnrichmentRatio(cm_set, geneSets, T, enrichment_threshold=enrichment_threshold, N=N)
           return tmp

    def getEnrichmentRatioInGeneSets(self, geneSets, T, enrichment_threshold = 0.05, N = 100):
           H = self.snmnmf.H2_genes
           S = self.removeTemporaryNegativeFeatures(self.getCommoduleMembers(H, T))
           cm_set = reduce(or_, S) 
           tmp = self.computeEnrichmentRatio(cm_set, geneSets, T\
           , enrichment_threshold = enrichment_threshold, N = N)
           return tmp

    def getEnrichmentInGeneSetsWithH(self, geneSets, H, T):
        S = self.removeTemporaryNegativeFeatures(self.getCommoduleMembers(H, T))
        cm_set = reduce(or_, S)
        all_genes = reduce(or_, Series(geneSets).apply(lambda x: set(x)))
        cm_genes  = set(cm_set).intersection(all_genes)
        enriched_counter, retdict = self.computeFisherExactTest(all_genes, cm_genes, geneSets)
        return retdict

    def getEnrichmentInGeneSets(self, geneSets, T):
        H = self.snmnmf.H2_genes
        S = self.removeTemporaryNegativeFeatures(self.getCommoduleMembers(H, T))
        cm_set = reduce(or_, S)                     
        all_genes = reduce(or_, Series(geneSets).apply(lambda x: set(x)))
        cm_genes  = set(cm_set).intersection(all_genes)
        enriched_counter, retdict\
        = self.computeFisherExactTest(all_genes, cm_genes, geneSets)
        return  retdict
         
    def getCommoduleMembers(self, H, T):
        """Computes co-comodules from matrix H by given threshold T."""
        mu = np.mean(H, axis = 1)    
        sigma = np.std(H, axis = 1)
        Z = H.apply(lambda z: (z-mu)/sigma, axis = 0)
        return Z.apply(lambda x: Z.columns[x >= T].tolist(), axis = 1)        

    def computeEnrichmentInGeneSets(self, H, geneSets):
        commoduleMembers = self.getCommoduleMembers(H, self.T)
        S  =  self.removeTemporaryNegativeFeatures(commoduleMembers)           
        return S  
         
    def computeFisherExactTest(self, all_genes, cm_genes, bpGO, enrichment_threshold = 0.05):
        #
        retdict = {}
        enriched_counter = 0
        for term_name in bpGO.keys():        
            goterm = set(bpGO[term_name])    
            #
            a = len(list(cm_genes.intersection(goterm)))                                              # contains     co-module and     go-term genes
            b = len(list(cm_genes.intersection(all_genes.difference(goterm))))                        # contains     co-module and not go-term genes
            c = len(list(all_genes.difference(cm_genes).intersection(goterm)))                        # contains not co-module and     go-term genes
            d = len(list(all_genes.difference(cm_genes).intersection(all_genes.difference(goterm))))  # contains not co-module and not go-term genes
            #
            x = np.array([[a, b],[c, d]])
            pval = sp.stats.fisher_exact(x)[1]    
            retdict[term_name] = pval
            if pval <= enrichment_threshold:
                enriched_counter = enriched_counter + 1
        return enriched_counter, retdict  
        
    
    def computeEnrichmentRatio(self, cm_set, geneSets, T, enrichment_threshold = 0.05, N = 100):        
        all_genes = reduce(or_, Series(geneSets).apply(lambda x: set(x)))
        cm_genes  = set(cm_set).intersection(all_genes)
        genuine_count, tmp2 = self.computeFisherExactTest(all_genes, cm_genes, geneSets, enrichment_threshold)
        #
        random_count_sum = 0
        for n in range(1, N, 1):
            print str(math.floor(n*100.0/N)) + '%'
            random_cm_genes = np.random.choice(list(all_genes), len(list(cm_genes)), replace = False)    
            random_count, tmp2 = self.computeFisherExactTest(all_genes, set(random_cm_genes), geneSets, enrichment_threshold)
            random_count_sum = random_count_sum + random_count
        if random_count_sum/N != 0:
            return genuine_count/(random_count_sum/N)
        else:
            return 0
     