
[Home](../../../index.html) > [Categories](../../index.html) > [Feature Aggregation](index.html)

# Gene set aggregation

* Category: Feature Aggregation

## Inputs

* es [[ExpressionSet](../../../data_types.html#expressionset)]
* gs [[GeneSets](../../../data_types.html#genesets)]

## Parameters

* Aggregate method

## Outputs

* agg_es [[ExpressionSet](../../../data_types.html#expressionset)]

## Description

  transforms the original expression set into an expression set where the original features get replaced by the feature groups, an example: gs field may define a set of pathways, the original expression probes get aggregated over the pathways using the selected aggregate method, i.e., a single value is produced per each pathway and biological sample/array, the value represents for example the mean value for all the probes falling into the given pathway in the given sample/array

## Examples of Usage
        