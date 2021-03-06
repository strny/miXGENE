import gzip
import cPickle as pickle
import logging
from uuid import uuid1
import pandas as pd
import numpy as np
import scipy.sparse as sp
import rpy2.robjects as R
from copy import deepcopy
import hashlib
import re
import json

from workflow.input import AbsInputVar
from wrappers.scoring import metrics
from webapp.notification import AllUpdated, NotifyMode
from django.conf import settings


# from wrappers.input.utils import translate_inters


log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class PickleStorage(object):
    def __init__(self, filepath, gzipped=True):
        self.filepath = filepath
        self.gzipped = gzipped

    def load(self):
        try:
            if self.gzipped:
                return pickle.loads(gzip.open(self.filepath, "rb").read())
            else:
                return pickle.loads(open(self.filepath, "rb").read())
        except:
            return pickle.loads(gzip.open(self.filepath, "rb").read())

    def store(self, obj):
        try:
            if self.gzipped:
                with gzip.open(self.filepath, "wb") as out:
                    pickle.dump(obj, out, 2)
            else:
                with open(self.filepath, "wb") as out:
                    pickle.dump(obj, out, 2)
        except:
            with gzip.open(self.filepath, "wb") as out:
                pickle.dump(obj, out, 2)


class DataFrameStorage(object):
    sep = " "
    header = 0
    index_col = 0
    compression = "gzip"

    def __init__(self, filepath):
        self.filepath = filepath

    def load(self, nrows=None):
        """
            @type nrows: int or None
            @param nrows: Number of rows to read

            @rtype  : pandas.DataFrame
            @return : Stored matrix
        """
        return pd.read_table(
            self.filepath,
            sep=self.sep,
            compression=self.compression,
            header=self.header,
            index_col=self.index_col,
            nrows=nrows
        )

    def store(self, df):
        """
            @type   df: pandas.DataFrame
            @param  df: Stored matrix
        """
        if not isinstance(df, pd.DataFrame):
            raise TypeError("Given object isn't of DataFrame class: %s" % df)
        if self.compression == "gzip":
            with gzip.open(self.filepath, "wb") as output:
                df.to_csv(
                    output,
                    sep=self.sep,
                    index_col=self.index_col,
                )
        elif self.compression is None:
            with open(self.filepath, "wb") as output:
                df.to_csv(
                    output,
                    sep=self.sep,
                    index_col=self.index_col,
                )


class GenericStoreStructure(object):
    def __init__(self, base_dir, base_filename, *args, **kwargs):
        self.base_dir = base_dir
        self.base_filename = base_filename

    def form_filepath(self, suffix):
        return "%s/%s_.%s.gz" % (self.base_dir, self.base_filename, suffix)


class PcaResult(GenericStoreStructure):
    def __init__(self, base_dir, base_filename):
        super(PcaResult, self).__init__(base_dir, base_filename)
        self.pca_storage = None

    def store_pca(self, df):
        if self.pca_storage is None:
            self.pca_storage = DataFrameStorage(self.form_filepath("pca"))
        self.pca_storage.store(df)

    def get_pca(self):
        if self.pca_storage is None:
            raise RuntimeError("PCA data wasn't stored prior")
        return self.pca_storage.load()


