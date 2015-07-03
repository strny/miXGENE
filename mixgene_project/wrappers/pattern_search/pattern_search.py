"""
-------------------------------------------------------------------------------
Object oriented design and extension of differential expressed pattern mining 
-------------------------------------------------------------------------------
Method of Chuang, 2007 is state-of-the-art approach in set-level analysis 
of gene expression (GE) data. It mines differentially expressed patterns (subgraphs)
based on GE data and prior knowledge of genes interactions. 
    Besides mining and reporting differentially expressed patterns, this design 
enables modular use of differential pattern mining (Chuang, 2007) with modifications
of metrics, search strategy, etc. Moreover, it enables integration of all the adjacent
procedures into Scikit-learn pipelines. Henceforth, the patterns discovered may be further
used as metafearues and be empirically validated within a classification framework. 
It overloads Scikit-learn methods of feature-space transformation. 
    The we propose a new generic method tailored for potentially anticorelated
features, namely miRNAs and targeted genes. The method DynamicSetSig is based 
on computing gene signatures (Mramor, 2009). However, it constructs the signature 
dynamicaly as the pattern is beeing constructed. It speeds up the computation.

References
----------
H Chuang et al. Network-based classification of breast cancer metastasis.
    Mol Syst Biol, 3, 2007.
F Pedregosa et al. Scikit-learn: Machine Learning in Python.
    JMLR 12, pp. 2825-2830, 2011.
M Mramor et al. "On utility of gene set signatures in gene expression-based cancer class prediction.
    Machine Learning in Systems Biology, 2009.
"""
    
__author__ = 'andelmi2'
# Michael Andel, Czech technical University in Prague, 2015


import numpy as np

from .utils import draw_graph

import scipy.stats
import copy
import sklearn.metrics  
import numpy as np
from scipy import stats
from utils import check_dir
import time

class SearchMethod:
    """ Differentially expressed pattern search method """
    def create_pattern(self, data, seed):
        raise NotImplementedError()

    
class ChuangMethod:
    """
    Differentiall pattern search method based on averaged GE profile (Chuang, 2007)
    """
    def create_pattern(self, data, seed):
        return AvgPattern(data, seed)
 
   
class DynamicSetSig:
    """
    Our method, dedicated for potentially antocorelated features, namely miRNA-target
    """    
    def create_pattern(self, data, seed):
        return SetSigPattern(data, seed)   
        
class Pattern(object):
    """
    Differentially expressed pattern -- subgraph validated by data.
        
    Parameters
    ----------
    seed : gene id
        A seed gene to initialize the patterns
    Attributes
    ----------
    genes : set of gene ids
    edges : set of gene id tuples
    score : float, scores the diference in expressions between two phenotypes
    dist : array[n_genes]
        Distance of a gene from the seed
    signatures : array[n_samples]
        Metafeature characterization of pattern geneset for each sample    
    """    
    def __init__(self, data, seed):   
        self.genes = set([seed])
        self.edges = set()
#        self.dist = [0 for _ in xrange(data.shape[1])]
        self.dist = -np.ones(data.shape[1])
        self.dist[seed] = 0
        self.score = 0            
        self.signatures = np.zeros(data.shape[0])
        self.added = seed
    
    
    def expandX(self, network, radius):
        """
        Expands the pattern according to gene network.
        
        Input
        -----
        network : scipy.sparse.csr_matrix, i.e. graph
            Gene network to expand the pattern
        Output
        ---------
        expansion : list of candidate patterns
        """
        expansion = []
        for gene in self.genes:
            for neighb in network.getrow(gene).indices:
                if neighb in self.genes:
                    continue
                if self.dist[gene]+1 > radius:
                    continue
                next_pattern = copy.deepcopy(self)
                next_pattern.genes.add(neighb)
                #next_pattern.edges.add((gene, neighb))
                next_pattern.added = neighb                    
                next_pattern.dist[neighb] = self.dist[gene] + 1
                expansion += [next_pattern]

        return expansion if len(expansion) > 0 else [self] 
    
