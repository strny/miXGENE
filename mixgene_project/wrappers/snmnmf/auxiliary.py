# -*- coding: utf-8 -*-
"""
Created on Thu Jul 10 11:03:15 2014

@author: holecm
"""

import numpy as np


def loadGmtFile(file_url, sep = '\t', comment = 1):
    """Load a gmt file defined by file_url. See Broadinstitute web page for gmt sets and details."""
    lines = [line.strip().split(sep) for line in open(file_url)]
    if comment != None:
        lines = [line[0:comment]+line[comment+1:] for line in lines]
    return { line[0]:line[1:] for line in lines} # return pathway_name: list of elements
    
# Python implementation of a matlab genelowvalfilter function    
def gene_low_val_filter(expr_data, q = 60):
    """We removed the gene expression profiles with overall small absolute \\
    values less than a percentile cutoff (60% is used here).
    
    expr_dat:   a We expect samples in rows and features in columns
    
    q:          given percetage for the percentile"""
    expr_data = expr_data.copy()
    perval = np.percentile(expr_data, q)
    #
    index_lowVal = expr_data <= perval
    index_remove =  index_lowVal.apply(lambda x: x.all(), axis=0)
    return expr_data[expr_data.columns[~index_remove]]

# Python implementation of a matlab genevarfilter function
def gene_var_filter(expr_data, q = 30):
    """we removed the gene expression profiles with a variance less 
    than the percentile specified by another cutoff (30% is used here)
    
    * We expect samples in rows and features in columns\\
    
    * q given percetage for the percentile"""
    expr_data = expr_data.copy()    
    data_var = expr_data.apply(lambda x: np.var(x), axis = 0) 
    var_percentil = np.percentile(data_var, q)
    index_remove = data_var <= var_percentil
    return expr_data[expr_data.columns[~index_remove]]
    
