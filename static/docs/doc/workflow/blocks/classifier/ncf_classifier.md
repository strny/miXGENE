
[Home](../../../index.html) > [Categories](../../index.html) > [Classifier](index.html)

# NCF classifier

* Category: Classifier

## Inputs

* *train_es [[ExpressionSet](../../../data_types.html#expressionset)]*
* *test_es [[ExpressionSet](../../../data_types.html#expressionset)]*
* *gene2gene [[BinaryInteraction](../../../data_types.html#binaryinteraction)]*
* *miRNA2gene [[BinaryInteraction](../../../data_types.html#binaryinteraction)]*

## Parameters

* *The number of trees in the forest* - size of the ensemble
* *Walk max length* - length of the random walk (the key bias parameter)
* *The function to measure quality of split* - phenotype-correlation statistic
* *Eps* - parameter of the heuiristic for learning the optimal walk length
* *The maximum depth of the tree* - key parameter for learning the optimal walk length
* *The minimum number of samples to split an internal node* - determines how much to shatter the data
* *The minimum number of samples to be at a leaf node* - determines how much to shatter the data
* *bootstrap* - whether to subsample the data examples

## Outputs

* *result [[ClassifierResult](../../../data_types.html#classifierresult)]*

## Description

  Network-Constrained Forest (NCF) classifier, a modified random forest classifier in which the features in the individual trees are not sampled randomly but by a probability distribution stemming from a feature interaction network, the features that appear close to each other in the network tend to appear in the same weak classifiers

## Examples of Usage
        