class BinaryInteraction(GenericStoreStructure):
    def __init__(self, *args, **kwargs):
        super(BinaryInteraction, self).__init__(*args, **kwargs)
        # self.storage = None
        self.storage_pairs = None
        self.x1_unit = ""
        self.x2_unit = ""
        self.header = False
        self.bi_data_type = ""

    def store_pairs(self, pairs, bi_data_type):
        if self.storage_pairs is None:
            self.storage_pairs = DataFrameStorage(self.form_filepath("interaction_pairs"))
        self.bi_data_type = bi_data_type
        self.storage_pairs.store(pairs)

    def load_pairs(self):
        if self.storage_pairs is None:
            raise RuntimeError("Interaction pairs data wasn't stored prior")
        return self.storage_pairs.load()

    def get_matrix_for_platform(self, exp, gene_list, mirna_list=None, symmetrize=True, identifiers=True,
                                tolower=False):
        if settings.CELERY_DEBUG:
            import sys
            sys.path.append('/Migration/skola/phd/projects/miXGENE/mixgene_project/wrappers/pycharm-debug.egg')
            import pydevd
            pydevd.settrace('localhost', port=6901, stdoutToServer=True, stderrToServer=True)

        from collections import defaultdict
        from wrappers.input.utils import find_refseqs
        log.debug(gene_list)
        if mirna_list:
            log.debug(mirna_list)
        regex = "^[A-Z][A-Z]_[a-zA-Z0-9.]*"
        if len(filter(lambda x: x is not None, map(lambda x: re.match(regex, str(x), re.IGNORECASE), gene_list))) < (len(gene_list)*0.5):
            new_g = []
            for gene in gene_list:
                rf = list(find_refseqs(gene))
                if len(rf) > 0:
                    new_g.append(rf[0])
                if len(rf) == 0:
                    new_g.append(gene)
            gene_list = new_g
        hasht = dict(zip(gene_list, range(len(gene_list))))

        mirna_hasht = dict()
        if mirna_list is not None:
            new_g = []
            for gene in mirna_list:
                rf = list(find_refseqs(gene))
                if len(rf) > 0:
                    new_g.append(rf[0])
                else:
                    new_g.append(gene)
            mirna_list = new_g
            mirna_hasht = dict(zip(mirna_list, range(len(mirna_list))))

        inter_hash = defaultdict(list)
        interactons = self.load_pairs()
        cols = []
        rows = []
        log.debug("transforming interactions")
        for ix in range(len(interactons)):
            a, b, val = interactons.iloc[ix]
            if mirna_list is not None:
                if self.x2_unit == 'mirbase':
                    inter_hash[b].append([a, val])
                else:
                    inter_hash[a].append([b, val])
            else:
                inter_hash[a].append([b, val])
        if exp:
            AllUpdated(
                exp.pk,
                comment=u"Transforming interaction matrix done",
                silent=False,
                mode=NotifyMode.INFO
            ).send()
        log.debug("transformation of interactions done")
        count = 0
        counter2 = 0
        counter3 = 0
        counter4 = 0
        size_hash = len(inter_hash)
        if mirna_list is None:
            for key, value in inter_hash.iteritems():
                count += 1
                if count % 500 == 0:
                    log.debug("translating gene %d", count)
                    if exp:
                        AllUpdated(
                            exp.pk,
                            comment=u"Translating gene %s of %s" % (count, size_hash),
                            silent=False,
                            mode=NotifyMode.INFO
                        ).send()
                refseqs = find_refseqs(key)
                for refseq in refseqs:
                    counter2 += 1
                    if refseq not in hasht:
                        continue
                    if refseq in hasht:
                        for (gene, strength) in value:
                            # new_inters.append([(refseq, new_refseq, strength)
                            for new_refseq in find_refseqs(gene):
                                counter3 += 1
                                gi = refseq
                                gj = new_refseq
                                if gj not in hasht:
                                    continue
                                counter4 += 1
                                val = strength
                                if tolower:
                                    gi = gi.lower()
                                    gj = gj.lower()
                                cols.append(hasht[gi])
                                rows.append(hasht[gj])
        else:
            for key, value in inter_hash.iteritems():
                count += 1
                if count % 500 == 0:
                    log.debug("translating miRNA %d", count)
                    if exp:
                        AllUpdated(
                            exp.pk,
                            comment=u"Translating miRNA %s of %s" % (count, size_hash),
                            silent=False,
                            mode=NotifyMode.INFO
                        ).send()
                refseqs = find_refseqs(key)
                for refseq in refseqs:
                    counter2 += 1
                    if refseq not in mirna_hasht:
                        continue
                    if refseq in mirna_hasht:
                        for (gene, strength) in value:
                            for new_refseq in find_refseqs(gene):
                                counter3 += 1
                                gi = refseq
                                gj = new_refseq
                                if gj not in hasht:
                                    continue
                                counter4 += 1
                                val = strength
                                if tolower:
                                    gi = gi.lower()
                                    gj = gj.lower()
                                rows.append(mirna_hasht[gi])
                                cols.append(hasht[gj])
        # size = max(max(rows), max(cols)) + 1
        if exp:
            AllUpdated(
                exp.pk,
                comment=u"%d interactions were found." % len(cols),
                silent=False,
                mode=NotifyMode.INFO
            ).send()
        inters_matr = None
        # TODO fix for custom value of interactions
        if mirna_list is None:
            # inters_matr = sp.coo_matrix((np.ones(len(cols)), (rows, cols)), (size, size))
            inters_matr = sp.coo_matrix((np.ones(len(cols)), (rows, cols)), (len(gene_list), len(gene_list)))
        else:
            inters_matr = sp.coo_matrix((np.ones(len(cols)), (rows, cols)), (len(mirna_list), len(gene_list)))
            #inters_matr = sp.coo_matrix((np.ones(len(cols)), (rows, cols)), (max(rows) + 1, max(cols) + 1))

        if symmetrize:
            inters_matr = inters_matr + inters_matr.T
            inters_matr.data /= inters_matr.data

        if identifiers:
            inters_matr = inters_matr.tocsr()
            sparse_df = pd.SparseDataFrame([pd.SparseSeries(inters_matr[i].toarray().ravel())
                                            for i in np.arange(inters_matr.shape[0])])
            # sparse_df = sparse_df.to_dense()
            if mirna_list is None:
                index = gene_list[:sparse_df.shape[0]]
                columns = gene_list[:sparse_df.shape[1]]
            else:
                index = mirna_list[:sparse_df.shape[0]]
                columns = gene_list[:sparse_df.shape[1]]
            if settings.CELERY_DEBUG:
                import sys
                sys.path.append('/Migration/skola/phd/projects/miXGENE/mixgene_project/wrappers/pycharm-debug.egg')
                import pydevd
                pydevd.settrace('localhost', port=6901, stdoutToServer=True, stderrToServer=True)

            # sparse_df['new_index'] = pd.Series(index, index=sparse_df.index)
            sparse_df.set_index([index], inplace=True)
            sparse_df.columns = columns
            return sparse_df
        return inters_matr

    def store_matrix(self, df):
        # deprecated
        pass
        # if self.storage is None:
        #     self.storage = DataFrameStorage(self.form_filepath("interaction"))
        # self.storage.store(df)

    def load_matrix(self):
        if self.storage is None:
            raise RuntimeError("Interaction data wasn't stored prior")
        interaction_df = self.storage.load()
        features_1 = interaction_df[0]
        features_2 = interaction_df[1]
        values = interaction_df[2]

        if self.bi_data_type in ["pairs", "triples"]:
            features = list(set(features_1 + features_2))
            sd = pd.DataFrame(index=features, columns=features).to_sparse(fill_value=0)
        else:
            sd = pd.DataFrame(index=list(set(features_1)), columns=list(set(features_2))).to_sparse(fill_value=0)
        # optimization
        if self.bi_data_type in ["pairs", "pairs_diff"]:
            for index, cols in interaction_df.iterrows():
                sd[cols[1]][cols[0]] = 1
        else:
            for index, cols in interaction_df.iterrows():
                sd[cols[1]][cols[0]] = cols[3]
        sd = sd.to_dense()
        # matrix.set_index(matrix.columns[0], inplace=True, drop=True)
        return sd


