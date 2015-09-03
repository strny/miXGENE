import rpy2.robjects as R
import pandas.rpy.common as com

from celery import task

from converters.gene_set_tools import filter_gs_by_genes
from environment.structures import TableResult

import sys
import traceback
from django.conf import settings
from converters.gene_set_tools import preprocess_df_gs
import logging
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

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
        # GlobalTest.gt_init()
        df = es.get_assay_data_frame()

        df, gs_filtered = preprocess_df_gs(df, src_gs)

        dataset = com.convert_to_r_matrix(df.T)
        response = es.get_pheno_column_as_r_obj(pheno_class_column)

        ds_r = R.r['t'](dataset)
        gs_r = gs_filtered.to_r_obj()
        try:
            R.r['library']("globaltest")
            gt = R.r['gt']
            gt_instance = gt(
                response,
                ds_r,
                subsets=gs_r,
              #  model=model,
              #  permutations=permutations
            )
        except:
            import sys
            log.error("Unexpected error: %s" % sys.exc_info()[0])
            raise
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

