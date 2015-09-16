# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'GeneIdentifier'
        db.create_table(u'webapp_geneidentifier', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128)),
        ))
        db.send_create_signal(u'webapp', ['GeneIdentifier'])

        # Adding model 'Refseq'
        db.create_table(u'webapp_refseq', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('gene_identifier_name', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['webapp.GeneIdentifier'])),
            ('refseq', self.gf('django.db.models.fields.CharField')(max_length=128)),
        ))
        db.send_create_signal(u'webapp', ['Refseq'])


    def backwards(self, orm):
        # Deleting model 'GeneIdentifier'
        db.delete_table(u'webapp_geneidentifier')

        # Deleting model 'Refseq'
        db.delete_table(u'webapp_refseq')


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'webapp.arbitraryupload': {
            'Meta': {'object_name': 'ArbitraryUpload'},
            'data': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'dt_updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'webapp.article': {
            'Meta': {'object_name': 'Article'},
            'article_type': ('django.db.models.fields.CharField', [], {'max_length': '31'}),
            'author_title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'author_user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            'content': ('django.db.models.fields.TextField', [], {}),
            'dt_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'dt_updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'preview': ('django.db.models.fields.TextField', [], {}),
            'text_format': ('django.db.models.fields.CharField', [], {'default': "'md'", 'max_length': '31'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'webapp.broadinstitutegeneset': {
            'Meta': {'object_name': 'BroadInstituteGeneSet'},
            'gmt_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'section': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'unit': ('django.db.models.fields.CharField', [], {'default': "'entrez'", 'max_length': '31'})
        },
        u'webapp.cachedfile': {
            'Meta': {'object_name': 'CachedFile'},
            'dt_updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'uri': ('django.db.models.fields.TextField', [], {'default': "''"}),
            'uri_sha': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '127'})
        },
        u'webapp.experiment': {
            'Meta': {'object_name': 'Experiment'},
            'author': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            'dt_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'dt_updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_run': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.TextField', [], {'default': "''"}),
            'parent_exp': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['webapp.Experiment']", 'null': 'True'}),
            'status': ('django.db.models.fields.TextField', [], {'default': "'created'"})
        },
        u'webapp.experimentlog': {
            'Meta': {'object_name': 'ExperimentLog'},
            'block_uuid': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '31'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'experiment': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['webapp.Experiment']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.TextField', [], {'default': "''"}),
            'severity': ('django.db.models.fields.CharField', [], {'default': "'INFO'", 'max_length': '31'})
        },
        u'webapp.geneidentifier': {
            'Meta': {'object_name': 'GeneIdentifier'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        u'webapp.refseq': {
            'Meta': {'object_name': 'Refseq'},
            'gene_identifier_name': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['webapp.GeneIdentifier']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'refseq': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        u'webapp.uploadeddata': {
            'Meta': {'object_name': 'UploadedData'},
            'block_uuid': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '127'}),
            'data': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True'}),
            'exp': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['webapp.Experiment']"}),
            'filename': ('django.db.models.fields.CharField', [], {'default': "'default'", 'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'var_name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }

    complete_apps = ['webapp']