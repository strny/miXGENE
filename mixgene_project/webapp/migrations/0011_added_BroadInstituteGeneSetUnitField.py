# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'BroadInstituteGeneSet.unit'
        db.add_column(u'webapp_broadinstitutegeneset', 'unit',
                      self.gf('django.db.models.fields.CharField')(default='entrez', max_length=31),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'BroadInstituteGeneSet.unit'
        db.delete_column(u'webapp_broadinstitutegeneset', 'unit')


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
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
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
            'e_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'status': ('django.db.models.fields.TextField', [], {'default': "'created'"}),
            'wfl_setup': ('django.db.models.fields.TextField', [], {'default': "''"}),
            'workflow': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['webapp.WorkflowLayout']"})
        },
        u'webapp.uploadeddata': {
            'Meta': {'object_name': 'UploadedData'},
            'data': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True'}),
            'exp': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['webapp.Experiment']"}),
            'filename': ('django.db.models.fields.CharField', [], {'default': "'default'", 'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'var_name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'webapp.workflowlayout': {
            'Meta': {'object_name': 'WorkflowLayout'},
            'description': ('django.db.models.fields.TextField', [], {'default': "''"}),
            'title': ('django.db.models.fields.TextField', [], {'default': "''"}),
            'w_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'wfl_class': ('django.db.models.fields.TextField', [], {'null': 'True'})
        }
    }

    complete_apps = ['webapp']