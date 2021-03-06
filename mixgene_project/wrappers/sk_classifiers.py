# -*- coding: utf-8 -*-

import logging
import traceback, sys

from sklearn.svm import LinearSVC, SVC
from sklearn.naive_bayes import GaussianNB
from sklearn import tree
from sklearn import neighbors
from sklearn.ensemble import RandomForestClassifier
from sklearn import preprocessing
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
    "ncf": (WalkForestHyperLearner, None)
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
    if settings.CELERY_DEBUG:
        import sys
        sys.path.append('/Migration/skola/phd/projects/miXGENE/mixgene_project/wrappers/pycharm-debug.egg')
        import pydevd
        pydevd.settrace('localhost', port=6901, stdoutToServer=True, stderrToServer=True)

    if not classifier_options:
        classifier_options = {}
    if not fit_options:
        fit_options = {}

    target_class_column = train_es.pheno_metadata["user_class_title"]
    tr_es = train_es.get_assay_data_frame()
    cols = tr_es.columns

    te_es = test_es.get_assay_data_frame()[list(cols)]

    # Unpack data
    x_train = tr_es.as_matrix()
    # x_train = train_es.get_assay_data_frame().as_matrix().transpose()
    y_train = train_es.get_pheno_data_frame()[target_class_column].as_matrix()

    x_test = te_es.as_matrix()
    # x_test = test_es.get_assay_data_frame().as_matrix().transpose()
    y_test = test_es.get_pheno_data_frame()[target_class_column].as_matrix()

    # Unfortunately svm can't operate with string labels as a target classes
    #   so we need to preprocess labels
    le = preprocessing.LabelEncoder()
    le.fit(y_train)

    y_train_fixed = le.transform(y_train)
    y_test_fixed = le.transform(y_test)

    # Classifier initialization
    fabric, apply_func = classifiers_map[classifier_name]
    # log.debug("Classifier options: %s", classifier_options)
    if apply_func is None:
        cl = get_classifier(fabric, classifier_options, classifier_name, block)
        log.debug("Fitting classifier.")
        try:
            log.debug(str(x_train))
            cl.fit(x_train, y_train_fixed)
        except ValueError:
            # if settings.CELERY_DEBUG:
            #     import sys
            #     sys.path.append('/Migration/skola/phd/projects/miXGENE/mixgene_project/wrappers/pycharm-debug.egg')
            #     import pydevd
            #     pydevd.settrace('localhost', port=6901, stdoutToServer=True, stderrToServer=True)
            log.debug(str(x_train))
            raise
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



def apply_ncf_classifier(
    exp, block,
    mRNA_train_es, mRNA_test_es, miRNA_train_es, miRNA_test_es,
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

    target_class_column = mRNA_train_es.pheno_metadata["user_class_title"]
    mRNA_tr_es = mRNA_train_es.get_assay_data_frame()
    miRNA_tr_es = miRNA_train_es.get_assay_data_frame()

    mRNA_cols = mRNA_tr_es.columns
    miRNA_cols = miRNA_tr_es.columns

    mRNA_te_es = mRNA_test_es.get_assay_data_frame()[list(mRNA_cols)]
    miRNA_te_es = miRNA_test_es.get_assay_data_frame()[list(miRNA_cols)]

    # Unpack data
    x_mRNA_train = mRNA_tr_es.as_matrix()
    x_miRNA_train = miRNA_tr_es.as_matrix()

    y_train = mRNA_train_es.get_pheno_data_frame()[target_class_column].as_matrix()

    x_mRNA_test = mRNA_te_es.as_matrix()
    x_miRNA_test = miRNA_te_es.as_matrix()

    y_test = miRNA_test_es.get_pheno_data_frame()[target_class_column].as_matrix()

    # Unfortunately svm can't operate with string labels as a target classes
    #   so we need to preprocess labels
    le = preprocessing.LabelEncoder()
    le.fit(y_train)

    y_train_fixed = le.transform(y_train)
    y_test_fixed = le.transform(y_test)
    classifier_options["mRNA_train_es"] = mRNA_tr_es
    classifier_options["miRNA_train_es"] = miRNA_tr_es

    # Classifier initialization
    fabric, apply_func = classifiers_map[classifier_name]
    # log.debug("Classifier options: %s", classifier_options)
    if apply_func is None:
        cl = get_classifier(fabric, classifier_options, classifier_name, block)
        log.debug("Fitting classifier.")
        cl.fit(x_mRNA_train, y_train_fixed, x_miRNA_train)
        log.debug("Finished fitting classifier.")
    else:
        raise NotImplementedError()

    log.debug("Applying on test.")
    # Applying on test partition
    y_test_predicted = cl.predict(x_mRNA_test, x_miRNA_test)
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
