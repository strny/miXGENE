import logging
import shutil
import gzip

import pandas as pd
from pandas import Series, DataFrame
from sklearn import cross_validation
from Bio.Geo import parse as parse_geo


from mixgene.util import prepare_GEO_ftp_url, fetch_file_from_url

from webapp.models import CachedFile
from environment.units import GeneUnits
from environment.structures import ExpressionSet, PlatformAnnotation, \
    GS, FileInputVar

from itertools import repeat, chain
from django.conf import settings

# TODO: invent magic to correct logging when called outside of celery task

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

# TODO: merge fetch_geo_gpl and fetch_geo_gse
def fetch_geo_gpl(exp, block, gpl_uid, ignore_cache=False):
    gpl_uid = gpl_uid.upper()
    file_format = "txt"
    url, compressed_filename, filename = prepare_GEO_ftp_url(gpl_uid, file_format)

    fi = FileInputVar("%s/%s_gpl.txt" % (exp.get_data_folder(), block.uuid), title="", description="")
    fi.is_done = True
    fi.is_being_fetched = False
    fi.file_extension = "txt"
    fi.is_gzipped = True
    fi.filename = filename

    fi.filepath = exp.get_data_file_path(fi.filename, fi.file_extension)
    fi.geo_uid = gpl_uid
    fi.geo_type = gpl_uid[:3]

    fi.file_format = "txt"
    fi.set_file_type("ncbi_geo")

    mb_cached = CachedFile.look_up(url)
    if mb_cached is None or ignore_cache:
        #FIME: grrrrrr...
        dir_path = exp.get_data_folder()
        fetch_file_from_url(url, "%s/%s" % (dir_path, filename + ".txt"))

        CachedFile.update_cache(url, fi.filepath)
    else:
        shutil.copy(mb_cached.get_file_path(), fi.filepath)
        log.debug("File for %s was copied file from cache", url)

    return fi


def fetch_geo_gse(exp, block, geo_uid, ignore_cache=False):
    file_format = "soft"
    geo_uid = geo_uid.upper()

    url, compressed_filename, filename = prepare_GEO_ftp_url(geo_uid, file_format)

    fi = FileInputVar("%s/%s_source.soft.gz" % (exp.get_data_folder(), block.uuid), title="", description="")
    fi.is_done = True
    fi.is_being_fetched = False
    fi.file_extension = "soft.gz"
    fi.is_gzipped = True
    fi.filename = filename

    fi.filepath = exp.get_data_file_path(fi.filename, fi.file_extension)
    fi.geo_uid = geo_uid
    fi.geo_type = geo_uid[:3]

    fi.file_format = file_format
    fi.set_file_type("ncbi_geo")

    mb_cached = CachedFile.look_up(url)
    if mb_cached is None or ignore_cache:
        # FIME: grrrrrr...
        dir_path = exp.get_data_folder()
        fetch_file_from_url(url, "%s/%s" % (dir_path, compressed_filename))

        CachedFile.update_cache(url, fi.filepath)
    else:
        shutil.copy(mb_cached.get_file_path(), fi.filepath)
        log.debug("File for %s was copied file from cache", url)

    return [fi], {}

def map_probes_to_refseqs(probes_to_refseq, probes_values):
    out = []
    for (probe, value) in probes_values:
        if probes_to_refseq[probe] != [""]:
            for refseq in probes_to_refseq[probe]:
                out.append((refseq, value))
    return out

