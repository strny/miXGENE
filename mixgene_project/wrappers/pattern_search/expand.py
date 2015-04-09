__author__ = 'pavel'


def expand(nw, pattern_genes, radius, dist, edges):
    """
    Parameters
    ----------
    nw : scipy.sparse.csr_matrix
         Omics network (PPI, miRNA-target)
    pattern_genes : set like
                    Actual set of features within the pattern
    radius : int, maximum distance of search from the seed
    dist: array[n_genes]
          Distance of a gene from the seed
    Output
    ------
    next_sets : list of candidate sets , i.e. updated pattern_gene sets
    dist : updated dist array
    """

    # pattern_neighbs = set()
    # for neighb in frozenset().union(*[nw.getrow(gene).indices for gene in pattern_genes]):
    #     pattern_neighbs |= set(nw.getrow(neighb).indices)
    next_sets = []
    for gene in pattern_genes:
        for neighb in nw.getrow(gene).indices:
            if neighb in pattern_genes:
                continue
            if dist[gene] + 1 > radius:
                continue
            dist[neighb] = dist[gene] + 1
            edges.add((gene, neighb))
            next_sets += [pattern_genes | set([neighb])]
    if len(next_sets) == 0:
        next_sets = [pattern_genes]
    return next_sets, dist, edges

