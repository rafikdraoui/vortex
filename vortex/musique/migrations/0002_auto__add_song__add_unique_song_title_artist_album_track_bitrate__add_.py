# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Song'
        db.create_table('musique_song', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('artist', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['musique.Artist'])),
            ('album', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['musique.Album'])),
            ('track', self.gf('django.db.models.fields.CharField')(default='', max_length=10)),
            ('bitrate', self.gf('django.db.models.fields.IntegerField')()),
            ('filetype', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('filefield', self.gf('django.db.models.fields.files.FileField')(max_length=200)),
            ('original_path', self.gf('django.db.models.fields.CharField')(default='', max_length=200)),
            ('first_save', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('musique', ['Song'])

        # Adding unique constraint on 'Song', fields ['title', 'artist', 'album', 'track', 'bitrate']
        db.create_unique('musique_song', ['title', 'artist_id', 'album_id', 'track', 'bitrate'])

        # Adding model 'Artist'
        db.create_table('musique_artist', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=100)),
            ('filepath', self.gf('django.db.models.fields.FilePathField')(path='/Users/rafik/Projets/musique-achoppe/media', unique=True, max_length=200, recursive=True)),
        ))
        db.send_create_signal('musique', ['Artist'])

        # Adding model 'Album'
        db.create_table('musique_album', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('artist', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['musique.Artist'])),
            ('filepath', self.gf('django.db.models.fields.FilePathField')(path='/Users/rafik/Projets/musique-achoppe/media', unique=True, max_length=200, recursive=True)),
        ))
        db.send_create_signal('musique', ['Album'])


    def backwards(self, orm):
        # Removing unique constraint on 'Song', fields ['title', 'artist', 'album', 'track', 'bitrate']
        db.delete_unique('musique_song', ['title', 'artist_id', 'album_id', 'track', 'bitrate'])

        # Deleting model 'Song'
        db.delete_table('musique_song')

        # Deleting model 'Artist'
        db.delete_table('musique_artist')

        # Deleting model 'Album'
        db.delete_table('musique_album')


    models = {
        'musique.album': {
            'Meta': {'ordering': "['title']", 'object_name': 'Album'},
            'artist': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['musique.Artist']"}),
            'filepath': ('django.db.models.fields.FilePathField', [], {'path': "'/Users/rafik/Projets/musique-achoppe/media'", 'unique': 'True', 'max_length': '200', 'recursive': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'musique.artist': {
            'Meta': {'ordering': "['name']", 'object_name': 'Artist'},
            'filepath': ('django.db.models.fields.FilePathField', [], {'path': "'/Users/rafik/Projets/musique-achoppe/media'", 'unique': 'True', 'max_length': '200', 'recursive': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'})
        },
        'musique.song': {
            'Meta': {'ordering': "['track', 'title']", 'unique_together': "(('title', 'artist', 'album', 'track', 'bitrate'),)", 'object_name': 'Song'},
            'album': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['musique.Album']"}),
            'artist': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['musique.Artist']"}),
            'bitrate': ('django.db.models.fields.IntegerField', [], {}),
            'filefield': ('django.db.models.fields.files.FileField', [], {'max_length': '200'}),
            'filetype': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'first_save': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'original_path': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'track': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '10'})
        }
    }

    complete_apps = ['musique']