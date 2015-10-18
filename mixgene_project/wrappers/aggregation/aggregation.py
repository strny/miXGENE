# -*- coding: utf-8 -*-
import traceback
from celery import task

import numpy as np
import pandas as pd
from sklearn.decomposition import PCA

from converters.gene_set_tools import preprocess_df_gs

from pandas import DataFrame, Series, Index
from django.conf import settings

# load csv data
# mRNA
# m_rna = pd.read_csv('data/mRNA.csv', header=0, index_col=0).transpose()
# miRNA
# mi_rna = pd.read_csv('data/miRNA.csv', header=0, index_col=0).transpose()
# phenotype
# pt = pd.read_csv('data/phenotype.csv', header=0, index_col=0)
# reponse
# response = pt['sex']=='M'
import sys


#@task(name="wrappers.aggregation.aggregation.aggregation_task")
def aggregation_task(exp, block,
                     mode, c,
                     m_rna_es, mi_rna_es, interaction_matrix,
                     base_filename,
    ):
    """
        @type m_rna_es: ExpressionSet
        @type mi_rna_es: ExpressionSet
        @type interaction_matrix: BinaryInteraction

    """
    agg_func = svd_agg
    if mode == "SVD":
        agg_func = svd_agg
    elif mode == "SUB":
        agg_func = sub_agg

    m_rna = m_rna_es.get_assay_data_frame()
    mi_rna = mi_rna_es.get_assay_data_frame()
    targets_matrix = interaction_matrix.load_matrix()

    result_df = agg_func(m_rna, mi_rna, targets_matrix, c)
    result = m_rna_es.clone(base_filename)
    result.store_assay_data_frame(result_df)
    result.store_pheno_data_frame(mi_rna_es.get_pheno_data_frame())

    return [result], {}


### umela data

m_rna = DataFrame([[1,2,3],[1.5,0.5,2]], index=['s1', 's2'], columns=['m1', 'm2', 'm3'])
mi_rna = DataFrame([[0.5, 0.7, 0.1],[1,4,2]], index=['s1', 's2'], columns=['u1', 'u2', 'u3'])
targets_matrix = DataFrame([[1, 1, 0],[1, 1, 0], [0, 0, 1]], index=['u1', 'u2', 'u3'], columns=['m1', 'm2', 'm3'])

# sub agg
def sub_agg(m_rna, mi_rna, targets_matrix, c=1):
    #
    targeting_miRNAs = targets_matrix.sum(axis=0)
    aggtd_data =   m_rna.copy()
    # for all relevant miRNA labels
    miRNA_labels = set(mi_rna.columns) & set(targets_matrix.index)
    #
    for i in Index(miRNA_labels):
        i = Index([i])
        targets = targets_matrix.ix[i, targets_matrix.xs(i[0])==1].columns
        #
        ratios = m_rna[targets].apply(lambda x:[i*1.0/sum(x) for i in x], axis=1)
        subtracts = ratios.apply(lambda x: x*mi_rna[i[0]], axis=0) # ratios*c*miRNA sample-wise
        subtracts = subtracts.apply(lambda x:x/targeting_miRNAs[targets] , axis=1)
        aggtd_data[subtracts.columns] = aggtd_data[subtracts.columns]-subtracts
    return aggtd_data

# svd agg
def svd_agg(m_rna, mi_rna, targets_matrix, c=1):
    #
    mRNA_data = m_rna.apply(lambda x: 1.0*x/max(x), axis=0)
    miRNA_data = mi_rna.apply(lambda x: 1-1.0*x/max(x), axis=0)
    #
    aggregate_data = mRNA_data
    #
    common_mRNAs =  Index(set(mRNA_data.columns) & set(targets_matrix.columns))
    common_miRNAs = Index(set(miRNA_data.columns) & set(targets_matrix.index))
    #
    for mRNA in common_mRNAs:
        #
        mRNA = Index([mRNA])
        #
        targetting_miRNAs = targets_matrix.ix[targets_matrix[mRNA[0]]==1, mRNA].index
        #
        selected_miRNA = miRNA_data.ix[:, targetting_miRNAs]
        #
        if len(selected_miRNA.columns)>1:
            first_comp = DataFrame(np.linalg.svd(selected_miRNA)[2]).ix[0, :]
            first_comp.index = selected_miRNA.index
        new_rep = DataFrame(np.linalg.svd(DataFrame([aggregate_data.ix[:,mRNA[0]], first_comp ]).transpose())[2]).ix[0, :]
        new_rep.index = aggregate_data.index
        aggregate_data.ix[:, mRNA[0]] = new_rep
    return aggregate_data