class Edges(GenericStoreStructure):
    def __init__(self, *args, **kwargs):
        super(Edges, self).__init__(*args, **kwargs)
        self.storage = None

    def store_edges(self, df):
        if self.storage is None:
            self.storage = PickleStorage(self.form_filepath("edges"))
        self.storage.store(df)

    def load_edges(self):
        if self.storage is None:
            raise RuntimeError("Edges data wasn't stored prior")
        return self.storage.load()


class DiffExpr(GenericStoreStructure):
    def __init__(self, *args, **kwargs):
        super(DiffExpr, self).__init__(*args, **kwargs)
        self.storage = None

    def store_expr(self, df):
        if self.storage is None:
            self.storage = PickleStorage(self.form_filepath("diff_expr"))
        self.storage.store(df)

    def load_expr(self):
        if self.storage is None:
            raise RuntimeError("Edges data wasn't stored prior")
        return self.storage.load()


class ComoduleSet(GenericStoreStructure):
    def __init__(self, *args, **kwargs):
        super(ComoduleSet, self).__init__(*args, **kwargs)
        self.storage = None

    def store_set(self, df):
        if self.storage is None:
            self.storage = PickleStorage(self.form_filepath("comodule"))
        self.storage.store(df)

    def load_set(self):
        if self.storage is None:
            raise RuntimeError("Comodule data wasn't stored prior")
        return self.storage.load()


