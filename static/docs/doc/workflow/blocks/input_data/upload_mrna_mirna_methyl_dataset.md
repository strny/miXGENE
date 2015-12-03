
[Home](../../../index.html) > [Categories](../../index.html) > [Input Data](index.html)

# Upload mRna/miRna/methyl dataset

* Category: Input Data

## Inputs



## Parameters

* *mRNA expression* - a csv-like data table with header as gene or transcript IDs and index as sample IDs (or vice versa)
* *Platform ID* - NCBI platform identifier
* *Working unit* -  [used when platform is unknown]
* *Matrix orientation* - whether to consider the rows as samples and columns as features\
* *or vice versa
* *CSV separator symbol* - data entry delimiter
* *μRNA expression* - a csv-like data table with header as miRNA transcript IDs and index as sample IDs (or vice versa)
* *Platform ID* - NCBI platform identifier
* *Working unit * - [used when platform is unknown]
* *Matrix orientation* - whether to consider the rows as samples and columns as features\
* *or vice versa
* *CSV separator symboldata entry delimiter
* *Methylation Expression* - a csv-like data table with header as methylation island IDs IDs and index as sample IDs (or vice versa)
* *Platform ID* - NCBI platform identifier
* *Working unit* -  [used when platform is unknown]
* *Matrix orientation* - whether to consider the rows as samples and columns as features\
* *or vice versa
* *CSV separator symbol* - data entry delimiter

## Outputs

* *mi_rna_es[[ExpressionSet](../../../data_types.html#expressionset)]*
* *m_rna_es[[ExpressionSet](../../../data_types.html#expressionset)]*
* *methyl_es[[ExpressionSet](../../../data_types.html#expressionset)]*

## Description

  upload a user (expression) file, a file is supposed to be a rectangular matrix or their set, the user gives the type(s) of the matrix first (mRNA, miRNA, methylation, phenotype), orientation of the matrix and field separator

## Examples of Usage
        