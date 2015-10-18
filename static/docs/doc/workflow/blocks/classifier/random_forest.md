
[Home](../../../index.html) > [Categories](../../index.html) > [Classifier](index.html)

# Random forest

* Category: Classifier

## Inputs

* *train_es [[ExpressionSet](../../../data_types.html#expressionset)]*
* *test_es [[ExpressionSet](../../../data_types.html#expressionset)]*

## Parameters

* *The number of trees in the forest* - size of the ensemble
* *The function to measure the quality of a split* - phenotype-correlation statistic
* *The maximum depth of the tree* - determines how much to shatter the data
* *The minimum number of samples to split an internal node* - determines how much to shatter the data
* *The minimum number of samples to be at a leaf node* - determines how much to shatter the data

## Outputs

* *result [[ClassifierResult](../../../data_types.html#classifierresult)]*

## Description

  an ensemble classification algorithm that constructs multiple decision trees at the same time, the final decision is given by the mode of the classes predicted by the individual trees

## Examples of Usage
        