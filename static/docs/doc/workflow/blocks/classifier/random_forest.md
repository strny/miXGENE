
[Home](../../../index.html) > [Categories](../../index.html) > [Classifier](index.html)

# Random forest

* Category: Classifier

## Inputs

* train_es [[ExpressionSet](../../../data_types.html#expressionset)]
* test_es [[ExpressionSet](../../../data_types.html#expressionset)]

## Parameters

* The number of trees in the forest
* The function to measure the quality of a split
* The maximum depth of the tree.
* The minimum number of samples to split an internal node
* The minimum number of samples to be at a leaf node

## Outputs

* result [[ClassifierResult](../../../data_types.html#classifierresult)]

## Description

  an ensemble classification algorithm that constructs multiple decision trees at the same time, the final decision is given by the mode of the classes predicted by the individual trees

## Examples of Usage
        