class DictionarySet(GenericStoreStructure):
    def __init__(self, base_dir, base_filename):
        super(DictionarySet, self).__init__(base_dir, base_filename)
        self.storage = None

    def store_dict(self, d):
        if self.storage is None:
            self.storage = PickleStorage(self.form_filepath("dict_set"))
        self.storage.store(d)

    def load_dict(self):
        if self.storage is None:
            raise RuntimeError("Dictionary data wasn't stored prior!")
        return self.storage.load()


def convert_to_refseq(assay_df, platform):
    from wrappers.input.utils import find_refseqs
    # features of dataset
    columns_source = set(list(assay_df))
    new_names = {}
    count = 0
    for gene in columns_source:
        new_name = list(find_refseqs(gene))
        if new_name:
            for n in new_name:
                if n in platform:
                    new_names[gene] = n
                    count += 1
                    # find first and assign it to gene
                    break
        else:
            new_names[gene] = gene
    assay_df.rename(columns=new_names, inplace=True)
    return assay_df, count


class ExpressionSet(GenericStoreStructure):
    def __init__(self, base_dir, base_filename):
        """
            Expression data from micro array experiment.

            Actual matrices are stored in filesystem, so it's required
             to provide base_dir and base_base_filename.

            @type  base_dir: string
            @param base_dir: Path to directory where all data objects will be stored

            @type  base_filename: string
            @param base_filename: Basic name which is used as prefix for all stored data objects
        """
        super(ExpressionSet, self).__init__(base_dir, base_filename)

        self.assay_data_storage = None
        self.assay_metadata = {}

        self.pheno_data_storage = None
        self.pheno_metadata = {
            "user_class_title": "User_class"
        }

        self.working_unit = None
        self.annotation = None

        self.df_platform = {}

        # Have no idea about 3 following variables
        self.feature_data = None
        self.experiment_data = None
        self.protocol_data = None

    def __str__(self):
        return "ExpressionSet, pheno: %s , assay: %s" % (self.pheno_data_storage, self.assay_data_storage)

    def clone(self, base_filename, clone_data_frames=False):
        es = ExpressionSet(self.base_dir, base_filename)

        es.working_unit = deepcopy(self.working_unit)
        es.annotation = deepcopy(self.annotation)
        es.feature_data = deepcopy(self.feature_data)
        es.experiment_data = deepcopy(self.experiment_data)
        es.protocol_data = deepcopy(self.protocol_data)

        es.assay_metadata = deepcopy(self.assay_metadata)
        es.pheno_metadata = deepcopy(self.pheno_metadata)
        if clone_data_frames:
            es.store_assay_data_frame(self.get_assay_data_frame())
            es.store_pheno_data_frame(self.get_pheno_data_frame())

        return es

    def get_assay_data_frame_for_platform(self, exp, platform):
        """
            @rtype: pd.DataFrame
        """
        if self.assay_data_storage is None:
            raise RuntimeError("Assay data wasn't setup prior")
        p = set(platform)
        checksum = np.frombuffer("".join(platform), "uint8").sum()
        if checksum in self.df_platform:
            if self.df_platform[checksum]:
                if exp:
                    AllUpdated(
                        exp.pk,
                        comment=u"Loading Expression Set from Cache",
                        silent=False,
                        mode=NotifyMode.INFO
                    ).send()
                return self.df_platform[checksum].load()
        if self.working_unit != 'RefSeq':
            if exp:
                AllUpdated(
                    exp.pk,
                    comment=u"Converting unit %s to RefSeq" % self.working_unit,
                    silent=False,
                    mode=NotifyMode.INFO
                ).send()
            df = self.assay_data_storage.load()
            df, matched = convert_to_refseq(df, p)
            self.df_platform[checksum] = DataFrameStorage(
                filepath="%s/%s_%s_assay.csv.gz" % (self.base_dir, self.base_filename, checksum))
            self.df_platform[checksum].store(df)
            if exp:
                AllUpdated(
                    exp.pk,
                    comment=u"Converted %s %s to RefSeq" % (matched, self.working_unit),
                    silent=False,
                    mode=NotifyMode.INFO
                ).send()
            return df
        return self.assay_data_storage.load()

    def get_assay_data_frame(self):
        """
            @rtype: pd.DataFrame
        """
        if self.assay_data_storage is None:
            raise RuntimeError("Assay data wasn't setup prior")
        return self.assay_data_storage.load()

    def store_assay_data_frame(self, df):
        """
            @type  df: pd.DataFrame
            @param df: Table with expression data
        """
        if self.assay_data_storage is None:
            self.assay_data_storage = DataFrameStorage(
                filepath="%s/%s_assay.csv.gz" % (self.base_dir, self.base_filename))
        self.assay_data_storage.store(df)

    def get_pheno_data_frame(self):
        """
            @rtype: pd.DataFrame
        """
        if self.pheno_data_storage is None:
            raise RuntimeError("Phenotype data wasn't setup prior")
        return self.pheno_data_storage.load()

    def store_pheno_data_frame(self, df):
        """
            @type df: pd.DataFrame
        """
        if self.pheno_data_storage is None:
            self.pheno_data_storage = DataFrameStorage(
                filepath="%s/%s_pheno.csv.gz" % (self.base_dir, self.base_filename))
        self.pheno_data_storage.store(df)

    def to_r_obj(self):
        pass

    def get_pheno_column_as_r_obj(self, column_name):
        pheno_df = self.get_pheno_data_frame()
        column = pheno_df[column_name].tolist()
        return R.r['factor'](R.StrVector(column))

    def to_json_preview(self, row_number=20):
        assay_df = self.assay_data_storage.load(row_number)
        pheno_df = self.pheno_data_storage.load(row_number)

        result = {
            "assay_metadata": self.assay_metadata,
            "assay": json.loads(assay_df.to_json(orient="split")),
            "pheno_metadata": self.pheno_metadata,
            "pheno": json.loads(pheno_df.to_json(orient="split")),
        }
        return json.dumps(result)


