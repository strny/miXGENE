
[Home](../../../index.html) > [Categories](../../index.html) > [Feature Aggregation](index.html)

# SVD aggregation

* Category: Feature Aggregation

## Inputs

* mRNA_es [[ExpressionSet](../../../data_types.html#expressionset)]
* miRNA_es [[ExpressionSet](../../../data_types.html#expressionset)]
* interaction [[BinaryInteraction](../../../data_types.html#binaryinteraction)]

## Parameters

* Constant c

## Outputs

* agg_es[[ExpressionSet](../../../data_types.html#expressionset)]

## Description

  the method for mRNA and miRNA data aggregation based on the known miRNA targets, despite its sister approach, the subtractive aggregation method, the given mRNA and all its targeting miRNAs get reduced into one feature by singular value decomposition (SVD)

## Examples of Usage
        