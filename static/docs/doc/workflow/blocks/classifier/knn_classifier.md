
[Home](../../../index.html) > [Categories](../../index.html) > [Classifier](index.html)

# KNN classifier

* Category: Classifier

## Inputs

* train_es [[ExpressionSet](../../../data_types.html#expressionset)]
* test_es [[ExpressionSet](../../../data_types.html#expressionset)]

## Parameters

* Number of neighbors
* Algorithm [optional]
* Leaf size for BallTree or KDTree [optional]
* The distance metric to use for the tree [optional]

## Outputs

* result [[ClassifierResult](../../../data_types.html#classifierresult)]

## Description

  k-nearest neighbor classifier, each instance is assigned a class label which prevails in its neighborhood in the feature space, e.g., a biological sample/array is assigned the phenotype that occurs most frequently in k training samples/arrays whose feature vectors lie nearest to the feature vector of the sample (expression profile, methylation profile, etc.)

## Examples of Usage
        