
[Home](../../../index.html) > [Categories](../../index.html) > [Classifier](index.html)

# Decision tree

* Category: Classifier

## Inputs

* *train_es [[ExpressionSet](../../../data_types.html#expressionset)]*
* *test_es [[ExpressionSet](../../../data_types.html#expressionset)]*

## Parameters

* *The function to measure the quality of a splitclass-correlation statistic
* *The maximum depth of the tree* - phenotype-correlation statistic
* *The minimum number of samples to split an internal node* - determines how much to shatter the data
* *The minimum number of samples to be at a leaf node* - determines how much to shatter the data

## Outputs

* *result [[ClassifierResult](../../../data_types.html#classifierresult)]*

## Description

  learns a decision tree, each internal tree node represents a test on a feature (typically binary, e.g., whether an expression value exceeds a threshold), each branch corresponds to the outcome of the test and each leaf node represents a class label that makes the final decision after passing all the tests

## Examples of Usage
        