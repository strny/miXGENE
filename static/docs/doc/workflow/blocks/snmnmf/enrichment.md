
[Home](../../../index.html) > [Categories](../../index.html) > [SNMNMF](index.html)

# Enrichment

* Category: SNMNMF

## Inputs

* *gs [[GeneSets](../../../data_types.html#genesets)]*
* *H2_genes [[ExpressionSet](../../../data_types.html#expressionset)]*

## Parameters

* *Parameter T* - determines the specificity of a commodule to the particular gene set

## Outputs

* *dictionary_set[[DictionarySet](../../../data_types.html#dictionaryset)]*

## Description

  takes a set of mRNA comodules (a matrix that gives a membership value for each gene and each comodule), presumably the thresholded output of NIMFA SNMNMF block, and analyzes their enrichment in terms of the provided set of gene sets (GO terms, KEGG pathways, etc.), for all the comodules it reports the gene sets whose enrichment is larger than the user defined enrichment threshold

## Examples of Usage
        