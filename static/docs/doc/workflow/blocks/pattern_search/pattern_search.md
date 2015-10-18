
[Home](../../../index.html) > [Categories](../../index.html) > [Pattern Search](index.html)

# Pattern search

* Category: Pattern Search

## Inputs

* *mRNA [[ExpressionSet](../../../data_types.html#expressionset)]*
* *miRNA [[ExpressionSet](../../../data_types.html#expressionset)]*
* *gene2gene [[BinaryInteraction](../../../data_types.html#binaryinteraction)]*
* *miRNA2gene [[BinaryInteraction](../../../data_types.html#binaryinteraction)]*

## Parameters

* *Metric* - phenotype-correlation statistic
* *d* - the maximum diameter from the current pattern where to search for the next nodes
* *Minimal improvementa * - the minimal ratio of the old pattern statistic and the new patterns statistic to accept the new found patterns

## Outputs

* *patterns[[ComoduleSet](../../../data_types.html#comoduleset)]*

## Description

  searches for differentially expressed patterns (comodules) in mRNA-miRNA datasets, the user uploads mRNA and miRNA expression sets, provides the corresponding protein-protein binary interactions (PPI) and miRNA targets, then the method of is applied to identify feature subnetworks with distinct expression profiles in different phenotypes

## Examples of Usage
        