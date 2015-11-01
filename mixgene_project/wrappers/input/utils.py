import mygene
import re
from webapp.models import GeneIdentifier, Refseq, GEOTerm

__author__ = 'pavel'

gene_cache = {}


def expand_inters(protein_refseq1, protein_refseq2, value):
    """ Called for each original interaction
        (protein_refseq1, protein_refseq2) and returns partial list of
        new interactions, which is used in the next call :-)
    """
    mg = mygene.MyGeneInfo()
    res1 = Refseq.objects.filter(gene_identifier_name__name__in=[protein_refseq1])
    res2 = Refseq.objects.filter(gene_identifier_name__name__in=[protein_refseq1])
    exp_inters = []

    for refseq in res1:
        if refseq.gene_identifier_name.name in gene_cache:
            gene_cache[refseq.gene_identifier_name.name].add(refseq.refseq)
        else:
            gene_cache[refseq.gene_identifier_name.name] = set([refseq.refseq])

    for refseq in res2:
        if refseq.gene_identifier_name.name in gene_cache:
            gene_cache[refseq.gene_identifier_name.name].add(refseq.refseq)
        else:
            gene_cache[refseq.gene_identifier_name.name] = set([refseq.refseq])

    if protein_refseq1 in gene_cache:
        exp_transcripts1 = list(gene_cache[protein_refseq1])
    else:
        try:
            exp_transcripts1 = mg.query(str(protein_refseq1), species='human', fields='refseq')['hits']
            if len(exp_transcripts1) == 0:
                exp_transcripts1 = [protein_refseq1]
            else:
                exp_transcripts1 = exp_transcripts1[0]['refseq']['rna']
        except:
            exp_transcripts1 = [protein_refseq1]

    if protein_refseq2 in gene_cache:
        exp_transcripts2 = list(gene_cache[protein_refseq2])
    else:
        try:
            exp_transcripts2 = mg.query(str(protein_refseq2), species='human', fields='refseq')['hits']
            if len(exp_transcripts2) == 0:
                exp_transcripts2 = [protein_refseq2]
            else:
                exp_transcripts2 = exp_transcripts2[0]['refseq']['rna']
        except:
            exp_transcripts2 = [protein_refseq2]

    for trans1 in exp_transcripts1:
        for trans2 in exp_transcripts2:
            exp_inters.append([trans1, trans2, value])
    return exp_inters


def find_refseq(gene):
    # Returns set of RefSeqs
    mg = mygene.MyGeneInfo()
    out = set()
    res = Refseq.objects.filter(gene_identifier_name__name__in=gene_set)

    if res:
        return res[0].refseq
    else:
        if gene in gene_cache:
            return gene_cache[gene]
        else:
            exp = mg.query(str(gene), species='human', fields='refseq')['hits']
            if len(exp) > 0:
                try:
                    refseqs = exp[0]['refseq']['rna']
                    gene_cache[gene] = set()
                    if not isinstance(refseqs, basestring):
                        for refseq in refseqs:
                            entrez, created = GeneIdentifier.objects.get_or_create(name=gene)
                            entrez.refseq_set.create(refseq=refseq)
                            gene_cache[gene].add(refseq)
                            return refseq
                    else:
                        entrez, created = GeneIdentifier.objects.get_or_create(name=gene)
                        entrez.refseq_set.create(refseq=refseqs)
                        gene_cache[gene].add(refseqs)
                        return refseqs
                except KeyError:
                    pass
    return None


def expand_geneset(gene_set):
    # Returns set of RefSeqs
    mg = mygene.MyGeneInfo()
    out = set()
    res = Refseq.objects.filter(gene_identifier_name__name__in=gene_set)

    # out.append(res)
    found_genes = set()
    for refseq in res:
        found_genes.add(refseq.gene_identifier_name.name)
        out.add(refseq.refseq)
        if refseq.gene_identifier_name.name in gene_cache:
            gene_cache[refseq.gene_identifier_name.name].add(refseq.refseq)
        else:
            gene_cache[refseq.gene_identifier_name.name] = set([refseq.refseq])
    for i, gene in enumerate(set(gene_set) - set(found_genes)):
        if gene in gene_cache:
            out.add(gene_cache[gene])
        else:
            exp = mg.query(str(gene), species='human', fields='refseq')['hits']
            if len(exp) > 0:
                try:
                    refseqs = exp[0]['refseq']['rna']
                    gene_cache[gene] = set()
                    if not isinstance(refseqs, basestring):
                        for refseq in refseqs:
                            entrez, created = GeneIdentifier.objects.get_or_create(name=gene)
                            entrez.refseq_set.create(refseq=refseq)
                            gene_cache[gene].add(refseq)
                            out.add(refseq)
                    else:
                        entrez, created = GeneIdentifier.objects.get_or_create(name=gene)
                        entrez.refseq_set.create(refseq=refseqs)
                        gene_cache[gene].add(refseqs)
                        out.add(refseqs)
                except KeyError:
                    pass
    return out
    # return frozenset().union(*out)


def find_target_column(regex, gpl_data):
    columns_gpl = list(gpl_data)
    freqs = {column: len(filter(lambda x: x is not None,
                                map(lambda x: re.match(regex, str(x), re.IGNORECASE), gpl_data[column].values[:1000])))
             for column in columns_gpl}
    max_key = max(freqs.keys(), key=(lambda key: freqs[key]))
    return max_key