class GS(object):
    def __init__(self, description=None, genes=None):
        if description is not None:
            self.description = description
        else:
            self.description = {}

        if genes is not None:
            self.genes = genes
        else:
            self.genes = {}

    def to_r_obj(self):
        gene_sets = R.ListVector(dict([
                                          (k, R.StrVector(list(v)))
                                          for k, v in self.genes.iteritems()
                                          if len(v)
                                          ]))
        return gene_sets


class GmtStorage(object):
    def __init__(self, filepath, compression=None, sep=None):
        """

        @param sep:
        @type filepath: str
        @param filepath: absolute path to stored object

        @param compression: either None of "gzip"

        @param sep: elements separator, default  \t

        @rtype: GeneSets
        @return:
        """
        self.filepath = filepath
        self.compression = compression
        if sep is not None:
            self.sep = sep
        else:
            self.sep = "\t"

    @staticmethod
    def convert_to_refseqs(gene_sets):
        from wrappers.input.utils import expand_geneset
        from webapp.models import GEOTerm
        import json

        for key in gene_sets.genes.keys():
            if str(key).isdigit():
                genes = expand_geneset(gene_sets.genes[key])
            else:
                term, created = GEOTerm.objects.get_or_create(term_name=key)
                if created:
                    genes = expand_geneset(gene_sets.genes[key])
                    term.term_genes = json.dumps(list(genes))
                    term.save()
                else:
                    genes = set(json.loads(term.term_genes))
            gene_sets.genes[key] = genes
        return gene_sets

    @staticmethod
    def read_inp(inp, sep, conv=True):
        gene_sets = GS(dict(), dict())
        for line in inp:
            split = line.strip().split(sep)
            if len(split) < 3:
                continue
            key = split[0]
            gene_sets.description[key] = split[1]
            gene_sets.genes[key] = split[2:]
        if conv:
            return GmtStorage.convert_to_refseqs(gene_sets)
        else:
            return gene_sets

    def load(self, conv=True):
        """
            @rtype  : GS
        """
        if self.compression == "gzip":
            with gzip.open(self.filepath) as inp:
                return GmtStorage.read_inp(inp, self.sep, conv)
        else:
            with open(self.filepath) as inp:
                return GmtStorage.read_inp(inp, self.sep, conv)

    def store(self, gene_sets):
        """
            @type gene_sets: GS
            @return: None
        """

        def write_out(out):
            for key in gene_sets.description.keys():
                description = gene_sets.description[key]
                elements = gene_sets.genes[key]
                out.write("%s\t%s\t%s\n" % (
                    (key, description, "\t".join(elements))
                ))

        if self.compression == "gzip":
            with gzip.open(self.filepath, "w") as output:
                write_out(output)
        else:
            with open(self.filepath, "w") as output:
                write_out(output)


