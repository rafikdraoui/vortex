# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

from django.conf import settings

class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Album.cover_file_type'
        db.add_column('library_album', 'cover_file_type',
                      self.gf('django.db.models.fields.CharField')(default='jpg', max_length=5),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Album.cover_file_type'
        db.delete_column('library_album', 'cover_file_type')


    models = {
        'library.album': {
            'Meta': {'ordering': "['title']", 'object_name': 'Album'},
            'artist': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['library.Artist']"}),
            'cover': ('django.db.models.fields.files.ImageField', [], {'max_length': '200'}),
            'cover_file_type': ('django.db.models.fields.CharField', [], {'max_length': '5'}),
            'filepath': ('django.db.models.fields.FilePathField', [], {'path': "'%s'" % settings.MEDIA_ROOT, 'unique': 'True', 'max_length': '200', 'recursive': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'library.artist': {
            'Meta': {'ordering': "['name']", 'object_name': 'Artist'},
            'filepath': ('django.db.models.fields.FilePathField', [], {'path': "'%s'" % settings.MEDIA_ROOT, 'unique': 'True', 'max_length': '200', 'recursive': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'})
        },
        'library.song': {
            'Meta': {'ordering': "['track', 'title']", 'unique_together': "(('title', 'album', 'track'),)", 'object_name': 'Song'},
            'album': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['library.Album']"}),
            'bitrate': ('django.db.models.fields.IntegerField', [], {}),
            'date_added': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'filefield': ('django.db.models.fields.files.FileField', [], {'max_length': '200'}),
            'filetype': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'first_save': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'original_path': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'track': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '10', 'blank': 'True'})
        }
    }

    complete_apps = ['library']
