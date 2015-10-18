
[Home](../../../index.html) > [Categories](../../index.html) > [Filter](index.html)

# Filter ES by interaction

* Category: Filter

## Inputs

* *mRNA_es [[ExpressionSet](../../../data_types.html#expressionset)]*
* *miRNA_es [[ExpressionSet](../../../data_types.html#expressionset)]*
* *interaction [[BinaryInteraction](../../../data_types.html#binaryinteraction)]*

## Parameters



## Outputs

* *mi_rna_filtered_es[[ExpressionSet](../../../data_types.html#expressionset)]*
* *m_rna_filtered_es[[ExpressionSet](../../../data_types.html#expressionset)]*

## Description

  takes mRNA and miRNA expression sets and the set of their binary interactions and filters out all the mRNAs and miRNAs that do not interact with any of its counterparts (i.e., mRNAs that do not make target of an miRNA and miRNAs that do not target any mRNA), returns the filtered mRNA and miRNA expression sets, serves mainly to reduce the feature sets when  testing the performance of integration methods where the entities without interaction play a minor role only

## Examples of Usage
        