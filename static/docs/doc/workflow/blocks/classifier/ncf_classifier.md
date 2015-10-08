
[Home](../../../index.html) > [Categories](../../index.html) > [Classifier](index.html)

# NCF classifier

* Category: Classifier

## Inputs

* train_es [[ExpressionSet](../../../data_types.html#expressionset)]
* test_es [[ExpressionSet](../../../data_types.html#expressionset)]
* gene2gene [[BinaryInteraction](../../../data_types.html#binaryinteraction)]
* miRNA2gene [[BinaryInteraction](../../../data_types.html#binaryinteraction)]

## Parameters

* The number of trees in the forest
* Walk max length
* The function to measure quality of split
* Eps
* The maximum depth of the tree
* The minimum number of samples to split an internal node
* The minimum number of samples to be at a leaf node
* bootstrap

## Outputs

* result [[ClassifierResult](../../../data_types.html#classifierresult)]

## Description

  Network-Constrained Forest (NCF) classifier, a modified random forest classifier in which the features in the individual trees are not sampled randomly but by a probability distribution stemming from a feature interaction network, the features that appear close to each other in the network tend to appear in the same weak classifiers

## Examples of Usage
        