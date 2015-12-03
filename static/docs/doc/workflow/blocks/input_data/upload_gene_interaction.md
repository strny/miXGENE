
[Home](../../../index.html) > [Categories](../../index.html) > [Input Data](index.html)

# Upload gene interaction

* Category: Input Data

## Inputs



## Parameters

* *Interaction file* - the interaction file in which the individual rows correspond to the individual binary interactions between units
* *Header* - whether the first line of the interaction file is the header (i.e. not to be cosidered for upload)
* *Data type* - interaction format i.e. whether the interactions have the form of 2-tuples or 3-tuples where the first two elements of a tuple are the omics units (both same
* *or distinct) and the third (if 3-tuple) is the real valued strength of this ineraction.
* *CSV separator symbol* - interaction delimiter

## Outputs

* *interaction [[BinaryInteraction](../../../data_types.html#binaryinteraction)]*

## Description

  upload user defined interactions, typically target interactions between mRNA and miRNA

## Examples of Usage
        