class GeneSets(GenericStoreStructure):
    def __init__(self, base_dir, base_filename):
        super(GeneSets, self).__init__(base_dir, base_filename)

        self.storage = None
        self.metadata = {
            "org": list(),
            "set_units": str(),
            "gene_units": str(),
        }

    def store_gs(self, gs):
        """
            @type gs: GS
        """
        if self.storage is None:
            self.storage = GmtStorage(
                filepath="%s/%s_gene_sets.gmt.gz" % (self.base_dir, self.base_filename),
                compression="gzip"
            )
        self.storage.store(gs)

    def get_gs(self, conv=True):
        if self.storage is None:
            raise RuntimeError("No gene sets was stored")
        return self.storage.load(conv)




class PlatformAnnotation(object):
    def __init__(self, platform_name, base_dir, base_filename):
        """
            Metadata about experiment platform

            Actual matrices are stored in filesystem, so it's required
             to provide base_dir and base_base_filename.

            @type  base_dir: string
            @param base_dir: Path to directory where all data objects will be stored

            @type  base_filename: string
            @param base_filename: Basic name which is used as prefix for all stored data objects
        """
        self.base_dir = base_dir
        self.base_filename = base_filename

        self.name = platform_name
        self.gene_sets = GeneSets(base_dir, "%s_platform" % base_filename)


class SequenceContainer(object):
    def __init__(self, fields=None, sequence=None):
        self.sequence = sequence or []
        self.fields = fields or {}  # TODO: Just names, or contains some meta info ?
        self.iterator = -1

    def is_end(self):
        if self.iterator == len(self.sequence) - 1:
            return True
        return False

    def append(self, element):
        self.sequence.append(element)

    def clean_content(self):
        self.sequence = []
        self.iterator = -1

    def apply_next(self):
        """
            Set block properties from the current sequence element

            @type block: workflow.Block

            @return: None
            @throws: StopIteration
        """
        self.iterator += 1
        if self.iterator >= len(self.sequence):
            raise StopIteration()

            # el = self.sequence[self.iterator]
            # for field in self.fields:
            #     setattr(block, field, getattr(el, field))

    def get_field(self, field):
        return self.sequence[self.iterator][field]

    def reset_iterator(self):
        self.iterator = -1

    def to_dict(self):
        dict_seq = []
        for cell in self.sequence:
            if cell is not None and self.fields is not None:
                cell_dict = {}
                for field in self.fields.keys():
                    obj = cell.get(field)
                    if hasattr(obj, "to_dict"):
                        cell_dict[field] = obj.to_dict()
                    else:
                        cell_dict[field] = str(obj)
                dict_seq.append(cell_dict)
            else:
                dict_seq.append(None)
        return {
            "fields": self.fields,
            "seq": dict_seq
        }


class ClassifierResult(GenericStoreStructure):
    def __init__(self, *args, **kwargs):
        super(ClassifierResult, self).__init__(*args, **kwargs)

        self.classifier = ""
        self.labels_encode_vector = []
        self.scores = {}  # metric -> value
        self.y_true = []
        self.y_predicted = []
        self.model_storage = None

    def get_model(self):
        if self.model_storage is None:
            raise RuntimeError("Model wasn't stored")
        return self.model_storage.load()

    def store_model(self, model):
        if self.model_storage is None:
            self.model_storage = PickleStorage(self.form_filepath("classifier_result"))
        self.model_storage.store(model)

    def to_dict(self):
        scores_dict = {}
        for metric in metrics:
            if metric.name in self.scores:
                scores_dict[metric.name] = \
                    metric.to_dict(self.scores[metric.name])

        return {
            "classifier": self.classifier,
            "scores": scores_dict,
        }


class TableResult(GenericStoreStructure):
    def __init__(self, base_dir, base_filename):
        super(TableResult, self).__init__(base_dir, base_filename)

        self.table_storage = None
        self.metadata = dict()
        self.headers = []

    def to_dict(self):
        # df = self.get_table()
        return {
            "headers": self.headers
        }

    def store_table(self, df):
        if self.table_storage is None:
            self.table_storage = DataFrameStorage(self.form_filepath("result_table"))
        self.table_storage.store(df)

    def get_table(self):
        """
            @rtype: pd.DataFrame
        """
        if self.table_storage is None:
            raise RuntimeError("Result table data wasn't stored prior")
        return self.table_storage.load()


