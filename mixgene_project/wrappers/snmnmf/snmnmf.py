# -*- coding: utf-8 -*-
"""
Created on Thu Jul 10 10:58:14 2014

@author: holecm
"""

import pandas as pd
import auxiliary as aux



class SNMNMFException(Exception):
    pass
    # """Base class for exceptions in this module."""
    # def __init__(self, msg = None):
    #     self.msg = msg
    

class SNMNMFPerformance:

    def __init__(self):
        pass    
    
    def getResults(self):
        raise SNMNMFException("Results are not available.")
        
        
class SNMNMF(object):    
    """TODO: Factorization task description"""
    
    # data    
    mRNA = None
    miRNA = None
    DNAmethyl = None
    # knowledge
    gene2gene = None
    miRNA2gene = None
    gene2DNAmethylation = None
    # params
    l1 = None # −λ1 Tr(H_2*gene2gene*H_2) --  The parameters λ1 and λ2 are weights for the must-link constraints defined
    l2 = None # −λ2 Tr(H_1*miRNA2gene*H_2)
    l3 = None # −λ3 Tr(H_2*gene2DNAmethylation*H_3)
    g1 = None # g1*||W||^2_F --- limits growth of W
    g2 = None # γ2(hj 1 2 + hj 2 1) -- encourages sparsity    
    # results
    W = None
    H1_miRNA = None
    H2_genes = None
    H3_DNAmethyl = None
    # performance
    performance = SNMNMFPerformance()    
    # indicates if data are non-negative      
    mRNA_doTransformationToNN = False      
    miRNA_doTransformationToNN = False  
    DNAmethyl_doTransformationToNN = False  
   
    # init data
    def __init__(self, mRNA, miRNA = None, DNAmethyl = None, gene2gene=None, miRNA2gene = None \
    ,gene2DNAmethylation = None , params = {}):        
        # data
        self.mRNA = mRNA
        self.miRNA = miRNA
        self.DNAmethyl = DNAmethyl
        # knowledge
        self.gene2gene = gene2gene
        self.miRNA2gene = miRNA2gene
        self.gene2DNAmethylation = gene2DNAmethylation        
        # params
        self.l1 =  params.get('l1')
        self.l2 =  params.get('l2')
        self.l3 =  params.get('l3')
        self.g1 =  params.get('g1')
        self.g2 =  params.get('g2')      
        # TODO: check if data are usable (no NaN, wrond dimesions, or bad col and row names)
    
    # transform data matrix into its non-negative equivalent using a method by Kim and Tidor (2003).
    def transformToNonNegativeRepresentation(self, data_matrix, indicator_string = 'negative_feature___'):
        """The function 'doubles' the original matrix MxN into Mx2N. The positive part is in \\
        the left submatrix and the negative part is negated and in the right submatrix so \\
        that the final matrix is non-negative."""
        data_matrix = data_matrix.copy()
        neg_indicies = data_matrix.apply(lambda x: x < 0)
        if neg_indicies.any().any() == False:
            raise SNMNMFException("There is not a need to make this matrix non-negative")
        #
        additional_columns = [indicator_string + str(s) for s in data_matrix.columns]
        additional_data_matrix = -data_matrix.copy()
        additional_data_matrix[~neg_indicies] = 0
        data_matrix[neg_indicies] = 0
        additional_data_matrix.columns = additional_columns
        #
        new_data_matrix = pd.concat([data_matrix, additional_data_matrix], axis=1)
        return new_data_matrix
        
    # Test NMF compatibility specified in an argument list    
    def nonnegativeFactorizationCompatibilty(self, *matrices_list):
        """Test NMF compatibility specified in an argument list.\
        Returns T/F values for the matrices specified as imputs."""        
        retlist = []
        for m in matrices_list:
            if m.isnull().any().any():
                raise SNMNMFException("Missing data are not allowed for the factorization.")     
            if (m < 0).any().any():      
                retlist.append(True)
            else:
                retlist.append(False)
        return retlist            
            
    # Test multiplication compatibility for data frames specified in an argument list      
    def colnamesAndIndexCompatibility(self, A, B, index = False, columns = False, transposed_A = False):
        """Matrices A and B must share the same index and colums names,\
        in some cases it is necessary to transpose one of the matrices"""
        if transposed_A:
            test_index =  str(A.columns) == str(B.index)
            test_columns =  str(A.index) == str(B.columns)
        else:        
            test_index =  str(A.index) == str(B.index)
            test_columns =  str(A.columns) == str(B.columns)
        if index & columns:
            return test_index & test_columns
        if index and not columns:
            return test_index 
        if not index and columns:
            return test_columns    

    # For an interaction matrix, assures the dimensional compatibility
    def adaptInteractionData(self, index_names, columns_names, interactions_matrix):
        """Return the adapted interaction matrix."""
        inte = pd.DataFrame(interactions_matrix, index=index_names, columns=columns_names).to_sparse()
        inte = inte.fillna(0)
        return inte
            
    def run(self):
        print "this method should be overridden"     
        #        

    def tostring(self):
        retstr = ""
        #if mRNA != None:
        retstr = "mRNA: " + str(self.mRNA.shape) + "\n"
        #if miRNA != None:
        retstr = retstr + "miRNA: " + str(self.miRNA.shape) + "\n"
        #if DNAmethyl != None:
        #print "DNA methyl: " + DNAmethyl.shape
        retstr = retstr + "l1: " + str(self.l1) +"; l2: "+ str(self.l2) +"; g1: "+ str(self.g1) +"; g2: "+ str(self.g2) + "\n"    
        return retstr


def loadData(full = False):
    """Loads data from Zhang2011"""
    # mRNA
    m_rna = pd.read_csv('test/data/genedata3_30.csv.bz2', header=0, compression='bz2')
    # miRNA
    mi_rna = pd.read_csv('test/data/microdata3_30.csv.bz2', header=0, compression='bz2')
    #  
    m2g_intction =  pd.read_csv('test/data/geneMicroMatrix_v5.csv.bz2', header=None, compression='bz2').to_sparse()
    #
    pp_intction = pd.read_csv('test/data/ppiMatrixTF.csv.bz2', header=None, compression='bz2').to_sparse()
    #
    bpGO = aux.loadGmtFile('test/data/c5.bp.v4.0.symbols.gmt')
    # fix the missing col and row names
    m2g_intction.columns = m_rna.columns
    m2g_intction.index = mi_rna.columns
    pp_intction.columns = m_rna.columns    
    pp_intction.index = m_rna.columns    
    
    ## filter the data
    m_rna = aux.gene_low_val_filter(m_rna)
    m_rna = aux.gene_var_filter(m_rna)
    #
    mi_rna = aux.gene_low_val_filter(mi_rna)
    mi_rna = aux.gene_var_filter(mi_rna)
    
    # select a submatrix just for the testing purposes
    if full == False:
        mi_rna = mi_rna[mi_rna.columns[0:30]]
        m_rna = m_rna[m_rna.columns[0:50]]    
    
    return m_rna, mi_rna, m2g_intction, pp_intction, bpGO
        