#    def expand(self, network, radius):
#        """
#        Expands the pattern according to gene network.
#        
#        Input
#        -----
#        network : scipy.sparse.csr_matrix, i.e. graph
#            Gene network to expand the pattern
#        Output
#        ---------
#        expansion : list of candidate patterns
#        """
#        expansion = []
#        used = [0]*network.indices.max()
#        for gene in self.genes:
#            for neighb in network.getrow(gene).indices:
#                try:
#                    if used[neighb]:
#                        continue
#                except: KeyError(neighb)    
#                if neighb in self.genes:
#                    continue
#                if self.dist[gene]+1 > radius:
#                    continue
#                used[neighb] = 1
#                next_pattern = copy.deepcopy(self)
#                next_pattern.genes.add(neighb)
#                #next_pattern.edges.add((gene, neighb))
#                next_pattern.added = neighb                    
#                next_pattern.dist[neighb] = self.dist[gene] + 1
#                expansion += [next_pattern]
#
#        return expansion if len(expansion) > 0 else [self] 
        
    def expand2(self, network, radius):
        """
        Expands the pattern according to gene network.
        
        Input
        -----
        network : scipy.sparse.csr_matrix, i.e. graph
            Gene network to expand the pattern
        Output
        ---------
        expansion : list of candidate patterns
        """
        expansion = []
        neighbors = frozenset().union(*[set(network.getrow(g).indices) for g in self.genes])  
        for neighb in neighbors:           
            if neighb in self.genes:
                continue
            dist_from_pattern = self.dist[network.getrow(neighb).indices] 
            dist_of_added = dist_from_pattern[dist_from_pattern > -1].min() + 1
            if dist_of_added > radius:
                continue
            
            next_pattern = copy.deepcopy(self)
            next_pattern.genes.add(neighb)
            #next_pattern.edges.add((pred, neighb))
            next_pattern.added = neighb                    
            next_pattern.dist[neighb] = dist_of_added
            expansion += [next_pattern]

        return expansion if len(expansion) > 0 else [self]     
        
    def expand(self, network, radius):
        """
        Expands the pattern according to gene network.
        
        Input
        -----
        network : scipy.sparse.csr_matrix, i.e. graph
            Gene network to expand the pattern
        Output
        ---------
        expansion : list of candidate patterns
        """
        expansion = []
        neighbors = frozenset().union(*[set(network.getrow(g).indices) for g in self.genes])  
        for neighb in neighbors:           
            if neighb in self.genes:
                continue
            preds = list(set(network.getrow(neighb).indices) & self.genes) 
            if len(preds)>2:
                pass
            dist_seed = self.dist[preds].min() + 1
            if dist_seed > radius:
                continue
            
            next_pattern = copy.deepcopy(self)
            next_pattern.genes.add(neighb)
            next_pattern.edges |= set((pred, neighb) for pred in preds)  
            next_pattern.added = neighb                    
            next_pattern.dist[neighb] = dist_seed
            expansion += [next_pattern]

        return expansion if len(expansion) > 0 else [self]     
        
    def evaluate(self, data, metric, classes=None):
        """
        Scores the pattern based on phenotepe and chosen metric
        metric : {'mutual_information', 'normed_mutual_information', 'square_error', 
                  'correlation' 't-test', 'wilcoxon'}
        """
        func_dict = {
        'mutual_information': sklearn.metrics.mutual_info_score,
        'normed_mutual_information': sklearn.metrics.normalized_mutual_info_score,
        'square_error': sklearn.metrics.mean_squared_error,
        't-test': scipy.stats.ttest_ind,
        'wilcoxon': scipy.stats.wilcoxon,
        'correlation': np.corrcoef
        }
        self.make_signature(data, classes)
        try:
            if metric in {'mutual_information', 'normed_mutual_information'}:
                self.score = func_dict[metric](classes, self.digit_signature()) 
            elif metric == 'square_error':
                self.score = func_dict[metric](classes, self.signatures)
            elif metric in {'t-test', 'wilcoxon'} :
                self.score = np.abs(func_dict[metric](self.signatures[classes==1], \
                    self.signatures[classes==0])[0])
 
            elif metric == 'correlation':
                self.score = func_dict[metric](classes, self.signatures)[1,0]
                    
        except: KeyError("no such a function")            
   
        return self.score
        
    def make_signature(self, data, classes=None):
        """
        Computes metafeature for the pattern based on expression data 
        
        Input
        -----
        data : numpy array[n_samples, n_genes]
        classes : numpy zero-one array[n_samples]
        """ 
        raise NotImplementedError
        
    def digit_signature(self):
        """
        Discretize GE (meta)profile before submitted to mutual information
        based metric. The procedure is according to Chuang, 2007.
        
        Output
        ------
        int array[n_samples] digitized (meta)profile
        """
        n_bins = np.floor(np.log2(len(self.signatures))+1)
        bins = np.histogram(self.signatures,bins=n_bins-1)[1]
        
        return np.digitize(self.signatures,bins) - 1
        