### R Legacy
class mixML(object):
    def __init__(self, exp, rMixML, csv_filename):
        self.uuid = str(uuid1())
        self.template = "workflow/result/mixML.html"
        self.title = "mixML"

        self.model = str(rMixML.do_slot('model')[0])
        self.acc = int(rMixML.do_slot('acc')[0])
        self.working_units = list(rMixML.do_slot('working.units'))

        predicted = rMixML.do_slot('predicted')

        self.filename = csv_filename
        self.filepath = exp.get_data_file_path(csv_filename)

        R.r['write.table'](predicted, self.filepath, row_names=True, col_names=True)

        self.has_col_names = True
        self.has_row_names = True
        self.csv_delimiter = " "


class FileInputVar(AbsInputVar):
    # TODO: rework into storage + variable
    def __init__(self, *args, **kwargs):
        super(FileInputVar, self).__init__(*args, **kwargs)
        self.input_type = "file"
        self.is_done = False
        self.is_being_fetched = False

        self.file_type = None
        self.filename = None
        self.filepath = None
        self.file_extension = "csv"
        self.is_gzipped = False

        self.file_format = None

        self.geo_uid = None
        self.geo_type = None

    def to_dict(self, *args, **kwargs):
        return self.__dict__

    def set_file_type(self, file_type):
        if file_type in ['user', 'ncbi_geo', 'gmt']:
            self.file_type = file_type
        else:
            raise Exception("file type should be in [`user`, `ncbi_geo`, `gmt`], not %s" % type)


def fix_val(value):
    if not pd.notnull(value):
        # return None
        return ""
    return str(value)


def prepare_phenotype_for_js_from_es(es, headers_option=None):
    """
        @type es: ExpressionSet
        @param headers_option: dict containing the following fields:
            `custom_title_prefix_map`: [list of pairs ( , )] orig prefix, new prefix.
                first matched prefix will be applied
            `prefix_order`: [list] order of headers, all other header would be put in the tail
            `prefix_hide`:  set() of headers which would be hidden by default
    """
    if headers_option is None:
        headers_option = {
            "custom_title_prefix_map": {},
            "prefix_order": [],
            "prefix_hide": set(),
        }
    log.debug("headers options %s", headers_option)

    pheno_df = es.get_pheno_data_frame()
    skip_index = 0
    if pheno_df.index.name:
        pheno_headers_list = [pheno_df.index.name, ] + pheno_df.columns.tolist()

    else:
        pheno_headers_list = pheno_df.columns.tolist()
        skip_index = 1


    # ng-grid specific
    column_title_to_code_name = {
        val: "_" + hashlib.md5(val).hexdigest()[:8]
        for val in pheno_headers_list
        }

    # Here we reorder pheno columns according to `headers_option.order`
    pheno_headers_fixed_list = []
    for prefix_header in headers_option["prefix_order"]:
        for header in pheno_headers_list:
            if header.startswith(prefix_header):
                pheno_headers_fixed_list.append(header)

    pheno_headers_fixed_set = set(pheno_headers_fixed_list)
    pheno_headers_fixed_list.extend([
                                        header for header in pheno_headers_list
                                        if header not in pheno_headers_fixed_set
                                        ])

    def prefix_rename(value):
        prefix_map = headers_option["custom_title_prefix_map"]
        for src_prefix, dst_prefix in prefix_map:
            if value.startswith(src_prefix):
                value = value.replace(src_prefix, dst_prefix, 1)
                break

        value = value.replace("_", " ")
        return value

    pheno_headers = [
        {
            "field": column_title_to_code_name[val],
            # "displayName": headers_option["custom_title"].get(val, val),
            "displayName": prefix_rename(val),
            "minWidth": 150,
            "visible": all([
                               not val.startswith(prefix) for prefix in
                               headers_option["prefix_hide"]
                               ])
        }
        for val in pheno_headers_fixed_list
        ]
    log.debug(pheno_headers_fixed_list)
    # pheno_table = json.loads(pheno_df.to_json(orient="records"))
    # again ng-grid specific
    pheno_table = []
    for record in pheno_df.to_records():
        pheno_table.append({
                               str(column_title_to_code_name[title]): fix_val(value)
                               for (title, value)
                               in zip(pheno_headers_list, list(record)[skip_index:])
                               })

    return {
        "headers": pheno_headers,
        "headers_title_to_code_map": column_title_to_code_name,
        "table": pheno_table,
        "user_class_title": es.pheno_metadata.get("user_class_title")
    }
