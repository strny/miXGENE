
[Home](../../../index.html) > [Categories](../../index.html) > [Data Processing](index.html)

# SVMRFE ranking

* Category: Data Processing

## Inputs

* es [[ExpressionSet](../../../data_types.html#expressionset)]

## Parameters

* Consider only best

## Outputs

* result [[TableResult](../../../data_types.html#tableresult)]

## Description

  takes an expression set including the definition of phenotype and ranks its features by their importance for SVM accuracy, SVM is repeatedly run, the algorithm starts with all the features and recursively removes the least useful feature, the other features are retained and used in next run (RFE stands for recursive feature elimination), finally a feature ranking is produced, the number of features given by "Consider only best" is preserved eventually, when this field remains void all the features are kept

## Examples of Usage
        