__author__ = 'pavel'

import unittest
from mixgene_project.wrappers.aggregation.aggregation import svd_agg, sub_agg
from pandas import DataFrame
from pandas.util.testing import assert_frame_equal


class AggregationTestCase(unittest.TestCase):

    def setUp(self):
        self.m_rna = DataFrame([[1, 2, 3], [1.5, 0.5, 2]],
                               index=['s1', 's2'], columns=['m1', 'm2', 'm3'])
        self.mi_rna = DataFrame([[0.5, 0.7, 0.1], [1, 4, 2]],
                                index=['s1', 's2'], columns=['u1', 'u2', 'u3'])
        self.targets_matrix = DataFrame([[1, 1, 0], [1, 1, 0], [0, 0, 1]],
                                        index=['u1', 'u2', 'u3'], columns=['m1', 'm2', 'm3'])

    def test_svd_agg(self):
        output_matrix = DataFrame([[-0.768759, -0.722027, -0.77461],
                                   [-0.639538, -0.691865, -0.63244]],
                                  index=['s1', 's2'], columns=['m1', 'm2', 'm3'])
        # print(svd_agg(m_rna, mi_rna, targets_matrix))
        assert_frame_equal(svd_agg(self.m_rna, self.mi_rna, self.targets_matrix), output_matrix)
        # self.assertEqual(svd_agg(m_rna, mi_rna, targets_matrix), output_matrix)

    def test_sub_agg(self):
        output_matrix = DataFrame([[0.800, 1.600, 2.9], [-0.375, -0.125,  0.0]],
                                  index=['s1', 's2'], columns=['m1', 'm2', 'm3'])
        # print(sub_agg(m_rna, mi_rna, targets_matrix))
        assert_frame_equal(sub_agg(self.m_rna, self.mi_rna, self.targets_matrix), output_matrix)


if __name__ == '__main__':
    unittest.main()
    # suite = unittest.TestLoader().loadTestsFromTestCase(TestSequenceFunctions)
    # unittest.TextTestRunner(verbosity=2).run(suite)