import re
def preprocess_soft(exp, block, source_file):
    #TODO: now we assume that we get GSE file
    try:
        soft = list(parse_geo(gzip.open(source_file.filepath)))
    except:
        raise RuntimeError("Bad source file, can't read")

    assert soft[2].entity_type == "PLATFORM"

    pl = soft[2].table_rows
    id_idx = pl[0].index('ID')
    # entrez_idx = pl[0].index('ENTREZ_GENE_ID')
    refseq_idx = [i for i, item in enumerate(pl[0]) if re.search('.*refseq.*', item, re.IGNORECASE)]
    if refseq_idx == []:
        refseq_idx = [i for i, item in enumerate(pl[0]) if re.search('.*mirna.*', item, re.IGNORECASE)][0]
    else:
        refseq_idx = refseq_idx[0]


    probe_to_genes_GS = GS()
    for row in pl[1:]:
        probe_to_genes_GS.description[row[id_idx]] = ""
        probe_to_genes_GS.genes[row[id_idx]] = [row[refseq_idx].split(" /// ")[0]]

    # platform_annotation = PlatformAnnotation(
    #     "TODO:GET NAME FROM SOFT",
    #     base_dir=exp.get_data_folder(),
    #     base_filename="%s_annotation" % block.uuid
    # )
    #
    # platform_annotation.gene_sets.metadata["gene_units"] = GeneUnits.ENTREZ_ID
    # platform_annotation.gene_sets.metadata["set_units"] = GeneUnits.PROBE_ID
    # platform_annotation.gene_sets.store_gs(probe_to_genes_GS)

    if settings.CELERY_DEBUG:
        import sys
        sys.path.append('/Migration/skola/phd/projects/miXGENE/mixgene_project/wrappers/pycharm-debug.egg')
        import pydevd
        pydevd.settrace('localhost', port=6901, stdoutToServer=True, stderrToServer=True)

    id_ref_idx = soft[3].table_rows[0].index("ID_REF")
    value_idx = soft[3].table_rows[0].index("VALUE")
    assay_df = DataFrame(dict([
        (
            soft[i].entity_attributes['Sample_geo_accession'],
            Series(dict(
                map_probes_to_refseqs(probe_to_genes_GS.genes, [(row[id_ref_idx], row[value_idx]) for row in soft[i].table_rows[1:]])
            ))
        )
        for i in range(3, len(soft))
    ]))

    expression_set = ExpressionSet(exp.get_data_folder(), "%s_es" % block.uuid)
    expression_set.store_assay_data_frame(assay_df.T)

    raw_factors = [soft[i].entity_attributes
               for i in range(3, len(soft))]
    pheno_index = []

    # Here we trying to guess sub columns
    one_factor_row = raw_factors[0]
    pheno_complex_columns_def = {}
    for col_name, col in one_factor_row.iteritems():
        if type(col) in [str, unicode]:
            continue
        else:
            if all([":" in sub_col for sub_col in col]):
                mb_sub_col_names_sets = [
                    tuple(map(lambda x: x.split(":")[0], row[col_name]))
                    for row in raw_factors
                ]
                if len(set(mb_sub_col_names_sets)) == 1:
                    pheno_complex_columns_def[col_name] = "dict"
                else:
                    pheno_complex_columns_def[col_name] = "list"
            else:
                pheno_complex_columns_def[col_name] = "list"

    factors = []
    for idx, factor in enumerate(raw_factors):
        pheno_index.append(factor.pop('Sample_geo_accession', idx))
        factor.pop('sample_table_begin', None)
        factor.pop('sample_table_end', None)
        fixed_factor = {}
        for col_name, col in factor.iteritems():
            # Special treat for sub columns
            if col_name in pheno_complex_columns_def:
                if pheno_complex_columns_def[col_name] == "list":
                    for sub_idx, sub_col in enumerate(col):
                        fixed_factor["%s_%s" % (col_name, sub_idx + 1)] = sub_col
                elif pheno_complex_columns_def[col_name] == "dict":
                    for sub_col in col:
                        sub_name, sub_value = sub_col.split(":", 1)
                        fixed_factor["%s_%s" % (col_name, sub_name)] = sub_value

            else:
                fixed_factor[col_name] = col
        factors.append(fixed_factor)

    # TODO: add ordering to phenotype features

    pheno_df = DataFrame([Series(factor) for factor in factors], index=pheno_index)
    if expression_set.pheno_metadata["user_class_title"] not in pheno_df.columns:
        pheno_df[expression_set.pheno_metadata["user_class_title"]] = ""

    pheno_df.index.name = 'Sample_geo_accession'
    expression_set.store_pheno_data_frame(pheno_df)

    return [expression_set], {}



