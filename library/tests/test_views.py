# -*- coding: utf-8 -*-

import os
import shutil
import tempfile
import zipfile
from logging import FileHandler

from django.core.files.base import ContentFile
from django.core.urlresolvers import reverse
from django.http import HttpRequest
from django.test import TransactionTestCase
from django.test.client import Client
from django.test.utils import override_settings

from .. import update
from ..models import Artist, Album, Song, CustomStorage
from ..views import update_library


TEST_MEDIA_DIR = tempfile.mkdtemp()
TEST_DROPBOX_DIR = tempfile.mkdtemp()
TEST_FILES_DIR = os.path.join(os.path.dirname(__file__), 'files')


@override_settings(MEDIA_ROOT=TEST_MEDIA_DIR, DROPBOX=TEST_DROPBOX_DIR)
class ViewTest(TransactionTestCase):

    reset_sequences = True

    def setUp(self):
        self.media_dir = TEST_MEDIA_DIR
        self.dropbox = TEST_DROPBOX_DIR
        if not os.path.exists(TEST_MEDIA_DIR):
            os.mkdir(TEST_MEDIA_DIR)
        if not os.path.exists(TEST_DROPBOX_DIR):
            os.mkdir(TEST_DROPBOX_DIR)

        # use a temporary log file
        self.logfile = tempfile.NamedTemporaryFile(delete=False)
        default_handler = update.LOGGER.handlers[0]
        update.LOGGER.removeHandler(default_handler)
        update.LOGGER.addHandler(FileHandler(self.logfile.name))

        self.mutagen_opts = update.get_mutagen_audio_options()

        # Swap CustomStorage for filefield for testing so that it uses
        # the temporary media folder instead of settings.MEDIA_ROOT
        self._field = Song._meta.get_field_by_name('filefield')[0]
        self._default_storage = self._field.storage
        test_storage = CustomStorage(location=self.media_dir)
        self._field.storage = test_storage

    def tearDown(self):
        os.remove(self.logfile.name)
        shutil.rmtree(self.media_dir)
        shutil.rmtree(self.dropbox)
        self._field = self._default_storage

    def assertNoLogError(self):
        """Asserts that nothing was written to the log file."""
        self.assertEqual(os.path.getsize(self.logfile.name), 0)

    def test_get_song_info_mp3(self):
        filename = os.path.join(TEST_FILES_DIR, 'testfile.mp3')
        info = update.get_song_info(filename, self.mutagen_opts)

        self.assertEqual(info.artist, 'The Artist')
        self.assertEqual(info.album, 'The Album')
        self.assertEqual(info.title, 'The Song')
        self.assertEqual(info.track, '01')
        self.assertEqual(info.bitrate, 320000)
        self.assertNoLogError()

    def test_get_song_info_mp4(self):
        filename = os.path.join(TEST_FILES_DIR, 'testfile.m4a')
        info = update.get_song_info(filename, self.mutagen_opts)

        self.assertEqual(info.artist, 'The Artist')
        self.assertEqual(info.album, 'The Album')
        self.assertEqual(info.title, 'The Song')
        self.assertEqual(info.track, '01')
        self.assertEqual(info.bitrate, 128000)
        self.assertNoLogError()

    def test_get_song_info_ogg(self):
        filename = os.path.join(TEST_FILES_DIR, 'testfile.ogg')
        info = update.get_song_info(filename, self.mutagen_opts)

        self.assertEqual(info.artist, 'The Artist')
        self.assertEqual(info.album, 'The Album')
        self.assertEqual(info.title, 'The Song')
        self.assertEqual(info.track, '01')
        self.assertEqual(info.bitrate, 160000)
        self.assertNoLogError()

    def test_get_song_info_flac(self):
        filename = os.path.join(TEST_FILES_DIR, 'testfile.flac')
        info = update.get_song_info(filename, self.mutagen_opts)

        self.assertEqual(info.artist, 'The Artist')
        self.assertEqual(info.album, 'The Album')
        self.assertEqual(info.title, 'The Song')
        self.assertEqual(info.track, '01')
        self.assertEqual(info.bitrate, 0)
        self.assertNoLogError()

    def test_get_song_info_wma(self):
        filename = os.path.join(TEST_FILES_DIR, 'testfile.wma')
        info = update.get_wma_info(filename)

        self.assertEqual(info.artist, 'The Artist')
        self.assertEqual(info.album, 'The Album')
        self.assertEqual(info.title, 'The Song')
        self.assertEqual(info.track, '01')
        self.assertEqual(info.bitrate, 198000)
        self.assertNoLogError()

    def test_get_song_info_unicode_file(self):
        filename = os.path.join(TEST_FILES_DIR, u'ȕñĭçợƌɇ⸞ƒıℓⱻ.ogg')
        info = update.get_song_info(filename, self.mutagen_opts)

        self.assertEqual(info.artist, u'ṫħĕ Ⓐ řⱦⅈṩȶ')
        self.assertEqual(info.album, 'The Album')
        self.assertEqual(info.title, 'The Song')
        self.assertEqual(info.track, '01')
        self.assertEqual(info.bitrate, 160000)
        self.assertNoLogError()

    def test_import_file(self):
        # put test file in dropbox
        shutil.copy(os.path.join(TEST_FILES_DIR, 'testfile.ogg'),
                    self.dropbox)
        filename = os.path.join(self.dropbox, 'testfile.ogg')

        self.assertFalse(Artist.objects.exists())
        self.assertFalse(Album.objects.exists())
        self.assertFalse(Song.objects.exists())
        self.assertTrue(os.path.exists(filename))

        with open(filename, 'rb') as f:
            original_content = f.read()

        # import file
        update.import_file(filename, self.mutagen_opts)
        song = Song.objects.get(title='The Song')

        self.assertEqual(song.title, 'The Song')
        self.assertEqual(song.album.title, 'The Album')
        self.assertEqual(song.album.artist.name, 'The Artist')
        self.assertEqual(song.track, '01')
        self.assertEqual(song.bitrate, 160000)
        self.assertEqual(song.filetype, 'ogg')
        self.assertEqual(song.original_path, 'testfile.ogg')
        self.assertEqual(song.filefield.read(), original_content)
        self.assertFalse(os.path.exists(filename))
        self.assertNoLogError()

    def test_import_existing_file_with_no_better_bitrate_skips_it(self):
        # put test files in dropbox
        shutil.copy(os.path.join(TEST_FILES_DIR, 'testfile.ogg'),
                    self.dropbox)
        shutil.copy(os.path.join(TEST_FILES_DIR, 'testfile.ogg'),
                    os.path.join(self.dropbox, 'testfile_copy.ogg'))

        # import files
        filename = os.path.join(self.dropbox, 'testfile.ogg')
        update.import_file(filename, self.mutagen_opts)
        filename = os.path.join(self.dropbox, 'testfile_copy.ogg')
        update.import_file(filename, self.mutagen_opts)

        with open(self.logfile.name, 'r') as f:
            log_record = f.read()

        self.assertIn('Problem importing file', log_record)
        self.assertIn('The Song by The Artist already exists', log_record)
        self.assertTrue(os.path.exists(filename))

    def test_import_existing_file_with_better_bitrate_replaces_it(self):
        # put test files in dropbox
        shutil.copy(os.path.join(TEST_FILES_DIR, 'testfile-128k.mp3'),
                    self.dropbox)
        shutil.copy(os.path.join(TEST_FILES_DIR, 'testfile.mp3'),
                    self.dropbox)

        # import files
        filename = os.path.join(self.dropbox, 'testfile-128k.mp3')
        update.import_file(filename, self.mutagen_opts)
        song = Song.objects.get(title='The Song')
        self.assertEqual(song.bitrate, 128000)

        filename = os.path.join(self.dropbox, 'testfile.mp3')
        update.import_file(filename, self.mutagen_opts)

        self.assertEqual(Song.objects.count(), 1)

        song = Song.objects.get(title='The Song')
        self.assertEqual(song.bitrate, 320000)

        self.assertNoLogError()

    def test_importing_unsupported_format_gives_an_error(self):
        # put file in dropbox and import it
        shutil.copy(os.path.join(TEST_FILES_DIR, 'testfile.wav'),
                    self.dropbox)
        filename = os.path.join(self.dropbox, 'testfile.wav')
        update.import_file(filename, self.mutagen_opts)

        with open(self.logfile.name, 'r') as f:
            log_record = f.read()

        self.assertIn('Problem importing file', log_record)
        self.assertIn('testfile.wav (Mutagen could not read', log_record)
        self.assertTrue(os.path.exists(filename))

    def test_importing_dummy_file_removes_it_from_dropbox(self):
        # create the dummy file
        filename = os.path.join(self.dropbox, '.DS_Store')
        with open(filename, 'w'):
            pass

        self.assertTrue(os.path.exists(filename))

        update.update()

        self.assertFalse(os.path.exists(filename))
        self.assertNoLogError()

    def test_upload_dropbox_files_to_library(self):
        # Put some files in dropbox
        zipped_dropbox = os.path.join(TEST_FILES_DIR, 'test_dropbox.zip')
        with zipfile.ZipFile(zipped_dropbox, 'r') as f:
            f.extractall(self.dropbox)

        self.assertItemsEqual(os.listdir(self.dropbox),
                              ['song1.ogg', 'The Artist', 'Unknown'])
        self.assertItemsEqual(
            os.listdir(os.path.join(self.dropbox, 'The Artist')),
            ['Album', 'song2.ogg', 'song3.ogg'])
        self.assertItemsEqual(
            os.listdir(os.path.join(self.dropbox, 'Unknown')),
            ['song5.ogg', 'song6.ogg'])

        # Upload files to library
        update_library(HttpRequest())

        # Check that the files have been imported
        self.assertNoLogError()
        self.assertEqual(os.listdir(self.dropbox), [])

        self.assertEqual(Artist.objects.count(), 2)
        self.assertEqual(Album.objects.count(), 4)
        self.assertEqual(Song.objects.count(), 6)

        self.assertItemsEqual(os.listdir(self.media_dir), ['L', 'T'])
        filename = os.path.join(self.media_dir, 'T', 'The Artist',
                                'The Album', '04 - The Fourth Song.ogg')
        self.assertTrue(os.path.exists(filename))

    def test_download_artist(self):
        # Upload some files
        zipped_dropbox = os.path.join(TEST_FILES_DIR, 'test_dropbox.zip')
        with zipfile.ZipFile(zipped_dropbox, 'r') as f:
            f.extractall(self.dropbox)
        update.update()

        # make request
        c = Client()
        response = c.get(reverse('download_artist', args=[1]))

        # check response have right headers
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/zip')
        self.assertEqual(response['Content-Disposition'],
                         'attachment; filename=The%20Artist.zip')

        # check structure of returned zip file
        songs = Song.objects.filter(album__artist=1)
        original_song_names = [s.filefield.name[2:] for s in songs]

        content = ContentFile(response.content)
        self.assertTrue(zipfile.is_zipfile(content))
        with zipfile.ZipFile(content, 'r') as z:
            self.assertIsNone(z.testzip())
            self.assertItemsEqual(z.namelist(), original_song_names)

    def test_download_artist_with_no_songs_redirects_to_detail_view(self):
        # Create dummy artist
        a = Artist.objects.create(name='The Artist')

        # make request
        c = Client()
        response = c.get(reverse('download_artist', args=[a.pk]))

        # check response have right headers
        self.assertEqual(response.status_code, 302)
        redirect_url = response.get('Location', '')
        self.assertEqual(
            redirect_url,
            'http://testserver' + reverse('artist_detail', args=[a.pk]))

        # check that a message has been set in the cookie
        self.assertTrue('messages' in response.cookies.keys())
        self.assertIn('The artist does not have any song',
                      response.cookies.get('messages').value)

    def test_download_updated_artist_retrieve_the_correct_file_structure(self):
        pass

    def test_fetching_url_of_nonexisting_instance_redirects_to_list_view(self):
        c = Client()
        response = c.get(reverse('artist_detail', args=[1]))
        self.assertEqual(response.status_code, 302)
        redirect_url = response.get('Location', '')
        self.assertEqual(redirect_url,
                         'http://testserver' + reverse('artist_list'))

    def test_fetching_other_nonexisting_url_returns_404(self):
        c = Client()
        response = c.get('/spam/and/eggs')
        self.assertEqual(response.status_code, 404)
