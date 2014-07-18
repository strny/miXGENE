# -*- coding: utf-8 -*-
"""
Created on Thu Jul 10 10:58:14 2014

@author: holecm
"""

import nimfa
from snmnmf import SNMNMF, SNMNMFPerformance, SNMNMFException
from scipy.sparse import csr_matrix   
from pandas import DataFrame

class NIMFA_SNMNMFPerformance(SNMNMFPerformance):
    """
    Class which stores factorization quality evaluation (see NIMFA page for more information):
    sm['rss'] Residual sum of squares (Hutchins, 2008). Can be used for estimating optimal factorization rank.
    sm['evar'] Explained variance.
    sm['n_iter'] Actual number of iterations performed
    sm['kl'] Distance according to Kullback-Leibler divergence
    sm['euclidean']  Distance according to Euclidean metric
    sm['cophenetic'] Cophenetic correlation. Can be used for rank estimation.
    fctr_res.distance(metric = "euclidean", idx = 0) The loss function (Euclidean distance between target matrix and its estimate). 
    """
    
    fctr_res = None
    
    def __init__(self, fctr_res):
        self.fctr_res = fctr_res
        
    def getSummary(self, sm):
        return {'rss':sm['rss'], 'evar':sm['evar'], 'n_iter':sm['n_iter'], \
        'euclidean':sm['euclidean'], 'cophenetic':sm['cophenetic']}
        
    def getResults(self):
        sm0 = self.fctr_res.summary(0)
        sm1 = self.fctr_res.summary(1)
        return {'H0':self.getSummary(sm0), 'H1':self.getSummary(sm1)}

class NIMFA_SNMNMF(SNMNMF):    
    #TODO: throw if you have too many or too few data and knowledge
    #def __init__(self): 
    #    pass   
  
    dataConsolided = False  # if function consolideTheData(self) was already used        
        
    def consolideTheData(self):
        """check if the data are suitable for the SNMNMF"""  
        # test if data are present        
        if self.mRNA.empty or self.mRNA.empty:
            raise SNMNMFException("Both mRNA and miRNA matrices must be non-empty.")
        # presence of non-numeric elements
        self.mRNA_doTransformationToNN = self.nonnegativeFactorizationCompatibilty(self.mRNA)[0]
        self.miRNA_doTransformationToNN = self.nonnegativeFactorizationCompatibilty(self.miRNA)[0]
        # transform into NN if needed
        if self.mRNA_doTransformationToNN:
            self.mRNA = self.transformToNonNegativeRepresentation(self.mRNA)        
        
        if self.miRNA_doTransformationToNN:
            self.miRNA = self.transformToNonNegativeRepresentation(self.miRNA)        
        # test if mRNA and miRNA have the same samples
        if not self.colnamesAndIndexCompatibility(A = self.mRNA, B = self.miRNA, index = True):
            raise SNMNMFException("Matrices mRNA and miRNA have not compatible dimemsions")
        # adapt the prior knowledge
        self.gene2gene = self.adaptInteractionData(self.mRNA.columns, self.mRNA.columns, self.gene2gene)
        self.miRNA2gene = self.adaptInteractionData(self.miRNA.columns, self.mRNA.columns, self.miRNA2gene)    
    
    def run(self, **params):
        if not self.dataConsolided:
            print "NIMFA_SNMNMF: preparing data"     
            self.consolideTheData()         
            self.dataConsolided = True
        print "NIMFA_SNMNMF: starting"     
        #        
        V  = self.miRNA.as_matrix()
        V1 = self.mRNA.as_matrix()
        A  = csr_matrix(self.gene2gene)
        B  = csr_matrix(self.miRNA2gene)
        
        fctr = nimfa.mf(target = (V, V1), 
                      seed = params['seed'], # e.g., "random_c", 
                      rank = params['rank'], # e.g., 50, 
                      method = "snmnmf", 
                      max_iter = params['max_iter'], # e.g., 500, 
                      initialize_only = True,
                      A = A ,
                      B = B,               
                      n_run = 3,
                      gamma = self.g1,
                      gamma_1 = self.g2,
                      lamb = self.l1,
                      lamb_1 = self.l2)
        fctr_res = nimfa.mf_run(fctr)
        print "NIMFA_SNMNMF: done"     
        # extract the results
        self.W =  DataFrame(fctr_res.basis(), index = self.miRNA.index)        
        self.H1_miRNA = DataFrame(fctr_res.coef(0), columns = self.miRNA.columns)
        self.H2_genes = DataFrame(fctr_res.coef(1), columns = self.mRNA.columns)
        self.performance = NIMFA_SNMNMFPerformance(fctr_res)
