
[Home](../../../index.html) > [Categories](../../index.html) > [Classifier](index.html)

# Kernel SVM classifier

* Category: Classifier

## Inputs

* *train_es [[ExpressionSet](../../../data_types.html#expressionset)]*
* *test_es [[ExpressionSet](../../../data_types.html#expressionset)]*

## Parameters

* *Penalty* - the norm of coefficient regularization ('2' - standard SVM  '1' - sparse coeffficients)
* *Kernel type* - feature space adaptation
* *Degree of the polynomial kernel* - degree of the feature space expansion (1-3)
* *Kernel coefficient for RBF and Polynomial and Sigmoid* - kernel adaptation coefficient (if gamma is 0.0 then 1/n_features will be used instead)
* *Tolerance for stopping criteria* - when to stop the optimization

## Outputs

* *result [[ClassifierResult](../../../data_types.html#classifierresult)]*

## Description

  Support Vector Machines (SVM) represent a class of accurate and noise robust linear classifiers, they split data by the hyperplane with the largest margin, i.e., the largest distance to the nearest training points called support vectors, kernel SVM allows a non-linear classification by implicit mapping into another feature space

## Examples of Usage
        