def generate_cv_folds(
        exp, block,
        folds_num,
        es_dict, inner_output_es_names_map,
        repeats_num=1,
        success_action="success", error_action="error",
    ):
    """
        @type es_dict: dict
        @param es_dict: {input_name -> ExpressionSet}

        @type inner_output_es_names_map: dict
        @param inner_output_es_names_map: input field name ->
            (inner output name train, inner output name test)
    """
    #
    # if settings.CELERY_DEBUG:
    #     import sys
    #     sys.path.append('/Migration/skola/phd/projects/miXGENE/mixgene_project/wrappers/pycharm-debug.egg')
    #     import pydevd
    #     pydevd.settrace('localhost', port=6901, stdoutToServer=True, stderrToServer=True)

    sequence = []

    es_0 = es_dict.values()[0]
    pheno_df = es_0.get_pheno_data_frame()

    folds_num = int(folds_num)
    user_class_title = es_0.pheno_metadata["user_class_title"]
    if user_class_title not in pheno_df.columns:
        raise RuntimeError("Phenotype doesn't have user assigned classes")

    mask = pd.notnull(pheno_df[user_class_title])

    masked_pheno_df = pheno_df.loc[mask]
    classes_vector = masked_pheno_df[user_class_title].values
    from collections import Counter
    for c in Counter(classes_vector).itervalues():
        folds_num = min(c, folds_num)
    block.folds_num = folds_num
    # block.save()
    i = 0
    for train_idx, test_idx in chain(*repeat(cross_validation.StratifiedKFold(
        classes_vector,
        n_folds=folds_num,
        shuffle=True
    ), repeats_num)):
        cell = {}
        for input_name, output_names in inner_output_es_names_map.iteritems():
            # if settings.CELERY_DEBUG:
            #     import sys
            #     sys.path.append('/Migration/skola/phd/projects/miXGENE/mixgene_project/wrappers/pycharm-debug.egg')
            #     import pydevd
            #     pydevd.settrace('localhost', port=6901, stdoutToServer=True, stderrToServer=True)
            es_train_name, es_test_name = output_names
            es = es_dict[input_name]
            assay_df = es.get_assay_data_frame().T

            # Reorder columns to be compatible to phenotype
            assay_df = assay_df[pheno_df.index]
            # Removing unused samples
            assay_df = assay_df[assay_df.columns[mask]]

            train_es = es.clone("%s_%s_train_%s" % (es_0.base_filename, input_name, i))
            train_es.base_dir = exp.get_data_folder()
            train_es.store_assay_data_frame(assay_df[train_idx].T)
            train_es.store_pheno_data_frame(masked_pheno_df.iloc[train_idx])

            test_es = es.clone("%s_%s_test_%s" % (es_0.base_filename, input_name, i))
            test_es.base_dir = exp.get_data_folder()
            test_es.store_assay_data_frame(assay_df[test_idx].T)
            test_es.store_pheno_data_frame(masked_pheno_df.iloc[test_idx])

            cell[es_train_name] = train_es
            cell[es_test_name] = test_es
            log.debug("train_es: %s", assay_df[train_idx].shape)
            log.debug("test_es: %s", assay_df[test_idx].shape)
        sequence.append(cell)
        i += 1

    return [sequence], {}

# @task(name="workflow.common_tasks.gt_pval_cut")
# def gt_pval_cut(ctx):
#     exp = Experiment.objects.get(e_id=ctx["exp_id"])
#
#     df = DataFrame.from_csv(ctx['mgt_result'].filepath, sep=' ')
#
#     cut_val = ctx["input_vars"]["common_settings"].inputs["pval_cut"].value
#     index = df[df['p-value'] <= cut_val].index
#
#     # filter expression_train and expression_test
#     expression_train = ctx["expression_train"]
#     train_df = expression_train.to_data_frame()
#     train_df = train_df.loc[index]
#     train_df.to_csv(expression_train.filepath, sep=expression_train.delimiter, index_label=False)
#
#     expression_test = ctx["expression_test"]
#     test_df = expression_test.to_data_frame()
#     test_df = test_df.loc[index]
#     test_df.to_csv(expression_test.filepath, sep=expression_test.delimiter, index_label=False)
#
#     return ctx

