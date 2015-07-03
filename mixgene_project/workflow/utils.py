__author__ = 'pavel'


import pandas as pd


def match_features(sa_matrix, features, from_index, to_index):
    """
    :type features: list
    :type sa_matrix: pd.DataFrame
    :type from_index: int
    :type to_index: int
    """
    all_features = set(sa_matrix.columns.tolist()[from_index:to_index])
    not_matched = all_features - set(features)
    matched = all_features - not_matched
    return [matched, not_matched]


def reorganize_matrix(sa_matrix, bi_matrix, from_index, to_index, cols=True):
    """
    #indices are 1-based!!!
    :type sa_matrix: pd.DataFrame
    :type from_index: int
    :type to_index: int
    :type cols: bool
    """
    from_index -= 1
    to_index -= 1
    bi_matrix.set_index(bi_matrix.columns[0], inplace=True)
    features = sa_matrix[sa_matrix.columns[from_index:to_index]]
    features = features.columns.tolist()
    if cols:
        bi_matrix_columns = bi_matrix.columns.tolist()
        features = [i for i in features if i in bi_matrix_columns]
        #reorganized matrix
        return bi_matrix[features]
    else:
        bi_matrix_rows = bi_matrix.index.tolist()
        features = [i for i in features if i in bi_matrix_rows]
        return bi_matrix.loc[features, :]