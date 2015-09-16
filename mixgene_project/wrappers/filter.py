__author__ = 'pavel'

import numpy as np
from scipy import stats
import pandas as pd
from django.conf import settings


#@task(name="wrappers.filter.zscore_task")
def zscore_task(exp, block,
                     es,
                     base_filename,
    ):
    """
        @type es: ExpressionSet

    """
    if settings.CELERY_DEBUG:
        import sys
        sys.path.append('/Migration/skola/phd/projects/miXGENE/mixgene_project/wrappers/pycharm-debug.egg')
        import pydevd
        pydevd.settrace('localhost', port=6901, stdoutToServer=True, stderrToServer=True)

    m = es.get_assay_data_frame()
    result_arr = stats.zscore(m.as_matrix())
    result_df = pd.DataFrame(columns=m.columns, index=m.index)
    for val, item in enumerate(result_arr):
        result_df.ix[val] = item

    result = es.clone(base_filename)
    result.store_assay_data_frame(result_df)
#    result.store_pheno_data_frame(es.get_pheno_data_frame())

    return [result], {}



#@task(name="wrappers.filter.quant_norm_task")
def quant_norm_task(exp, block,
                     es,
                     base_filename,
    ):
    """
        @type es: ExpressionSet

    """
    if settings.CELERY_DEBUG:
        import sys
        sys.path.append('/Migration/skola/phd/projects/miXGENE/mixgene_project/wrappers/pycharm-debug.egg')
        import pydevd
        pydevd.settrace('localhost', port=6901, stdoutToServer=True, stderrToServer=True)

    m = es.get_assay_data_frame()
    result_df = (m - m.mean()) / (m.max() - m.min())
    result = es.clone(base_filename)
    result.store_assay_data_frame(result_df)
#    result.store_pheno_data_frame(es.get_pheno_data_frame())

    return [result], {}



#@task(name="wrappers.filter.filter_task")
def filter_task(exp, block,
                     filter_type,
                     q,
                     es,
                     base_filename,
    ):
    """
        @type es: ExpressionSet

    """
    if settings.CELERY_DEBUG:
        import sys
        sys.path.append('/Migration/skola/phd/projects/miXGENE/mixgene_project/wrappers/pycharm-debug.egg')
        import pydevd
        pydevd.settrace('localhost', port=6901, stdoutToServer=True, stderrToServer=True)

    filter_func = gene_low_val_filter
    if filter_type == "LOW_VAL":
        filter_func = gene_low_val_filter
    elif filter_type == "VAR":
        filter_func = gene_var_filter

    m = es.get_assay_data_frame()
    result_df = filter_func(m, q)
    result = es.clone(base_filename)
    result.store_assay_data_frame(result_df)
    #result.store_pheno_data_frame(es.get_pheno_data_frame())

    return [result], {}

# Python implementation of a matlab genelowvalfilter function
def gene_low_val_filter(expr_data, q = 60):
    """We removed the gene expression profiles with overall small absolute \\
    values less than a percentile cutoff (60% is used here).

    expr_dat:   a We expect samples in rows and features in columns

    q:          given percetage for the percentile"""
    expr_data = expr_data.copy()
    perval = np.percentile(expr_data, q)
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

