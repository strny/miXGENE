
[Home](../../../index.html) > [Categories](../../index.html) > [Classifier](index.html)

# Linear SVM classifier

* Category: Classifier

## Inputs

* train_es [[ExpressionSet](../../../data_types.html#expressionset)]
* test_es [[ExpressionSet](../../../data_types.html#expressionset)]

## Parameters

* Penalty
* Tolerance for stopping criteria
* The loss function

## Outputs

* result [[ClassifierResult](../../../data_types.html#classifierresult)]

## Description

  Support Vector Machines (SVM) represent a class of accurate and noise robust linear classifiers, they split data by the hyperplane with the largest margin, i.e., the largest distance to the nearest training points called support vectors, note: one of the kernels in kernel SVM can be linear, this dedicated linear SVM is supposed to be more efficiently implemented than the generic kernel one

## Examples of Usage
        