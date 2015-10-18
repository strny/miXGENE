
[Home](../../../index.html) > [Categories](../../index.html) > [Meta Block](index.html)

# Cross-validation K-fold

* Category: Meta Block

## Inputs

* *New input field [[ExpressionSet](../../../data_types.html#expressionset)]*

## Parameters

* *Folds number* - the number of disjoint subsets the data are split into
* *Repeats number* - the number cross-validation runs on differently splitted data

## Outputs

* *results_container[[ResultsContainer](../../../data_types.html#resultscontainer)]*

## Description

  cross-validation is a model validation technique, it is used to assess the accuracy of the model on independent dataset, it is used namely for small datasets where it is not advisable to split into training and testing data only, the user sets the input expression set, the number of folds to split in and the number of repeated runs of cross-validation to minimize the random component in the accuracy estimate when working with unstable models influenced by randomly perturbed folds, the final estimate is the mean accuracy reached over multiple cross-validation runs

## Examples of Usage
        