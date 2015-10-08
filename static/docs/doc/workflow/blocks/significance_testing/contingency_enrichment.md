
[Home](../../../index.html) > [Categories](../../index.html) > [Significance Testing](index.html)

# Contingency enrichment

* Category: Significance Testing

## Inputs

* gs [[GeneSets](../../../data_types.html#genesets)]
* cs [[ComoduleSet](../../../data_types.html#comoduleset)]

## Parameters

* Enrichment threshold

## Outputs

* dictionary_set[[DictionarySet](../../../data_types.html#dictionaryset)]

## Description

  takes a set of comodules, the thresholded output of NIMFA SNMNMF block, and analyzes their enrichment in terms of the provided set of gene sets (GO terms, KEGG pathways, etc.), for all the comodules it reports the gene sets whose enrichment is larger than the user defined enrichment threshold

## Examples of Usage
        