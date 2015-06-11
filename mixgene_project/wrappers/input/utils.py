__author__ = 'pavel'

import mygene


def expand_inters(protein_refseq1, protein_refseq2, exp_inters=[]):
    """ Called for each original interaction
        (protein_refseq1, protein_refseq2) and returns partial list of
        new interactions, which is used in the next call :-)
    """
    mg = mygene.MyGeneInfo()
    exp_transcripts1 = mg.query(str(protein_refseq1), species='human', fields='refseq')['hits'][0]['refseq']
    exp_transcripts2 = mg.query(str(protein_refseq2), species='human', fields='refseq')['hits'][0]['refseq']

    for trans1 in exp_transcripts1:
        for trans2 in exp_transcripts2:
            exp_inters.append([trans1, trans2])
    return exp_inters


def expand_geneset(gene_set):
    mg = mygene.MyGeneInfo()
    return frozenset().union(*[mg.query(str(gene), species='human', fields='refseq')['hits'][0]['refseq']
                               for gene in gene_set])
