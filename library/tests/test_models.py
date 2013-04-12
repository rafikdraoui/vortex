import os
import shutil
import tempfile

from django.core.files import File
from django.db import IntegrityError
from django.test import TransactionTestCase
from django.test.utils import override_settings

from ..models import Artist, Album, Song, CustomStorage
from ..utils import full_path


TEST_MEDIA_DIR = tempfile.mkdtemp()


@override_settings(MEDIA_ROOT=TEST_MEDIA_DIR)
class ModelTest(TransactionTestCase):

    def setUp(self):
        self.media_dir = TEST_MEDIA_DIR
        if not os.path.exists(TEST_MEDIA_DIR):
            os.mkdir(TEST_MEDIA_DIR)
        self.media_file = tempfile.NamedTemporaryFile(suffix='.ogg',
                                                      delete=False)
        self.media_file.write("""
        Lorem ipsum dolor sit amet, consectetur adipiscing elit. Quisque
        feugiat sem velit, sed rutrum urna. Etiam sed varius risus. Aenean
        consequat enim magna. Praesent sed metus tellus, eget sagittis sem.
        """)
        self.media_file.close()

        cover_file = os.path.join(
            os.path.dirname(__file__), 'files', 'cover.jpg')
        self.cover_art = File(open(cover_file, 'rb'))

        # Swap CustomStorage for song.filefield and album.cover for
        # testing so that it uses the temporary media folder instead
        # of settings.MEDIA_ROOT
        test_storage = CustomStorage(location=self.media_dir)
        self._songfield = Song._meta.get_field_by_name('filefield')[0]
        self._default_storage = self._songfield.storage
        self._songfield.storage = test_storage
        self._albumfield = Album._meta.get_field_by_name('cover')[0]
        self._albumfield.storage = test_storage

    def tearDown(self):
        os.remove(self.media_file.name)
        shutil.rmtree(self.media_dir)
        self._songfield = self._default_storage
        self._albumfield = self._default_storage


@override_settings(MEDIA_ROOT=TEST_MEDIA_DIR)
class ArtistModelTest(ModelTest):

    def setUp(self):
        super(ArtistModelTest, self).setUp()

        artist1 = Artist.objects.create(name='First Artist')
        album1 = Album.objects.create(title='First Album',
                                      artist=artist1,
                                      cover=self.cover_art,
                                      cover_file_type='jpg')
        Song.objects.create(title='The First Song',
                            album=album1,
                            bitrate=128000,
                            filetype='ogg',
                            first_save=True,
                            filefield=File(open(self.media_file.name)))

        artist2 = Artist.objects.create(name='Other Artist')
        album2 = Album.objects.create(title='Second Album',
                                      artist=artist2,
                                      cover=self.cover_art,
                                      cover_file_type='jpg')
        Song.objects.create(title='Second Song',
                            album=album2,
                            bitrate=128000,
                            track='02',
                            filetype='ogg',
                            first_save=True,
                            filefield=File(open(self.media_file.name)))

        common_album1 = Album.objects.create(title='Common Album',
                                             artist=artist1,
                                             cover=self.cover_art,
                                             cover_file_type='jpg')
        Song.objects.create(title='Common Song 1',
                            album=common_album1,
                            bitrate=128000,
                            filetype='ogg',
                            first_save=True,
                            filefield=File(open(self.media_file.name)))
        Song.objects.create(title='Common Song 3',
                            album=common_album1,
                            bitrate=128000,
                            filetype='ogg',
                            first_save=True,
                            filefield=File(open(self.media_file.name)))

        common_album2 = Album.objects.create(title='Common Album',
                                             artist=artist2,
                                             cover=self.cover_art,
                                             cover_file_type='jpg')
        Song.objects.create(title='Common Song 2',
                            album=common_album2,
                            bitrate=128000,
                            filetype='ogg',
                            first_save=True,
                            filefield=File(open(self.media_file.name)))
        Song.objects.create(title='Common Song 3',
                            album=common_album2,
                            bitrate=128000,
                            filetype='ogg',
                            first_save=True,
                            filefield=File(open(self.media_file.name)))

    def test_merge_artists(self):
        artist1 = Artist.objects.get(name='First Artist')
        artist2 = Artist.objects.get(name='Other Artist')

        self.assertEqual(artist1.albums.count(), 2)
        self.assertEqual(artist2.albums.count(), 2)

        artist1.name = 'Other Artist'
        artist1.save()

        self.assertRaises(Artist.DoesNotExist,
                          Artist.objects.get,
                          name='First Artist')

        # Check that Album.DoesNotExist is not thrown
        Album.objects.get(title='First Album')

        self.assertEqual(artist2.albums.count(), 3)
        self.assertItemsEqual(
            artist2.albums.values_list('title', flat=True),
            ['First Album', 'Second Album', 'Common Album'])

        # Check to see that the songs of the common album were merged
        common_album = artist2.albums.get(title='Common Album')
        self.assertEqual(common_album.songs.count(), 3)
        self.assertItemsEqual(
            common_album.songs.values_list('title', flat=True),
            ['Common Song 1', 'Common Song 2', 'Common Song 3'])

    def test_save_artist_without_change_is_idempotent(self):
        artist = Artist.objects.get(name='First Artist')
        self.assertEqual(artist.name, 'First Artist')
        self.assertEqual(artist.filepath, 'F/First Artist')
        self.assertItemsEqual(
            artist.albums.values_list('title', flat=True),
            ['First Album', 'Common Album'])
        self.assertTrue(os.path.exists(full_path(artist.filepath)))
        self.assertItemsEqual(os.listdir(full_path(artist.filepath)),
                              ['First Album', 'Common Album'])

        artist.save()

        self.assertEqual(artist.name, 'First Artist')
        self.assertEqual(artist.filepath, 'F/First Artist')
        self.assertItemsEqual(
            artist.albums.values_list('title', flat=True),
            ['First Album', 'Common Album'])
        self.assertTrue(os.path.exists(full_path(artist.filepath)))
        self.assertItemsEqual(os.listdir(full_path(artist.filepath)),
                              ['First Album', 'Common Album'])


