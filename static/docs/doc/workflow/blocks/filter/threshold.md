
[Home](../../../index.html) > [Categories](../../index.html) > [Filter](index.html)

# Threshold

* Category: Filter

## Inputs

* *es [[ExpressionSet](../../../data_types.html#expressionset)]*

## Parameters

* *Threshold* - the minimum intensity value of the basis matrix which determines a feature as belonging to the respective module (factor)

## Outputs

* *comodule_set[[ComoduleSet](../../../data_types.html#comoduleset)]*

## Description

  takes a set of mRNA comodules (a matrix that gives a membership value for each gene and each comodule), presumably the output of NIMFA SNMNMF block, for each comodule enumerates all the genes whose comodule membership is higher than a user defined threshold RENAME: es -> H2_genes

## Examples of Usage
        