# -*- coding: utf-8 -*-
"""
Created on Wed Apr 15 12:41:09 2015

@author: andelmi2
"""
import numpy as np
from sklearn import metrics
from scipy import stats
import itertools

def digit_profile(profile):
    """
    Discretize GE (meta)profile before submitted to mutual information
    based metric. The procedure is according to Chuang, 2007.
    
    Output
    ------
    int array[n_samples] digitized (meta)profile
    """
    n_bins = np.floor(np.log2(len(profile))+1)
    bins = np.histogram(profile,bins=n_bins-1)[1]
    
    return np.digitize(profile,bins) - 1

def pattern_filter(modules, GE, classes, n_best=10, metric='mutual_information', aggregation='average'):
    """
    GE : DataFrame
    classes : DataFrame
    metric : {'mutual_information', 'normed_mutual_information', 'square_error', 
    'correlation' 't-test', 'wilcoxon'}  
    aggregation : {'average', 'setsig'}
    """
    if metric =='mutual_information':
        metric = lambda classes, signature: \
                metrics.mutual_info_score(classes, digit_profile(signature))
    elif metric == 'normed_mutual_information':
        metric = lambda classes, signature: \
                metrics.normalized_mutual_info_score(classes, digit_profile(signature))                
    elif metric == 'square_error':
        metric = lambda classes, signature: metrics.mean_squared_error(classes, signature)
    elif metric == 'correlation':
        metric = lambda classes, signature: np.corrcoef(classes,signature)[1,0]
    elif metric == 'wilcoxon':
        metric = lambda classes, signature: np.abs(stats.wilcoxon(signature[classes==1], \
            signature[classes==0])[0])  
    elif metric == 'ttest':
        metric = lambda classes, signature: np.abs(stats.ttest_ind(signature[classes==1], \
            signature[classes==0])[0])           
    else: raise KeyError("no such a function")
                
    if aggregation == 'average':            
        aggregate = lambda x: np.mean(x,1)
    elif aggregation == 'setsig':
        raise NotImplementedError("Not implemented yet.")
    else: raise KeyError("no such an aggregation")

    modules = [list(mod) for mod in modules]

    sort_modules = sorted(modules, key=lambda mod: metric(classes, aggregate(GE[mod].values)), reverse=True)
    
    return sort_modules[:n_best]
    
def get_patterns(modules, GE, classes, gene2gene):
    """
    returns list of edge-sets
    """    
    gene2gene = gene2gene.tolil()
    genes = GE.columns
    igenes = dict(zip(genes,range(len(genes))))
    
    patterns = []
    for mod in modules:
        edges = set()
        for gi,gj in itertools.combinations(mod,2): 
            try:
                i = igenes[gi]
                j = igenes[gj]
            except KeyError: 
                continue  
            if (gene2gene[i,j]>0) or (gene2gene[j,i]>0):
                edges.add((genes[i],genes[j]))
        patterns.append(edges)
            
    return patterns
    
def differential_expression(GE, classes):
    """
    returns dict gene_names -> {-1, 1}
    """
    tstat = lambda profile: stats.ttest_ind(profile[classes==1], profile[classes==0])[0]
    de = np.array(map(tstat, GE.values.T))
    Min = de.min()
    Max = de.max()
    de=de*2/(Max-Min) - 2*Min/(Max-Min) - 1
    
    return dict(zip(GE.columns, de))    
    