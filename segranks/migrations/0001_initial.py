# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'RankProject'
        db.create_table(u'segranks_rankproject', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('instructions', self.gf('django.db.models.fields.TextField')()),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal(u'segranks', ['RankProject'])

        # Adding model 'Sentence'
        db.create_table(u'segranks_sentence', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(related_name='sentences', to=orm['segranks.RankProject'])),
            ('sentence_id', self.gf('django.db.models.fields.IntegerField')()),
            ('source_str', self.gf('django.db.models.fields.TextField')()),
            ('reference_str', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'segranks', ['Sentence'])

        # Adding model 'Segment'
        db.create_table(u'segranks_segment', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('sentence', self.gf('django.db.models.fields.related.ForeignKey')(related_name='segments', to=orm['segranks.Sentence'])),
            ('segment_str', self.gf('django.db.models.fields.TextField')()),
            ('segment_indexes', self.gf('django.db.models.fields.TextField')()),
            ('candidates_str', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'segranks', ['Segment'])

        # Adding model 'Annotation'
        db.create_table(u'segranks_annotation', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('annotated_segment', self.gf('django.db.models.fields.related.ForeignKey')(related_name='annotations', to=orm['segranks.Segment'])),
            ('ranks', self.gf('django.db.models.fields.TextField')()),
            ('annotator', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal(u'segranks', ['Annotation'])


    def backwards(self, orm):
        # Deleting model 'RankProject'
        db.delete_table(u'segranks_rankproject')

        # Deleting model 'Sentence'
        db.delete_table(u'segranks_sentence')

        # Deleting model 'Segment'
        db.delete_table(u'segranks_segment')

        # Deleting model 'Annotation'
        db.delete_table(u'segranks_annotation')


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
        u'segranks.annotation': {
            'Meta': {'object_name': 'Annotation'},
            'annotated_segment': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'annotations'", 'to': u"orm['segranks.Segment']"}),
            'annotator': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ranks': ('django.db.models.fields.TextField', [], {})
        },
        u'segranks.rankproject': {
            'Meta': {'ordering': "['created']", 'object_name': 'RankProject'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'instructions': ('django.db.models.fields.TextField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        },
        u'segranks.segment': {
            'Meta': {'object_name': 'Segment'},
            'candidates_str': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'segment_indexes': ('django.db.models.fields.TextField', [], {}),
            'segment_str': ('django.db.models.fields.TextField', [], {}),
            'sentence': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'segments'", 'to': u"orm['segranks.Sentence']"})
        },
        u'segranks.sentence': {
            'Meta': {'ordering': "['sentence_id']", 'object_name': 'Sentence'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'sentences'", 'to': u"orm['segranks.RankProject']"}),
            'reference_str': ('django.db.models.fields.TextField', [], {}),
            'sentence_id': ('django.db.models.fields.IntegerField', [], {}),
            'source_str': ('django.db.models.fields.TextField', [], {})
        }
    }

    complete_apps = ['segranks']