@override_settings(MEDIA_ROOT=TEST_MEDIA_DIR)
class AlbumModelTest(ModelTest):

    def setUp(self):
        super(AlbumModelTest, self).setUp()

        artist = Artist.objects.create(name='The Artist')
        album1 = Album.objects.create(title='First Album',
                                      artist=artist,
                                      cover=self.cover_art,
                                      cover_file_type='jpg')
        Song.objects.create(title='The First Song',
                            album=album1,
                            bitrate=128000,
                            filetype='ogg',
                            first_save=True,
                            filefield=File(open(self.media_file.name)))

        album2 = Album.objects.create(title='Second Album',
                                      artist=artist,
                                      cover=self.cover_art,
                                      cover_file_type='jpg')
        Song.objects.create(title='Second Song',
                            album=album2,
                            bitrate=128000,
                            track='2',
                            filetype='ogg',
                            first_save=True,
                            filefield=File(open(self.media_file.name)))

    def test_merge_albums(self):
        album1 = Album.objects.get(title='First Album')
        album2 = Album.objects.get(title='Second Album')

        self.assertEqual(album1.songs.count(), 1)
        self.assertEqual(album2.songs.count(), 1)

        album1.title = 'Second Album'
        album1.save()

        self.assertRaises(Album.DoesNotExist,
                          Album.objects.get,
                          title='First Album')

        self.assertEqual(album2.songs.count(), 2)
        self.assertItemsEqual(
            album2.songs.values_list('title', flat=True),
            ['The First Song', 'Second Song'])

    def test_omitting_skip_merge_check_raises_integrity_error(self):
        album = Album.objects.get(title='First Album')
        album.title = 'Second Album'
        self.assertRaises(IntegrityError,
                          album.save,
                          skip_merge_check=True)

    def test_save_album_without_change_is_idempotent(self):
        album = Album.objects.get(title='First Album')
        self.assertEqual(album.title, 'First Album')
        self.assertEqual(album.artist.name, 'The Artist')
        self.assertEqual(album.filepath, 'T/The Artist/First Album')
        self.assertTrue(os.path.exists(full_path(album.filepath)))
        self.assertItemsEqual(os.listdir(full_path(album.filepath)),
                              ['cover.jpg', 'The First Song.ogg'])

        album.save()

        self.assertEqual(album.title, 'First Album')
        self.assertEqual(album.artist.name, 'The Artist')
        self.assertEqual(album.filepath, 'T/The Artist/First Album')
        self.assertTrue(os.path.exists(full_path(album.filepath)))
        self.assertItemsEqual(os.listdir(full_path(album.filepath)),
                              ['cover.jpg', 'The First Song.ogg'])


@override_settings(MEDIA_ROOT=TEST_MEDIA_DIR)
class SongModelTest(ModelTest):

    def setUp(self):
        super(SongModelTest, self).setUp()

        self.artist = Artist.objects.create(name='The Artist')
        album = Album.objects.create(title='The Album',
                                     artist=self.artist,
                                     cover=self.cover_art,
                                     cover_file_type='jpg')
        self.song = Song(title='The Song', album=album, bitrate=128000,
                         filetype='ogg', first_save=True,
                         filefield=File(open(self.media_file.name)))
        self.song.save()

    def test_save_new_song_creates_file_in_media_directory(self):
        filename = os.path.join(
            self.media_dir, 'T', 'The Artist', 'The Album', 'The Song.ogg')

        self.assertEqual(os.listdir(self.media_dir), ['T'])
        self.assertTrue(os.path.exists(filename))
        self.assertEqual(open(self.media_file.name).read(),
                         open(filename).read())

    def test_save_song_without_change_is_idempotent(self):
        self.assertEqual(self.song.title, 'The Song')
        self.assertEqual(self.song.album.title, 'The Album')
        self.assertEqual(self.song.album.artist.name, 'The Artist')
        self.assertEqual(self.song.filefield.name,
                         'T/The Artist/The Album/The Song.ogg')
        self.assertTrue(os.path.exists(full_path(self.song.filefield.name)))

        original_content = self.song.filefield.read()

        self.song.save()

        self.assertEqual(self.song.title, 'The Song')
        self.assertEqual(self.song.album.title, 'The Album')
        self.assertEqual(self.song.album.artist.name, 'The Artist')
        self.assertEqual(self.song.filefield.name,
                         'T/The Artist/The Album/The Song.ogg')
        self.assertTrue(os.path.exists(full_path(self.song.filefield.name)))

        self.song.filefield.seek(0)
        current_content = self.song.filefield.read()

        self.assertEqual(original_content, current_content)

    def test_leading_zero_for_single_digit_track(self):
        self.song.track = '1'
        self.song.save()
        self.assertNotEqual(self.song.track, '1')
        self.assertEqual(self.song.track, '01')
