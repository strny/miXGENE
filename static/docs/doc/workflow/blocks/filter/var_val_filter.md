
[Home](../../../index.html) > [Categories](../../index.html) > [Filter](index.html)

# Var/Val filter

* Category: Filter

## Inputs

* *es [[ExpressionSet](../../../data_types.html#expressionset)]*

## Parameters

* *Threshold* - the minimal percentile to filter the features
* *Filter method* - whether to filter according to the maximum absolute value or variance of the features

## Outputs

* *flt_es[[ExpressionSet](../../../data_types.html#expressionset)]*

## Description

  takes an expression set and removes all the features whose variance is below a percentile threshold or whose all values are lower than a percentile threshold, the percentile is defined by the user, the actual threshold is the value that corresponds to the percentile in the given expression set, both the expression profiles with low variance and low intensity near the background level indicate irrelevant features, the outcome is a reduced expression set

## Examples of Usage
        