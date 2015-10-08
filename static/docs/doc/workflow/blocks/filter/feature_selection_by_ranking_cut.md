
[Home](../../../index.html) > [Categories](../../index.html) > [Filter](index.html)

# Feature selection by ranking cut

* Category: Filter

## Inputs

* es [[ExpressionSet](../../../data_types.html#expressionset)]
* rank_table [[TableResult](../../../data_types.html#tableresult)]

## Parameters

* Ranking property to use
* Threshold for cut
* Direction of cut

## Outputs

* es [[ExpressionSet](../../../data_types.html#expressionset)]

## Description

  selects the best ranked features from an expression set, the features have previously been scored by a test (e.g., t-test) and ranked by Ranking, keeps only those features that meet a certain threshold, allows the application of the test on training data while the cut can be applied to testing data

## Examples of Usage
        