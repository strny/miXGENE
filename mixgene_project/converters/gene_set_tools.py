from celery import task
from environment.structures import GeneSets, GmtStorage
from environment.units import GeneUnits

from mixgene.util import transpose_dict_list


def map_gene_sets_to_probes(annotation, gs):
    """
    @type annotation: environment.structures.PlatformAnnotation
    @type gs: environment.structures.GeneSets

    @rtype: environment.structures.GeneSets
    """
    ann_gs = annotation.get_gmt()
    entrez_ids_to_probes_map = transpose_dict_list(ann_gs.genes)

    gs_probes = GeneSets()
    gs_probes.org = gs.org
    gs_probes.units = GeneUnits.PROBE_ID
    for set_name, gene_ids in gs.genes.iteritems():
        tmp_set = set()
        for entrez_id in gene_ids:
            tmp_set.update(entrez_ids_to_probes_map.get(entrez_id ,[]))
        if tmp_set:
            gs_probes.genes[set_name] = list(tmp_set)
            gs_probes.description[set_name] = gs.description[set_name]

    return gs_probes


def filter_gs_by_genes(src, allowed_genes):
    """
    @type src: environment.structures.GeneSets

    @type allowed_genes: list of strings
    @param allowed_genes: gene units in allowed_genes and src should be the same

    @rtype: environment.structures.GeneSets
    """

    allowed = set(allowed_genes)
    gs = GeneSets()
    gs.org = src.org
    gs.units = src.units

    for k, gene_set in src.genes.iteritems():
        to_preserve = set(gene_set).intersection(allowed)
        if to_preserve:
            gs.genes[k] = list(to_preserve)
            gs.description[k] = src.description
    return gs

@task(name="converters.gene_set_tools.merge_gs_with_platform_annotation")
def merge_gs_with_platform_annotation(
        exp, block, store_field,
        gmt_storage_gs,
        annotation,
        filepath,
        success_action="success", error_action="error",
    ):
    """
        @type gmt_storage_gs: GmtStorage
        @type annotation: PlatformAnnotation
    """
    try:
        gs = gmt_storage_gs.load()
        gs_merged = map_gene_sets_to_probes(annotation, gs)

        gmts = GmtStorage(filepath)
        gmts.store(gs_merged)

        setattr(block, store_field, gmts)
        block.do_action(success_action, exp)
    except Exception, e:
        block.errors.append(e)
        block.do_action(error_action, exp)


