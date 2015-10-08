
[Home](index.html)
# Data Types

# TableResult
a two-dimensional table, serves for reporting the results, in miXGENE mainly used to deliver a feature table with specific numericqal characteristics, formally, Pnadas data frame
# GeneSets
groups of omics units that share a common characteristic (typically biological function, chromosomal location, regulation or relation to a specific disease), formally a dictionary where the key corresponds to the shared characteristic/term and the value is a set of omics units
# Edges
bude nahrazen DictionarySet
# DiffExpr
a list of pairs (genomic unit and its real deregulation coefficient), the coefficient is -1 for the most downregulated unit and +1 for  the most upregulated unit, the values are scaled wrt to the related ExpressionSet
# DictionarySet
a dictionary storing pairs (key, value), where the value can be a list of lists, a typical example is a set of comodules (keys correspond to their ordinal numbers) characterized by the set of their members (mRNAs, miRNAs, methylation islands) and the list of thier enriched terms with the corresponding p-values
# BinaryInteraction
represents an interaction network, a set of binary interactions between omics units such as mRNA, miRNA and methylation islands 
# ComoduleSet
bude nahrazen DictionarySet
# ExpressionSet
the core data structure for expression analysis, it combines expression data (a real 2D array), phenotypes (a 2D array of labels) and all related additional information. It is implemented under the influence of ExpressionSet class from Bioconductor library
# ClassifierResult
a 1D vector of predictions reached by the application of the given classifier to the given sample set (typically ExpressionSet)
# ResultsContainer
a container storing the results originated from iterative meta-blocks, the individual items correspond to the individual runs of the meta-block such as cross-validation folds or the individual datasets in bunch upload, the individual items of the container are typically ClassiifierResults



