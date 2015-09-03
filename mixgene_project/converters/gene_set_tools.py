import traceback
from celery import task
import sys
import logging
from environment.structures import GeneSets, GS
from environment.units import GeneUnits

from mixgene.util import transpose_dict_list

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


def preprocess_df_gs(df, src_gs):
    cols = df.columns

    # We must rename cols to be unique for R
    out_genes = {}
    out_cols = []
    for i, g in enumerate(cols):
        g = g.split('.')[0]
        if g in out_genes:
            new_g = g + '__' + str(i)
            out_genes[g].append(new_g)
            out_cols.append(new_g)
        else:
            out_genes[g] = [g]
            out_cols.append(g)
    df.columns = out_cols

    genes_in_es = df.columns

    # We must appropriately rename genes in genesets
    for k, gene_set in src_gs.genes.iteritems():
        out_gs = []
        for gene in gene_set:
            if gene in out_genes:
                out_gs = out_gs + out_genes[gene]
            else:
                out_gs.append(gene)
        src_gs.genes[k] = out_gs

    gs_filtered = filter_gs_by_genes(src_gs, genes_in_es)
    return df, gs_filtered

def map_gene_sets_to_probes(exp, block,
                            base_dir, base_filename, ann_gene_sets, src_gene_sets):
    """
    TODO: working units check

    @param filepath: Filepath to store result obj

    @type ann_gs: GeneSets
    @type gs: GeneSets

    @rtype: GeneSets
    """
    entrez_ids_to_probes_map = transpose_dict_list(ann_gene_sets.get_gs().genes)

    gene_sets_probes = GeneSets(base_dir, base_filename)

    gene_sets_probes.metadata["org"] = src_gene_sets.metadata["org"]
    gene_sets_probes.metadata["gene_units"] = GeneUnits.PROBE_ID
    gene_sets_probes.metadata["set_units"] = src_gene_sets.metadata["set_units"]
    gs = GS()
    src_gs = src_gene_sets.get_gs()
    for set_name, gene_ids in src_gs.genes.iteritems():
        tmp_set = set()
        for entrez_id in gene_ids:
            tmp_set.update(entrez_ids_to_probes_map.get(entrez_id ,[]))
        if tmp_set:
            gs.genes[set_name] = list(tmp_set)
            gs.description[set_name] = src_gs.description[set_name]

    gene_sets_probes.store_gs(gs)
    return [gene_sets_probes], {}


def filter_gs_by_genes(src_gs, allowed_genes):
    """
    @type src: environment.structures.GS

    @type allowed_genes: list of strings
    @param allowed_genes: gene units in allowed_genes and src should be the same

    @rtype: environment.structures.GS
    """

    allowed = set(allowed_genes)
    gs = GS()
    for k, gene_set in src_gs.genes.iteritems():
        to_preserve = set(gene_set).intersection(allowed)
        if to_preserve:
            gs.genes[k] = list(to_preserve)
            gs.description[k] = src_gs.description
    return gs
