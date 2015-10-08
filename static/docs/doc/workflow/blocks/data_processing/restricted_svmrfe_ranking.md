
[Home](../../../index.html) > [Categories](../../index.html) > [Data Processing](index.html)

# Restricted SVMRFE ranking

* Category: Data Processing

## Inputs



## Parameters



## Outputs



## Description

  takes an expression set including the definition of phenotype and ranks its features by their importance for SVM accuracy, SVM is repeatedly run, the algorithm starts with all the features and recursively removes the least useful features, the other features are retained and used in next run (RFE stands for recursive feature elimination), finally a feature ranking is produced, the number of features given by "Consider only best" is preserved eventually, when this field remains void all the features are kept, as Restricted SVMRFE ranking removes more features at once, it is faster than SVMRFE ranking, but it can be less accurate when detecting feature interactions

## Examples of Usage
        