class AvgPattern(Pattern):
    """
    Differentially expressed pattern according to Chuang, 2007.
    """
    def __init__(self, data, seed):
        super(AvgPattern, self).__init__(data, seed)
    
    def make_signature(self, data, classes=None):
        """
        Metafeature is created as an average profile over the pattern genes
        """
        N = len(self.genes)
        self.signatures = ((N-1)*self.signatures + data[:,self.added])/N
        
        
class SetSigPattern(Pattern):
    """
    Differentialy expressed pattern suited for anticorrelated features
    
    Attributes
    ----------
    Buffer statistics used for dynamical computing of SetSig:
    covars : float array[n_samples, n_samples]
    means : float array[n_samples]
    variances : float array[n_samples]
    """
    def __init__(self, data, seed):
        super(SetSigPattern, self).__init__(data, seed)          
        self.covars = np.zeros(data.shape[0],data.shape[0]) 
        self.means = data[:,seed]
        self.variances = np.zeros(data.shape[0]) 
        
    def make_signature(self, data, classes=None):
        """
        Computes SetSig metafeatures in a dynamic way based on GE data and respective phenotype
        """
        if classes is None:
            raise ValueError("DynamicSetSig is a supervised method. Classes must be specified!")
            
        N = len(self.genes)
        means = (self.means*(N-1) + data[:,self.added]) / N
        variances = (self.variances*(N-1) + (data[:,self.added]-self.means)\
                    *(data[:,self.added]-means)) / N
        
        corrs=np.zeros(self.covars.shape)
        for samp in range(data.shape[0]):

            for samp2 in range(data.shape[1]):
                self.covars[samp,samp2] = (self.covars[samp,samp2]*(N-1) + \
                    (data[samp,self.added]-means[samp]) * \
                    (data[samp2,self.added]-self.means[samp2])) / N
                    
                corrs[samp,samp2] = self.covars[samp,samp2] / \
                                    (variances[samp]**.5 * variances[samp2]**.5)    
                    
                self.signatures[samp] = scipy.stats.ttest_ind(corrs[samp][classes==0], corrs[samp][classes==1])   
        
        self.means = means
        self.variances = variances    
        
            
