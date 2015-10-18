
[Home](../../../index.html) > [Categories](../../index.html) > [Filter](index.html)

# Pattern filter

* Category: Filter

## Inputs

* *mRNA [[ExpressionSet](../../../data_types.html#expressionset)]*
* *miRNA [[ExpressionSet](../../../data_types.html#expressionset)]*
* *cs [[ComoduleSet](../../../data_types.html#comoduleset)]*

## Parameters

* *Metric* - phenotype-correlated for selecting the best patterns
* *# of best* - number of the best selected patterns

## Outputs

* *patterns[[ComoduleSet](../../../data_types.html#comoduleset)]*

## Description

  evaluates the modules (patterns) by an arbitrary statistic (namely related to the one used in pattern-search block), and eventually releases the top scoring modules. The evaluation is based on GE metaprofile of each module. Therefore another input, i.e. expression set, is necessary. 

## Examples of Usage
        