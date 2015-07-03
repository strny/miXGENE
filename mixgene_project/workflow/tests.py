"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
import numpy as np
import pandas as pd
from utils import reorganize_matrix

class UtilsTest(TestCase):
    def test_matrix_reorganization_1(self):
        """
        Tests matrix reorganization
        """
        sa_matrix = pd.DataFrame(np.random.randn(6, 4),
                           index=list('abcdef'),
                           columns=list('ABCD'))

        bi_matrix = pd.DataFrame(np.random.randn(4, 4),
                                 index=list('ABCD'),
                                 columns=list('ABCD'))
        bi_matrix.reset_index(inplace=True)
        new_m = reorganize_matrix(sa_matrix, bi_matrix, 0, 4)
        self.assertEqual(new_m.columns.tolist()[0], "A")

    def test_matrix_reorganization_2(self):
        """
        Tests matrix reorganization
        """
        sa_matrix = pd.DataFrame(np.random.randn(6, 4),
                           index=list('abcdef'),
                           columns=list('DBCA'))

        bi_matrix = pd.DataFrame(np.random.randn(4, 4),
                                 index=list('ABCD'),
                                 columns=list('ABCD'))
        bi_matrix.reset_index(inplace=True)
        new_m = reorganize_matrix(sa_matrix, bi_matrix, 0, 4)
        self.assertEqual(new_m.columns.tolist(), list('DBCA'))


    def test_matrix_reorganization_3(self):
        """
        Tests matrix reorganization
        """
        sa_matrix = pd.DataFrame(np.random.randn(6, 4),
                           index=list('abcdef'),
                           columns=list('DBCA'))

        bi_matrix = pd.DataFrame(np.random.randn(4, 4),
                                 index=list('ABCD'),
                                 columns=list('ABCD'))
        bi_matrix.reset_index(inplace=True)
        new_m = reorganize_matrix(sa_matrix, bi_matrix, 0, 4, cols=False)
        self.assertEqual(new_m.index.tolist(), list('DBCA'))
