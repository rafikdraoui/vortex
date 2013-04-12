# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import os
import shutil
import tempfile
import zipfile

from django.test import TransactionTestCase
from django.test.utils import override_settings

from ..models import Artist, Album, Song, CustomStorage
from .. import update
from ..utils import (
    delete_empty_instances, full_path, remove_empty_directories,
    sync_song_files, sync_cover_images, titlecase
)


TEST_MEDIA_DIR = tempfile.mkdtemp()
TEST_DROPBOX_DIR = tempfile.mkdtemp()
TEST_FILES_DIR = os.path.join(os.path.dirname(__file__), 'files')


@override_settings(MEDIA_ROOT=TEST_MEDIA_DIR, DROPBOX=TEST_DROPBOX_DIR)
class UtilsTest(TransactionTestCase):

    reset_sequences = True

    def setUp(self):
        if not os.path.exists(TEST_MEDIA_DIR):
            os.mkdir(TEST_MEDIA_DIR)
        if not os.path.exists(TEST_DROPBOX_DIR):
            os.mkdir(TEST_DROPBOX_DIR)

        # Swap CustomStorage for song.filefield and album.cover for
        # testing so that it uses the temporary media folder instead
        # of settings.MEDIA_ROOT
        test_storage = CustomStorage(location=TEST_MEDIA_DIR)
        self._songfield = Song._meta.get_field_by_name('filefield')[0]
        self._default_storage = self._songfield.storage
        self._songfield.storage = test_storage
        self._albumfield = Album._meta.get_field_by_name('cover')[0]
        self._albumfield.storage = test_storage

        # Upload some songs to the library
        zipped_dropbox = os.path.join(TEST_FILES_DIR, 'test_dropbox.zip')
        with zipfile.ZipFile(zipped_dropbox, 'r') as f:
            f.extractall(TEST_DROPBOX_DIR)
        update.update()

    def tearDown(self):
        shutil.rmtree(TEST_MEDIA_DIR)
        shutil.rmtree(TEST_DROPBOX_DIR)
        self._field = self._default_storage

    def assertNoLogError(self):
        """Asserts that nothing was written to the log file."""
        self.assertEqual(os.path.getsize(self.logfile.name), 0)

    def test_sync_song_files(self):
        song = Song.objects.get(pk=1)
        original_filepath = song.filepath
        self.assertEqual(
            song.filepath, 'T/The Artist/The Album/04 - The Fourth Song.ogg')
        self.assertTrue(os.path.exists(full_path(song.filepath)))

        song.title = 'Spam'
        song.save()

        self.assertEqual(
            song.filepath, 'T/The Artist/The Album/04 - Spam.ogg')
        self.assertTrue(os.path.exists(full_path(original_filepath)))
        self.assertFalse(os.path.exists(full_path(song.filepath)))

        sync_song_files()

        self.assertFalse(os.path.exists(full_path(original_filepath)))
        self.assertTrue(os.path.exists(full_path(song.filepath)))

    def test_sync_cover_images(self):
        album = Album.objects.get(pk=1)
        original_coverpath = album.cover_filepath
        self.assertEqual(
            album.cover_filepath, 'T/The Artist/The Album/cover.jpg')
        self.assertTrue(os.path.exists(full_path(album.cover_filepath)))

        album.title = 'Egg'
        album.save()

        self.assertEqual(
            album.cover_filepath, 'T/The Artist/Egg/cover.jpg')
        self.assertTrue(os.path.exists(full_path(original_coverpath)))
        self.assertFalse(os.path.exists(full_path(album.cover_filepath)))

        sync_cover_images()

        self.assertFalse(os.path.exists(full_path(original_coverpath)))
        self.assertTrue(os.path.exists(full_path(album.cover_filepath)))

    def test_sync_songs_and_cover(self):
        artist = Artist.objects.get(pk=1)
        original_path = artist.filepath
        self.assertEqual(artist.filepath, 'T/The Artist')
        self.assertTrue(os.path.exists(full_path(artist.filepath)))
        self.assertTrue(
            os.path.exists(
                os.path.join(
                    full_path(artist.filepath), 'The Album', 'cover.jpg')))

        artist.name = 'Brian'
        artist.save()

        self.assertEqual(artist.filepath, 'B/Brian')
        self.assertTrue(os.path.exists(full_path(original_path)))
        self.assertFalse(os.path.exists(full_path(artist.filepath)))
        self.assertTrue(
            os.path.exists(
                os.path.join(
                    full_path(original_path), 'The Album', 'cover.jpg')))

        sync_song_files()
        sync_cover_images()

        self.assertTrue(os.path.exists(full_path(artist.filepath)))
        self.assertTrue(
            os.path.exists(
                os.path.join(
                    full_path(artist.filepath), 'The Album', 'cover.jpg')))

    def test_remove_empty_directories(self):
        artist = Artist.objects.get(pk=1)
        original_path = artist.filepath

        artist.name = 'Brian'
        artist.save()
        sync_song_files()
        sync_cover_images()

        self.assertTrue(os.path.exists(full_path(original_path)))
        self.assertTrue(os.path.exists(full_path(artist.filepath)))

        remove_empty_directories()

        self.assertFalse(os.path.exists(full_path(original_path)))
        self.assertTrue(os.path.exists(full_path(artist.filepath)))

    def test_delete_empty_instances(self):
        artist = Artist.objects.create(name='Brian')
        Album.objects.create(title='Spam',
                             artist=artist)
        album2 = Album.objects.create(title='Eggs',
                                      artist=artist)
        song = Song.objects.create(title='A song',
                                   album=album2,
                                   bitrate=128000)

        delete_empty_instances()

        # Check that the album 'Spam' has been deleted
        self.assertRaises(Album.DoesNotExist,
                          Album.objects.get,
                          title='Spam')

        # Check that Album.DoesNotExist if not raised for album2
        Album.objects.get(title='Eggs')

        song.delete()
        delete_empty_instances()

        # Check that album2 and artist have been deleted
        self.assertRaises(Album.DoesNotExist,
                          Album.objects.get,
                          title='Eggs')
        self.assertRaises(Artist.DoesNotExist,
                          Artist.objects.get,
                          name='Brian')

    def test_titlecase(self):
        self.assertEqual(titlecase('spam and eggs'), 'Spam And Eggs')
        self.assertEqual(titlecase('Spam And Eggs'), 'Spam And Eggs')
        self.assertEqual(titlecase("spam'n eggs"), "Spam'n Eggs")
        self.assertEqual(titlecase('spàm é ôeufs'), 'Spàm É Ôeufs')
