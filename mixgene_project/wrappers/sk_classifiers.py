# -*- coding: utf-8 -*-

import logging
import traceback, sys

from sklearn.svm import LinearSVC, SVC
from sklearn.naive_bayes import GaussianNB
from sklearn import tree
from sklearn import neighbors
from sklearn.ensemble import RandomForestClassifier
from sklearn import preprocessing
# from walkforest.hyperlearner import WalkForestHyperLearner
from walkforest.walkforest import WalkForestHyperLearner
from celery import task

from environment.structures import ExpressionSet, ClassifierResult
# from workflow.blocks.generic import GenericBlock
from wrappers.scoring import compute_scores
from django.conf import settings



log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


classifiers_map = {
    # name -> ( fabric,  apply wrapper, if None use common_apply)
    "linear_svm": (LinearSVC, None),
    "svm": (SVC, None),
    "gaussian_nb": (GaussianNB, None),
    "DT": (tree.DecisionTreeClassifier, None),
    "random_forest": (RandomForestClassifier, None),
    "knn": (neighbors.KNeighborsClassifier, None),
    "walk_forest": (WalkForestHyperLearner, None)
}


def apply_classifier(
    exp, block,
    train_es, test_es,
    classifier_name, classifier_options=None, fit_options=None,
    base_folder="/tmp", base_filename="cl"
):
    """
        @type train_es: ExpressionSet
        @type test_es: ExpressionSet
        @type exp: Experiment
        @type block: GenericBlock
    """
    # if settings.CELERY_DEBUG:
    #     import sys
    #     sys.path.append('/Migration/skola/phd/projects/miXGENE/mixgene_project/wrappers/pycharm-debug.egg')
    #     import pydevd
    #     pydevd.settrace('localhost', port=6901, stdoutToServer=True, stderrToServer=True)

    if not classifier_options:
        classifier_options = {}
    if not fit_options:
        fit_options = {}

    target_class_column = train_es.pheno_metadata["user_class_title"]


    # Unpack data
    x_train = train_es.get_assay_data_frame().as_matrix().transpose()
    # x_train = train_es.get_assay_data_frame().as_matrix()
    y_train = train_es.get_pheno_data_frame()[target_class_column].as_matrix()

    x_test = test_es.get_assay_data_frame().as_matrix().transpose()
    # x_test = test_es.get_assay_data_frame().as_matrix()
    y_test = test_es.get_pheno_data_frame()[target_class_column].as_matrix()

    # Unfortunately svm can't operate with string labels as a target classes
    #   so we need to preprocess labels
    le = preprocessing.LabelEncoder()
    le.fit(y_train)

    y_train_fixed = le.transform(y_train)
    y_test_fixed = le.transform(y_test)

    # Classifier initialization
    fabric, apply_func = classifiers_map[classifier_name]
    log.debug("Classifier options: %s", classifier_options)
    if apply_func is None:
        cl = get_classifier(fabric, classifier_options, classifier_name, block)
        log.debug("Fitting classifier.")
        cl.fit(x_train, y_train_fixed)
        log.debug("Finished fitting classifier.")
    else:
        raise NotImplementedError()

    log.debug("Applying on test.")
    # Applying on test partition
    y_test_predicted = cl.predict(x_test)
    log.debug("Building result.")
    # Here we build result object
    cr = ClassifierResult(base_folder, base_filename)

    log.debug("Storing labels.")
    cr.labels_encode_vector = le.classes_  # Store target class labels

    log.debug("Storing y.")
    cr.y_true = y_test_fixed
    cr.y_predicted = y_test_predicted

    cr.classifier = classifier_name
    log.debug("Storing model.")
    # TODO Why to store model?
    # cr.store_model(cl)
    log.debug("Finished apply_classifier.")
    return [cr], {}


def get_classifier(fabric, classifier_options, name, block):
    log.debug("Begin to get the classifier.")
    scope = block.get_scope()
    log.debug("Getting scope.")
    scope.load()
    log.debug("Scope loaded.")
    # if settings.CELERY_DEBUG:
    #     import sys
    #     sys.path.append('/Migration/skola/phd/projects/miXGENE/mixgene_project/wrappers/pycharm-debug.egg')
    #     import pydevd
    #     pydevd.settrace('localhost', port=6901, stdoutToServer=True, stderrToServer=True)

    cl = scope.get_temp_var("classifier_%s_%s" % (name, block.uuid))
    log.debug("Variable read.")
    if cl:
        log.debug("Returning existing classifier.")
        return cl
    else:
        log.debug("Initializing new classifier!")
        cl = fabric(**classifier_options)
        scope.set_temp_var("classifier_%s_%s" % (name, block.uuid), cl)
        scope.store()
        log.debug("Returning new classifier.")
        return cl
