# -*- coding: utf-8 -*-
"""
Created on Thu Feb 20 16:12:55 2014

@author: andelmi2
"""

from .walkforest import WalkForestClassifier
import scipy.sparse as sp

class WalkForestHyperLearner:
    """ Heuristicky urci delku prochazky po nahodne pasece
    Parameters
        ----------
        gene2gene : DataFrame, or scipy.sparse.matrix-like 
            protein-protein interaction matrix
        mir2gene : DataFrame, or scipy.sparse.matrix-like 
            target-miRNA interaction matrix  
        causgenes : gene-sets-like set of candidate genes
            for particular disese terms.      
        heur : heuristic to set walk length
                {'incid', 'tree_errors' }
    """

    def __init__(self,
                 gene2gene,
                 causgenes=None,
                 miRNA2gene=None,
                 walk_lengths=range(1, 11),
                 heuristic='incid',
                 n_estimators=1000,
                 eps=.01,
                 criterion="gini",
                 max_depth=1,
                 min_samples_split=2,
                 min_samples_leaf=1,
                 n_jobs=1,
                 random_state=None,
                 max_features='auto',
                 fsubsets=None,
                 bootstrap=False,
                 oob_score=False,
                 verbose=0
                 ):
        self.eps = eps
        self.n_estimators = n_estimators
        self.learners = []
        gene2gene = gene2gene.load_matrix()
        gene2gene = sp.coo_matrix(gene2gene.values)
        gene2gene = (gene2gene + gene2gene.T).tocoo()
        gene2gene.data /= gene2gene.data
        if miRNA2gene is not None:
            miRNA2gene = miRNA2gene.load_matrix()
            miRNA2gene = sp.coo_matrix(miRNA2gene.values)

        if heuristic in {'tree_errors', 'incid'}:
            tree_error = lambda tree, X, y: sum(y != tree[0].predict(X[:, tree[1]]))
            if heuristic == 'tree_errors':  # sum of trees' training error
                self.heuristic = lambda learner, X, y: sum(tree_error(tree, X, y) \
                                                           for tree in learner.estimators_)
            else:  # incidence of underfitted trees
                self.heuristic = lambda learner, X, y: sum(1 if tree_error(tree, X, y) > 0 \
                                                               else 0 for tree in
                                                           learner.estimators_) * 1. / self.n_estimators
        else:
            raise ValueError('Unknown heuristic')
        for k in walk_lengths:
            self.learners += [WalkForestClassifier(gene2gene, causgenes, mir2gene=miRNA2gene, \
                                                   n_estimators=self.n_estimators, random_state=random_state, K=k,
                                                   max_features=max_features, \
                                                   max_depth=max_depth, min_samples_leaf=min_samples_leaf,
                                                   bootstrap=bootstrap)]

    def fit(self, X, y):
        heur = []
        for k, learner in enumerate(self.learners):
            learner.fit(X, y)
            heur.append(self.heuristic(learner, X, y))
            if len(heur) < 2:
                continue
            if (heur[-2] - heur[-1] < self.eps) or (heur[-1] < self.eps):
                self.opt_model = self.learners[k - 1]
                print heur
                break
        # self.opt = min(range(len(self.heur)-1),key=lambda i:self.heur[i+1]-self.heur[i])
        return self

    def full_heur(self, X, y):
        "Computes full heuristic"

        heur = []
        for learner in self.learners:
            learner.fit(X, y)
            heur.append(self.heuristic(learner, X, y))

        return heur

    def predict(self, X):
        return self.opt_model.predict(X)
