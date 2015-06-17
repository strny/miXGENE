__author__ = 'pavel'

import mygene
import re

def expand_inters(protein_refseq1, protein_refseq2, value):
    """ Called for each original interaction
        (protein_refseq1, protein_refseq2) and returns partial list of
        new interactions, which is used in the next call :-)
    """
    exp_inters = []
    mg = mygene.MyGeneInfo()
    exp_transcripts1 = mg.query(str(protein_refseq1), species='human', fields='refseq')['hits']
    if len(exp_transcripts1) == 0:
        exp_transcripts1 = [protein_refseq1]
    else:
        exp_transcripts1 = exp_transcripts1[0]['refseq']['rna']
    exp_transcripts2 = mg.query(str(protein_refseq2), species='human', fields='refseq')['hits']
    if len(exp_transcripts2) == 0:
        exp_transcripts2 = [protein_refseq2]
    else:
        exp_transcripts2 = exp_transcripts2[0]['refseq']['rna']

    for trans1 in exp_transcripts1:
        for trans2 in exp_transcripts2:
            exp_inters.append([trans1, trans2, value])
    return exp_inters


def expand_geneset(gene_set):
    mg = mygene.MyGeneInfo()
    return frozenset().union(*[mg.query(str(gene), species='human', fields='refseq')['hits'][0]['refseq']['rna']
                               for gene in gene_set])


def find_target_column(regex, gpl_data):
    columns_gpl = list(gpl_data)
    freqs = {column: len(filter(lambda x: x is not None, map(lambda x: re.match(regex, str(x), re.IGNORECASE), gpl_data[column].values[:1000])))
             for column in columns_gpl}
    max_key = max(freqs.keys(), key=(lambda key: freqs[key]))
    return max_key