class DifferentialPatternSearcher(object):
    """
    Mines differentially expressed patterns (subgraphs) based on GE data and prior
    knowledge of genes interactions. Implements and furhter extends the method of Chuang, 2007. 
    
    Parameters
    ----------
    network : scipy.sparse matrix
            Gene network to expand the pattern
    seeds : list of gene indices
        If unspecified, uses all the genes present in the network 
    search_method : {'Chuang', 'DynamicSetSig'}    
    metric : {'mutual_information', 'normed_mutual_information', 'square_error', 
        'correlation' 't-test', 'wilcoxon'}        
    radius : integer, default 3, as the gene networks small worlds
        Maximum distance of search from the seed
    min_improve : float, percentage of improvement to admit next expansion    
    trivial_pattern : boolean
        Wheter to accept trivial patterns, i.e. isolated interactions 
    gene_names: list of gene names (for further reporting)    
    draw : boolean, whether to draw the pattern in GraphViz
    verbose : boolean    
    
    Attributes
    ----------
    patterns : list of discovered differentially expressed patterns
    """
    def __init__(self,
                 network,
                 search_method ='Chuang',
                 metric='mutual_information',
                 seeds=None,
                 radius=3,
                 min_improve=.05,
                 gene_names = None,
                 trivial_patterns=True,
                 verbose=True,
                 draw=False,
                 base_dir='./'):    
        self.network = network.tocsr()
        self.seeds = np.unique(self.network.indices) if seeds is None else seeds
        self.metric = metric
        self.radius =radius
        self.min_improve = min_improve
        self.gene_names = gene_names
        self.trivial_patterns = trivial_patterns
        self.verbose = verbose
        self.draw = draw
        self.base_dir=base_dir
        
        if search_method == 'Chuang':
            self.search_method = ChuangMethod()
        elif search_method == 'DynamicSetSig':
            self.search_method = DynamicSetSig()
        else: raise ValueError('Not supported search method')
            
    def search(self, data, classes):
        """
        Searches for the patterns based on expression data 
        
        Input
        -----
        data : numpy array[n_samples, n_genes], GE data
        classes : numpy zero-one array[n_samples]
        """
        self.patterns = []
        c = 0
        time_d=0
        for seed in self.seeds:
            #print seed
            c += 1
            if self.verbose and c%100 == 0:         
                print "Searching with seed %s" % str(seed)
                print np.mean(time_d) 
                time_d = 0

            pattern = self.search_method.create_pattern(data, seed)
            pattern.evaluate(data, self.metric, classes)
            st=time.clock()
            while True:
                next_pattern = max(pattern.expand(self.network,self.radius),
                            key=lambda ex: ex.evaluate(data, self.metric, classes))                                      
                if (next_pattern.score / pattern.score) > 1+self.min_improve:
                    pattern = next_pattern
                   # print "zlepseni",pattern.score
                else: 
                    break
            #pattern.edges = filter_edges(pattern.edges, pattern.genes)
            time_d += time.clock()-st
            if self.trivial_patterns or len(list(seed)[0]) > 2:
                self.patterns += [pattern]    
                check_dir(self.base_dir + 'greedy_search_pics/')
                if self.draw:
                    gene_color = dict()
                    for gene in pattern.genes:
                        edges_names = set((self.gene_names[h1], self.gene_names[h2]) for (h1, h2) in pattern.edges)
                        # a function to color a gene in discovered pattern
                        gene_color[self.gene_names[gene]] = scipy.stats.ttest_ind(data[:,-1], GE_profile = data[:,gene])
                    print "Drawing a graph for seed %s" % str(seed)
                    draw_graph(edges_names, self.base_dir + 'greedy_search_pics/test-graph-greedy', seed)    

            # if seed > 550:
            #     break

        return self.patterns

    def transform(self, data, classes=None, threshold=None):
        """
        Scikit-learn like method to ransform high dimensional GE data into few\
        interpretable subgraph features
        
        Output
        ------
        array[n_samples, n_best_patterns] Transformed data in pattern feature space
        """
        if (classes is None) and self.search_method is DynamicSetSig:
            raise ValueError("DynamicSetSig is a supervised method. Classes must be specified!")
            
        self.search(data, classes)    
        metafeatures = self.filter_patterns(threshold)    
        return np.array([pattern.signatures for pattern in metafeatures]).T
        
    def filter_patterns(self,threshold):
        """
        Filters discovered patterns by their score or throu the null distribution
        """
        if threshold is not None:
            pass #learn threshold
        return filter(lambda pattern: pattern.score > threshold, self.patterns)

