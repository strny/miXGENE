
[Home](../../../index.html) > [Categories](../../index.html) > [SNMNMF](index.html)

# NIMFA SNMNMF

* Category: SNMNMF

## Inputs

* *mRNA [[ExpressionSet](../../../data_types.html#expressionset)]*
* *miRNA [[ExpressionSet](../../../data_types.html#expressionset)]*
* *Gene2Gene [[BinaryInteraction](../../../data_types.html#binaryinteraction)]*
* *miRNA2gene [[BinaryInteraction](../../../data_types.html#binaryinteraction)]*

## Parameters

* *l1* - strength of the regularization by the protein-protein interactions
* *l2* - strength of the regularization by the miRNA-mRNA interaction
* *g1* - a parameter inducing the sparse coding
* *g2* - the sparsity inducing parameter
* *rank* - number of commodules

## Outputs

* *H2_genes[[ExpressionSet](../../../data_types.html#expressionset)]*
* *W[[ExpressionSet](../../../data_types.html#expressionset)]*
* *H1_miRNA[[ExpressionSet](../../../data_types.html#expressionset)]*

## Description

  implements the method of network-regularized multiple non-negative matrix factorization (SNMNMF). a data integration method to identify the miRNA–gene regulatory comodules, the method stems from mRNA and miRNA expression sets including their prior known interactions and generates a set of matrices vaguely representing regulatory comodules, i.e., the sets of mRNAs and miRNAs that tend to agree in their expression profiles and interact in terms of the prior knowledge

## Examples of Usage
        