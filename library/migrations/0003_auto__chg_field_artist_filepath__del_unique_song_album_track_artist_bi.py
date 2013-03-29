# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

from django.conf import settings


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Removing unique constraint on 'Song', fields ['album', 'track', 'artist', 'bitrate', 'title']
        db.delete_unique('library_song', ['album_id', 'track', 'artist_id', 'bitrate', 'title'])


        # Changing field 'Artist.filepath'
        db.alter_column('library_artist', 'filepath', self.gf('django.db.models.fields.FilePathField')(path=settings.MEDIA_ROOT, unique=True, max_length=200, recursive=True))
        # Adding field 'Song.date_added'
        db.add_column('library_song', 'date_added',
                      self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, default=datetime.datetime(2012, 11, 16, 0, 0), blank=True),
                      keep_default=False)

        # Adding field 'Song.date_modified'
        db.add_column('library_song', 'date_modified',
                      self.gf('django.db.models.fields.DateTimeField')(auto_now=True, default=datetime.datetime(2012, 11, 16, 0, 0), blank=True),
                      keep_default=False)

        # Adding unique constraint on 'Song', fields ['album', 'track', 'artist', 'title']
        db.create_unique('library_song', ['album_id', 'track', 'artist_id', 'title'])

        # Adding field 'Album.cover'
        db.add_column('library_album', 'cover',
                      self.gf('django.db.models.fields.files.ImageField')(default='', max_length=200),
                      keep_default=False)


        # Changing field 'Album.filepath'
        db.alter_column('library_album', 'filepath', self.gf('django.db.models.fields.FilePathField')(path=settings.MEDIA_ROOT, unique=True, max_length=200, recursive=True))

    def backwards(self, orm):
        # Removing unique constraint on 'Song', fields ['album', 'track', 'artist', 'title']
        db.delete_unique('library_song', ['album_id', 'track', 'artist_id', 'title'])


        # Changing field 'Artist.filepath'
        db.alter_column('library_artist', 'filepath', self.gf('django.db.models.fields.FilePathField')(max_length=200, path=settings.MEDIA_ROOT, unique=True, recursive=True))
        # Deleting field 'Song.date_added'
        db.delete_column('library_song', 'date_added')

        # Deleting field 'Song.date_modified'
        db.delete_column('library_song', 'date_modified')

        # Adding unique constraint on 'Song', fields ['album', 'track', 'artist', 'bitrate', 'title']
        db.create_unique('library_song', ['album_id', 'track', 'artist_id', 'bitrate', 'title'])

        # Deleting field 'Album.cover'
        db.delete_column('library_album', 'cover')


        # Changing field 'Album.filepath'
        db.alter_column('library_album', 'filepath', self.gf('django.db.models.fields.FilePathField')(max_length=200, path=settings.MEDIA_ROOT, unique=True, recursive=True))

    models = {
        'library.album': {
            'Meta': {'ordering': "['title']", 'object_name': 'Album'},
            'artist': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['library.Artist']"}),
            'cover': ('django.db.models.fields.files.ImageField', [], {'max_length': '200'}),
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
            'Meta': {'ordering': "['track', 'title']", 'unique_together': "(('title', 'artist', 'album', 'track'),)", 'object_name': 'Song'},
            'album': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['library.Album']"}),
            'artist': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['library.Artist']"}),
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
