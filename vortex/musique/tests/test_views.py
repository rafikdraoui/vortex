import os
import shutil
import tempfile
import zipfile
from logging import FileHandler

from django.core.files.base import ContentFile
from django.http import HttpRequest
from django.test import TestCase
from django.test.client import Client
from django.test.utils import override_settings

from vortex.musique import library
from vortex.musique.models import Artist, Album, Song
from vortex.musique.utils import CustomStorage
from vortex.musique.views import update_library


TEST_MEDIA_DIR = tempfile.mkdtemp()
TEST_DROPBOX_DIR = tempfile.mkdtemp()
TEST_FILES_DIR = os.path.join(os.path.dirname(__file__), 'files')


@override_settings(MEDIA_ROOT=TEST_MEDIA_DIR, DROPBOX=TEST_DROPBOX_DIR)
class ViewTest(TestCase):

    def setUp(self):
        self.media_dir = TEST_MEDIA_DIR
        self.dropbox = TEST_DROPBOX_DIR
        if not os.path.exists(TEST_MEDIA_DIR):
            os.mkdir(TEST_MEDIA_DIR)
        if not os.path.exists(TEST_DROPBOX_DIR):
            os.mkdir(TEST_DROPBOX_DIR)

        # use a temporary log file
        self.logfile = tempfile.NamedTemporaryFile(delete=False)
        default_handler = library.LOGGER.handlers[0]
        library.LOGGER.removeHandler(default_handler)
        library.LOGGER.addHandler(FileHandler(self.logfile.name))

        self.mutagen_opts = library.get_mutagen_audio_options()

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
        self.assertEquals(os.path.getsize(self.logfile.name), 0)

    def test_get_song_info_mp3(self):
        filename = os.path.join(TEST_FILES_DIR, 'testfile.mp3')
        info = library.get_song_info(filename, self.mutagen_opts)

        self.assertEquals(info['artist'], 'The Artist')
        self.assertEquals(info['album'], 'The Album')
        self.assertEquals(info['title'], 'The Song')
        self.assertEquals(info['track'], '01')
        self.assertEquals(info['bitrate'], 320000)
        self.assertNoLogError()

    def test_get_song_info_mp4(self):
        filename = os.path.join(TEST_FILES_DIR, 'testfile.m4a')
        info = library.get_song_info(filename, self.mutagen_opts)

        self.assertEquals(info['artist'], 'The Artist')
        self.assertEquals(info['album'], 'The Album')
        self.assertEquals(info['title'], 'The Song')
        self.assertEquals(info['track'], '01')
        self.assertEquals(info['bitrate'], 128000)
        self.assertNoLogError()

    def test_get_song_info_ogg(self):
        filename = os.path.join(TEST_FILES_DIR, 'testfile.ogg')
        info = library.get_song_info(filename, self.mutagen_opts)

        self.assertEquals(info['artist'], 'The Artist')
        self.assertEquals(info['album'], 'The Album')
        self.assertEquals(info['title'], 'The Song')
        self.assertEquals(info['track'], '01')
        self.assertEquals(info['bitrate'], 160000)
        self.assertNoLogError()

    def test_get_song_info_flac(self):
        filename = os.path.join(TEST_FILES_DIR, 'testfile.flac')
        info = library.get_song_info(filename, self.mutagen_opts)

        self.assertEquals(info['artist'], 'The Artist')
        self.assertEquals(info['album'], 'The Album')
        self.assertEquals(info['title'], 'The Song')
        self.assertEquals(info['track'], '01')
        self.assertEquals(info['bitrate'], 0)
        self.assertNoLogError()

    def test_get_song_info_wma(self):
        filename = os.path.join(TEST_FILES_DIR, 'testfile.wma')
        info = library.get_wma_info(filename)

        self.assertEquals(info['artist'], 'The Artist')
        self.assertEquals(info['album'], 'The Album')
        self.assertEquals(info['title'], 'The Song')
        self.assertEquals(info['track'], '01')
        self.assertEquals(info['bitrate'], 198000)
        self.assertNoLogError()

    def test_import_file(self):
        # put test file in dropbox
        shutil.copy(os.path.join(TEST_FILES_DIR, 'testfile.ogg'),
                    self.dropbox)
        filename = os.path.join(self.dropbox, 'testfile.ogg')

        self.assertEquals(len(Artist.objects.all()), 0)
        self.assertEquals(len(Album.objects.all()), 0)
        self.assertEquals(len(Song.objects.all()), 0)
        self.assertTrue(os.path.exists(filename))

        with open(filename, 'rb') as f:
            original_content = f.read()

        # import file
        library.import_file(filename, self.mutagen_opts)
        song = Song.objects.get(title='The Song')

        self.assertEquals(song.title, 'The Song')
        self.assertEquals(song.album.title, 'The Album')
        self.assertEquals(song.artist.name, 'The Artist')
        self.assertEquals(song.track, '01')
        self.assertEquals(song.bitrate, 160000)
        self.assertEquals(song.filetype, 'ogg')
        self.assertEquals(song.original_path, 'testfile.ogg')
        self.assertEquals(song.filefield.read(), original_content)
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
        library.import_file(filename, self.mutagen_opts)
        filename = os.path.join(self.dropbox, 'testfile_copy.ogg')
        library.import_file(filename, self.mutagen_opts)

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
        library.import_file(filename, self.mutagen_opts)
        song = Song.objects.get(title='The Song')
        self.assertEquals(song.bitrate, 128000)

        filename = os.path.join(self.dropbox, 'testfile.mp3')
        library.import_file(filename, self.mutagen_opts)

        self.assertEquals(len(Song.objects.all()), 1)

        song = Song.objects.get(title='The Song')
        self.assertEquals(song.bitrate, 320000)

        self.assertNoLogError()

    def test_importing_unsupported_format_gives_an_error(self):
        # put file in dropbox and import it
        shutil.copy(os.path.join(TEST_FILES_DIR, 'testfile.wav'),
                    self.dropbox)
        filename = os.path.join(self.dropbox, 'testfile.wav')
        library.import_file(filename, self.mutagen_opts)

        with open(self.logfile.name, 'r') as f:
            log_record = f.read()

        self.assertIn('Problem importing file', log_record)
        self.assertIn('testfile.wav (mutagen error)', log_record)
        self.assertTrue(os.path.exists(filename))

    def test_importing_dummy_file_removes_it_from_dropbox(self):
        # create the dummy file
        filename = os.path.join(self.dropbox, '.DS_Store')
        with open(filename, 'w'):
            pass

        self.assertTrue(os.path.exists(filename))

        library.update()

        self.assertFalse(os.path.exists(filename))
        self.assertNoLogError()

    def test_upload_dropbox_files_to_library(self):
        # Put some files in dropbox
        zipped_dropbox = os.path.join(TEST_FILES_DIR, 'test_dropbox.zip')
        with zipfile.ZipFile(zipped_dropbox, 'r') as f:
            f.extractall(self.dropbox)

        self.assertEquals(sorted(os.listdir(self.dropbox)),
                          sorted(['song1.ogg', 'The Artist', 'Unknown']))
        self.assertEquals(
            sorted(os.listdir(os.path.join(self.dropbox, 'The Artist'))),
            sorted(['Album', 'song2.ogg', 'song3.ogg']))
        self.assertEquals(
            sorted(os.listdir(os.path.join(self.dropbox, 'Unknown'))),
            sorted(['song5.ogg', 'song6.ogg']))

        # Upload files to library
        update_library(HttpRequest())

        # Check that the files have been imported
        self.assertNoLogError()
        self.assertEquals(os.listdir(self.dropbox), [])

        all_artists = Artist.objects.all()
        all_albums = Album.objects.all()
        all_songs = Song.objects.all()

        self.assertEquals(len(all_artists), 2)
        self.assertEquals(len(all_albums), 4)
        self.assertEquals(len(all_songs), 6)

        self.assertEquals(sorted(os.listdir(self.media_dir)),
                          sorted(['L', 'T']))
        filename = os.path.join(self.media_dir, 'T', 'The Artist',
                                'The Album', '04 - The Fourth Song.ogg')
        self.assertTrue(os.path.exists(filename))

    def test_download_artist(self):
        # Upload some files
        zipped_dropbox = os.path.join(TEST_FILES_DIR, 'test_dropbox.zip')
        with zipfile.ZipFile(zipped_dropbox, 'r') as f:
            f.extractall(self.dropbox)
        library.update()

        # make request
        c = Client()
        response = c.get('/musique/artist/1/download/')

        # check response have right headers
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/zip')
        self.assertEqual(response['Content-Disposition'],
                         'attachment; filename=The%20Artist.zip')

        # check structure of returned zip file
        songs = Artist.objects.get(pk=1).song_set.all()
        original_song_names = map(lambda s: s.filefield.name[2:],
                                  list(songs))

        content = ContentFile(response.content)
        self.assertTrue(zipfile.is_zipfile(content))
        with zipfile.ZipFile(content, 'r') as z:
            self.assertIsNone(z.testzip())
            self.assertEqual(sorted(z.namelist()), sorted(original_song_names))

    def test_download_artist_with_no_songs_redirects_to_detail_view(self):
        # Create dummy artist
        Artist.objects.create(name='The Artist')

        # make request
        c = Client()
        response = c.get('/musique/artist/1/download/')

        # check response have right headers
        self.assertEqual(response.status_code, 302)
        redirect_url = response.get('Location', '')
        self.assertEqual(redirect_url, 'http://testserver/musique/artist/1/')

        # check that a message has been set in the cookie
        self.assertTrue('messages' in response.cookies.keys())
        self.assertIn('The artist does not have any song',
                      response.cookies.get('messages').value)

    def test_fetching_url_of_nonexisting_instance_redirects_to_list_view(self):
        c = Client()
        response = c.get('/musique/artist/1/')
        self.assertEqual(response.status_code, 302)
        redirect_url = response.get('Location', '')
        self.assertEqual(redirect_url, 'http://testserver/musique/artist/')

    def test_fetching_other_nonexisting_url_returns_404(self):
        c = Client()
        response = c.get('/musique/artist/bob/')
        self.assertEqual(response.status_code, 404)
