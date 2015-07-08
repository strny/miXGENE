import rpy2.robjects as R
import pandas.rpy.common as com

from celery import task

from converters.gene_set_tools import filter_gs_by_genes
from environment.structures import TableResult

import sys
import traceback
from django.conf import settings


class GlobalTest(object):
    gt = None

    @staticmethod
    def gt_init():
        if GlobalTest.gt is None:
            # importr("globaltest", lib_loc=R_LIB_CUSTOM_PATH)
            R.r['library']("globaltest")  # lib_loc=R_LIB_CUSTOM_PATH)
            GlobalTest.gt = R.r['gt']

    @staticmethod
    def gt_basic(es, gene_sets, pheno_class_column,
                 model="logistic",
                 permutations=100):
        """
            @param es: Expression set with defined user class in pheno
            @type es: ExpressionSet

            @type gene_sets: environment.structures.GeneSets

            @param pheno_class_column: Column name of target classes in phenotype table
            @type pheno_class_column: string or None
        """
        if settings.CELERY_DEBUG:
            import sys
            sys.path.append('/Migration/skola/phd/projects/miXGENE/mixgene_project/wrappers/pycharm-debug.egg')
            import pydevd
            pydevd.settrace('localhost', port=6901, stdoutToServer=True, stderrToServer=True)
        src_gs = gene_sets.get_gs()
        GlobalTest.gt_init()
        df = es.get_assay_data_frame()
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

        dataset = com.convert_to_r_matrix(df.T)
        response = es.get_pheno_column_as_r_obj(pheno_class_column)

        gt_instance = GlobalTest.gt(
            response,
            R.r['t'](dataset),
            subsets=gs_filtered.to_r_obj(),
            model=model,
            permutations=permutations,
        )

        result = gt_instance.do_slot('result')
        result_df = com.convert_robj(result)
        return result_df


# @task(name="wrappers.gt.global_test_task")
def global_test_task(
        exp, block,
        es, gene_sets,
        # base_dir, base_filename,
        table_result
    ):
    """
    @param es: Expression set with defined user class in pheno
    @type es: ExpressionSet

    @type gs: environment.structures.GeneSets

    @param filepath: Fully qualified filepath to store result data frame
    @type filepath: str

    @param pheno_class_column: Column name of target classes in phenotype table
    @type pheno_class_column: str or None
    """

    result_df = GlobalTest.gt_basic(es, gene_sets, es.pheno_metadata["user_class_title"])
    table_result.store_table(result_df)
    return [table_result], {}

