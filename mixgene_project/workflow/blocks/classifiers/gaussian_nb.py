__author__ = 'pavel'

from .generic_classifier import GenericClassifier


class GaussianNb(GenericClassifier):
    block_base_name = "GAUSSIAN_NB"
    name = "Gaussian Naive Bayes"

    classifier_name = "gaussian_nb"

    def collect_options(self):
        pass

