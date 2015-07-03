__author__ = 'andelmi2'

import scipy.sparse as sp
import numpy as np
import random as rd
import re
import numpy as np

def load_tasks(filename, classes):    
    f = open(filename, 'rb')
    lines = f.readlines()
    f.close()
    names=[]
    pos=[]
    negs=[] 
    for line in lines:
        if line[0] is '#': 
            line=line.replace('\n', '')
            line = line.replace('\r', '')    
            names.append('PB: '+line[2:])
            names.append('BM: '+line[2:])
            continue
        line = re.split('[^\(\)]*c\(|\).*c\(|\)[^\(\)]*',line)
        iTask=False
        for dig in map(int,line[1].split(',')): 
            iTask|=classes==dig
        pos.append(iTask)    
        iTask=False
        for dig in map(int,line[2].split(',')): 
            iTask|=classes==dig
        negs.append(iTask)    
            
    return np.array(pos), np.array(negs), names   
    
def shuffle_data(data, cat, seed=None):
    np.random.seed(seed)
    iperm = np.random.permutation(data.shape[0])
    
    return data[iperm], cat[iperm]    

def draw_graph(edges, path, i, genes_colors=None):
    import pygraphviz as pgv
    G = pgv.AGraph()
    for (i, j) in edges:
        G.add_edge(i, j)
    # if genes_colors:
    #
    G.draw("%s_%s.png"%(path, str(i)), prog='circo')


def mergeNetworks(gene2gene, mir2gene):
    """
    mir2gene : (n_miRNAs x n_genes) scipy.sparse.csr_matrix
    """

    nw = sp.csr_matrix((np.concatenate((gene2gene.data, mir2gene.data)),
                        (np.hstack((gene2gene.row, mir2gene.col)),
                         np.hstack((gene2gene.col, mir2gene.row + gene2gene.shape[0])))),
                       shape=(gene2gene.shape[0] + mir2gene.shape[0], gene2gene.shape[0] + mir2gene.shape[0]))
    return nw

def translate_inters(interactions, platform_order, symmetrize=False, tolower=False):
    """
    Creates GE platform matching network matrix from feature interactions
    Attributes
    ----------
    interactions : DataFrame, names of interacting genes (1st and 2nd column)
    platform_order : list of genes ordered according to the platform
    symmetrize : if the network should be symmetric
    tolower : if genes in the platform are in lower case
    """
    hasht = dict(zip(platform_order, range(len(platform_order))))
    cols = []
    rows = []
    for ix in range(1,len(interactions)):
        inter = interactions.iloc[ix]
        gi = inter[0]
        gj = inter[1]
        if tolower:
            gi = gi.lower()
            gj = gj.lower()
        if (gi not in hasht) or (gj not in hasht):
             continue
        rows += [hasht[gi]]
        cols += [hasht[gj]]
    
    size = len(platform_order) # max(max(rows), max(cols)) + 1
    inters_matr = sp.coo_matrix((np.ones(len(cols)),(rows,cols)), (size, size))
    if symmetrize:
        inters_matr = inters_matr + inters_matr.T 
        inters_matr.data /= inters_matr.data  
            
    return inters_matr

def mergeSamples(mRNA, miRNA):
    """
    :param mRNA:
    :param miRNA:
    :return:
    """
    mRNA = mRNA.drop('class', 1)
    return mRNA.join(miRNA)


def filter_edges(edges, seed):
    """
    :param edges: set of pairs
    :param seed: set of sets
    :return: new set of edges filtered by seed sets
    """
    return set((i, j) for (i, j) in edges for s in seed if i in s and j in s)


def translate_index_to_names(index, gene_names):
    return [gene_names[i] for i in index]


def translate_index_to_names_for_edges(edges, gene_names):
    """
    :param edges: list or set of edges
    :param gene_names: list of gene_names
    :return:
    """
    return set((gene_names[h1], gene_names[h2]) for (h1, h2) in edges)


def translate_names_to_index(names, gene_names):
    """
    :param names: list of gene names
    :param gene_names: list of all genes
    :return: returns list of indices of names in gene_names
    """
    res = []
    names = [name.upper() for name in names]
    gene_names = [gene_name.upper() for gene_name in gene_names]
    for name in names:
        try:
            res.append(gene_names.index(name))
        except ValueError:
            pass
    return res


def shuffle_edge(nw,it=1):
    """
    nw .. scipy sparse matrix
    Output ... scipy sparse matrix
    """

    nw=nw.tocoo()
    inters = np.vstack((nw.row,nw.col)).T

    for i in range(it):
        shuffled=[]
        while len(shuffled)<len(inters):
            (i1,j1),(i2,j2)=rd.sample(inters,2)
            shuffled+=[[i1,j2]]
            shuffled+=[[i2,j1]]
        inters=shuffled
        shuffled=np.array(shuffled)

    return sp.csr_matrix((np.ones(len(shuffled)),(shuffled[:,0],shuffled[:,1])),shape=nw.shape)


def shuffle_edge_PPI(nw,it=1):
    """
    nw .. scipy sparse matrix
    Output ... scipy sparse matrix
    """

    nw=nw.tocoo()
    inters = np.vstack((nw.row,nw.col)).T

    for i in range(it):
        shuffled=[]
        while len(shuffled)<len(inters):
            (i1,j1),(i2,j2)=rd.sample(inters,2)
            shuffled+=[[i1,j2]]
            shuffled+=[[i2,j1]]
            shuffled+=[[j2,i1]]
            shuffled+=[[j1,i2]]
        inters=shuffled
        shuffled=np.array(shuffled)

    return sp.csr_matrix((np.ones(len(shuffled)),(shuffled[:,0],shuffled[:,1])),shape=nw.shape)


# def shuffle_edges(inters, it=1):
#     for i in range(it):
#         shuffled = set()
#         while len(shuffled) < len(inters):
#             (i1, j1), (i2, j2) = rd.sample(inters, 2)
#             shuffled.add((i1, j2))
#             shuffled.add((i2, j1))
#         inters = shuffled
#     return shuffled
#     # return np.array(shuffled)


def check_dir(directory):
    import os
    if not os.path.exists(directory):
        os.makedirs(directory)


def randomize_network(mRNA_network, miRNA_network):
    shuffled_mir = shuffle_edge(miRNA_network)
    shuffled_ppi = shuffle_edge_PPI(mRNA_network)
    return mergeNetworks(shuffled_ppi.tocoo(), shuffled_mir.tocoo())