def svd_agg_train(m_rna, mi_rna, targets_matrix, hide_columns=Index([])):
    #
    sample_indexes = m_rna.index - hide_columns
    mRNA_data = m_rna.apply(lambda x: 1.0*x/max(x), axis=0).ix[sample_indexes, :]
    miRNA_data = mi_rna.apply(lambda x: 1-1.0*x/max(x), axis=0).ix[sample_indexes, :]
    #
    aggregate_data = mRNA_data
    #
    common_mRNAs =  Index(set(mRNA_data.columns) & set(targets_matrix.columns))
    common_miRNAs = Index(set(miRNA_data.columns) & set(targets_matrix.index))
    #
    for mRNA in common_mRNAs:
        #
        mRNA = Index([mRNA])
        #
        targetting_miRNAs = targets_matrix.ix[targets_matrix[mRNA[0]]==1, mRNA].index
        #
        selected_miRNA = miRNA_data.ix[:, targetting_miRNAs]
        #
        if len(selected_miRNA.columns)>1:
            first_comp = DataFrame(np.linalg.svd(selected_miRNA)[2]).ix[0, :]
            first_comp.index = selected_miRNA.index
        new_rep = DataFrame(np.linalg.svd(DataFrame([aggregate_data.ix[:,mRNA[0]], first_comp ]).transpose())[2]).ix[0, :]
        new_rep.index = aggregate_data.index
        aggregate_data.ix[:, mRNA[0]] = new_rep
    return aggregate_data


#@task(name="wrappers.aggregation.aggregation.pca_agg_task")
def pca_agg_task(exp, block,
                     es, gene_sets,
                     base_filename,
    ):
    """
        @type es: ExpressionSet
        @type gene_sets: GeneSets

    """
    df = es.get_assay_data_frame()
    src_gs = gene_sets.get_gs()
    if settings.CELERY_DEBUG:
        import sys
        sys.path.append('/Migration/skola/phd/projects/miXGENE/mixgene_project/wrappers/pycharm-debug.egg')
        import pydevd
        pydevd.settrace('localhost', port=6901, stdoutToServer=True, stderrToServer=True)
    df, src_gs = preprocess_df_gs(df, src_gs)

    result_df = pca_agg(df, src_gs.genes)
    result = es.clone(base_filename)
    result.store_assay_data_frame(result_df)
    result.store_pheno_data_frame(es.get_pheno_data_frame())
    return [result], {}

#@task(name="wrappers.aggregation.aggregation.pca_agg_task_cv")
def pca_agg_task_cv(exp, block,
                     train_es, test_es, gene_sets,
                     base_filename,
    ):
    """
        @type train_es, test_es: ExpressionSet
        @type gene_sets: GeneSets

    """
    df_train = train_es.get_assay_data_frame()
    df_test = test_es.get_assay_data_frame()
    src_gs = gene_sets.get_gs()
    if settings.CELERY_DEBUG:
        import sys
        sys.path.append('/Migration/skola/phd/projects/miXGENE/mixgene_project/wrappers/pycharm-debug.egg')
        import pydevd
        pydevd.settrace('localhost', port=6901, stdoutToServer=True, stderrToServer=True)
    df_train, src_gs_train = preprocess_df_gs(df_train, src_gs)
    df_test, src_gs_test = preprocess_df_gs(df_test, src_gs)

    result_df_train, result_df_test = pca_agg_cv(df_train, df_test, src_gs_train.genes)

    result_train = train_es.clone(base_filename + "_train")
    result_train.store_assay_data_frame(result_df_train)
    result_train.store_pheno_data_frame(train_es.get_pheno_data_frame())

    result_test = test_es.clone(base_filename + "_test")
    result_test.store_assay_data_frame(result_df_test)
    result_test.store_pheno_data_frame(test_es.get_pheno_data_frame())

    return [result_train, result_test], {}


def pca_agg_cv(train_data, test_data, gene_sets):
    """
    train_data      DataFrame
    test_data       DataFrame
    gene_sets       dict of term: set
        Output
    trans_train_data    DataFrame
    trans_test_data     DataFrame
    """
    pca = PCA(n_components=1)
    trans_train = dict()
    trans_test = dict()
    for term in gene_sets.keys():
        trans_train.update({term: pca.fit_transform(train_data[list(gene_sets[term])].values).T[0]})
        trans_test.update({term: pca.transform(test_data[list(gene_sets[term])].values).T[0]})

    trans_train_data = pd.DataFrame(trans_train, columns=gene_sets.keys(), index=train_data.index)
    trans_test_data = pd.DataFrame(trans_test, columns=gene_sets.keys(), index=test_data.index)

    return trans_train_data, trans_test_data

from converters.gene_set_tools import filter_gs_by_genes

def pca_agg(df, gene_sets):
    """
    df       DataFrame
    gene_sets       dict of term: set
        Output DataFrame
    """
    pca = PCA(n_components=1)
    trans = dict()
    for term in gene_sets.keys():
        trans.update({term: pca.fit_transform(df[list(gene_sets[term])].values).T[0]})
    trans_df = pd.DataFrame(trans, columns=gene_sets.keys(), index=df.index)
    return trans_df


# print(sub_agg(m_rna, mi_rna, targets_matrix))

if __name__ == "__main__":
    print(svd_agg(m_rna, mi_rna, targets_matrix))