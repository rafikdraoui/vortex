import os
import shutil
import tempfile
from logging import FileHandler

from django.core.exceptions import ValidationError
from django.core.files import File
from django.test import TestCase
from django.test.utils import override_settings

from vortex.musique.models import Artist, Album, Song, LOGGER
from vortex.musique.utils import CustomStorage, full_path


TEST_MEDIA_DIR = tempfile.mkdtemp()


@override_settings(MEDIA_ROOT=TEST_MEDIA_DIR)
class ModelTest(TestCase):

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

        # use a temporary log file
        self.logfile = tempfile.NamedTemporaryFile(delete=False)
        default_handler = LOGGER.handlers[0]
        LOGGER.removeHandler(default_handler)
        LOGGER.addHandler(FileHandler(self.logfile.name))

        # Swap CustomStorage for filefield for testing so that it uses
        # the temporary media folder instead of settings.MEDIA_ROOT
        self._field = Song._meta.get_field_by_name('filefield')[0]
        self._default_storage = self._field.storage
        test_storage = CustomStorage(location=self.media_dir)
        self._field.storage = test_storage

    def tearDown(self):
        os.remove(self.media_file.name)
        os.remove(self.logfile.name)
        shutil.rmtree(self.media_dir)
        self._field = self._default_storage

    def assertNoLogError(self):
        """Asserts that nothing was written to the log file."""
        self.assertEquals(os.path.getsize(self.logfile.name), 0)


@override_settings(MEDIA_ROOT=TEST_MEDIA_DIR)
class ArtistModelTest(ModelTest):

    def setUp(self):
        super(ArtistModelTest, self).setUp()

        artist1 = Artist.objects.create(name='First Artist')
        album1 = Album.objects.create(title='First Album', artist=artist1)
        Song.objects.create(title='The First Song',
                            artist=artist1,
                            album=album1,
                            bitrate=128000,
                            filetype='ogg',
                            first_save=True,
                            filefield=File(open(self.media_file.name)))

        artist2 = Artist.objects.create(name='Other Artist')
        album2 = Album.objects.create(title='Second Album', artist=artist2)
        Song.objects.create(title='Second Song',
                            artist=artist2,
                            album=album2,
                            bitrate=128000,
                            track='02',
                            filetype='ogg',
                            first_save=True,
                            filefield=File(open(self.media_file.name)))

        common_album1 = Album.objects.create(title='Common Album',
                                             artist=artist1)
        Song.objects.create(title='Common Song 1',
                            artist=artist1,
                            album=common_album1,
                            bitrate=128000,
                            filetype='ogg',
                            first_save=True,
                            filefield=File(open(self.media_file.name)))
        Song.objects.create(title='Common Song 3',
                            artist=artist1,
                            album=common_album1,
                            bitrate=128000,
                            filetype='ogg',
                            first_save=True,
                            filefield=File(open(self.media_file.name)))

        common_album2 = Album.objects.create(title='Common Album',
                                             artist=artist2)
        Song.objects.create(title='Common Song 2',
                            artist=artist2,
                            album=common_album2,
                            bitrate=128000,
                            filetype='ogg',
                            first_save=True,
                            filefield=File(open(self.media_file.name)))
        Song.objects.create(title='Common Song 3',
                            artist=artist2,
                            album=common_album2,
                            bitrate=128000,
                            filetype='ogg',
                            first_save=True,
                            filefield=File(open(self.media_file.name)))

    def test_rename_artist_to_non_existent_artist_renames_folder(self):
        artist = Artist.objects.get(name='First Artist')
        original_artist_path = full_path(artist.filepath)
        album = artist.album_set.get(pk=1)
        original_album_path = full_path(album.filepath)
        original_song_names = os.listdir(original_album_path)

        self.assertTrue(os.path.exists(original_artist_path))
        self.assertTrue(os.path.exists(original_album_path))
        self.assertRaises(Artist.DoesNotExist,
                          Artist.objects.get,
                          name='Premier Artiste')

        artist.name = 'Premier Artiste'
        artist.save()

        # Check that Artist.DoesNotExist is not thrown
        Artist.objects.get(name='Premier Artiste')

        self.assertEquals(artist.filepath,
                          os.path.join('P', 'Premier Artiste'))

        new_artist_path = full_path(artist.filepath)
        new_album_path = full_path(artist.album_set.get(pk=1).filepath)
        new_song_names = os.listdir(new_album_path)

        self.assertTrue(os.path.exists(new_artist_path))
        self.assertFalse(os.path.exists(original_artist_path))
        self.assertTrue(os.path.exists(new_album_path))
        self.assertFalse(os.path.exists(original_album_path))

        self.assertEqual(artist.album_set.get(pk=1), album)
        self.assertEqual(album.artist, artist)
        self.assertEquals(original_song_names, new_song_names)

        self.assertNoLogError()

    def test_rename_artist_to_existing_artist_merges_folders(self):
        artist1 = Artist.objects.get(name='First Artist')
        artist2 = Artist.objects.get(name='Other Artist')
        original_filename = full_path(artist1.filepath)

        self.assertEquals(len(artist1.album_set.all()), 2)
        self.assertEquals(len(artist2.album_set.all()), 2)

        artist1.name = 'Other Artist'
        artist1.save()

        self.assertRaises(Artist.DoesNotExist,
                          Artist.objects.get,
                          name='First Artist')
        self.assertFalse(os.path.exists(original_filename))

        # Check that Album.DoesNotExist is not thrown
        Album.objects.get(title='First Album')

        albums = artist2.album_set.all()
        self.assertEquals(len(albums), 3)
        self.assertEquals(
            sorted(os.listdir(full_path(artist2.filepath))),
            sorted(['First Album', 'Second Album', 'Common Album']))

        # Check to see that the songs of the common album were merged
        common_album = artist2.album_set.get(title='Common Album')
        self.assertEquals(len(common_album.song_set.all()), 3)
        self.assertEquals(sorted(os.listdir(full_path(common_album.filepath))),
                          sorted(['Common Song 1.ogg',
                                  'Common Song 2.ogg',
                                  'Common Song 3.ogg']))

        self.assertNoLogError()

    def test_save_artist_without_change_is_idempotent(self):
        artist = Artist.objects.get(name='First Artist')
        self.assertEquals(artist.name, 'First Artist')
        self.assertEquals(artist.filepath, 'F/First Artist')
        self.assertTrue(os.path.exists(full_path(artist.filepath)))
        self.assertEquals(sorted(os.listdir(full_path(artist.filepath))),
                          sorted(['First Album', 'Common Album']))

        artist.save()

        self.assertEquals(artist.name, 'First Artist')
        self.assertEquals(artist.filepath, 'F/First Artist')
        self.assertTrue(os.path.exists(full_path(artist.filepath)))
        self.assertEquals(sorted(os.listdir(full_path(artist.filepath))),
                          sorted(['First Album', 'Common Album']))
        self.assertNoLogError()

    def test_delete_artist_removes_folder(self):
        artist = Artist.objects.get(name='First Artist')
        filename = full_path(artist.filepath)
        self.assertTrue(os.path.exists(filename))

        artist.delete()

        self.assertFalse(os.path.exists(filename))
        self.assertNoLogError()


@override_settings(MEDIA_ROOT=TEST_MEDIA_DIR)
class AlbumModelTest(ModelTest):

    def setUp(self):
        super(AlbumModelTest, self).setUp()

        artist = Artist.objects.create(name='The Artist')
        album1 = Album.objects.create(title='First Album', artist=artist)
        Song.objects.create(title='The First Song',
                            artist=artist,
                            album=album1,
                            bitrate=128000,
                            filetype='ogg',
                            first_save=True,
                            filefield=File(open(self.media_file.name)))

        album2 = Album.objects.create(title='Second Album', artist=artist)
        Song.objects.create(title='Second Song',
                            artist=artist,
                            album=album2,
                            bitrate=128000,
                            track='2',
                            filetype='ogg',
                            first_save=True,
                            filefield=File(open(self.media_file.name)))

    def test_rename_album_to_non_existent_album_renames_folder(self):
        album = Album.objects.get(title='First Album')
        original_filename = full_path(album.filepath)
        original_song_names = os.listdir(full_path(album.filepath))

        self.assertTrue(os.path.exists(original_filename))
        self.assertRaises(Album.DoesNotExist,
                          Album.objects.get,
                          title='Premier Album')

        album.title = 'Premier Album'
        album.save()

        # Check that Album.DoesNotExist is not thrown
        Album.objects.get(title='Premier Album')

        self.assertEquals(album.filepath,
                          os.path.join('T', 'The Artist', 'Premier Album'))

        new_filename = full_path(album.filepath)
        new_song_names = os.listdir(full_path(album.filepath))

        self.assertTrue(os.path.exists(new_filename))
        self.assertFalse(os.path.exists(original_filename))
        self.assertEquals(original_song_names, new_song_names)

        # check that song file was preserved during album renaming
        song = album.song_set.all()[0]
        self.assertEquals(open(self.media_file.name).read(),
                          song.filefield.read())
        self.assertNoLogError()

    def test_rename_album_to_existing_album_merges_folders(self):
        album1 = Album.objects.get(title='First Album')
        album2 = Album.objects.get(title='Second Album')
        original_filename = full_path(album1.filepath)

        self.assertEquals(len(album1.song_set.all()), 1)
        self.assertEquals(len(album2.song_set.all()), 1)

        album1.title = 'Second Album'
        album1.save()

        self.assertRaises(Album.DoesNotExist,
                          Album.objects.get,
                          title='First Album')
        self.assertFalse(os.path.exists(original_filename))

        songs = album2.song_set.all()
        self.assertEquals(len(songs), 2)
        self.assertEquals(
                sorted(os.listdir(full_path(album2.filepath))),
                sorted(['02 - Second Song.ogg', 'The First Song.ogg'])
        )

        self.assertNoLogError()

    def test_save_album_without_change_is_idempotent(self):
        album = Album.objects.get(title='First Album')
        self.assertEquals(album.title, 'First Album')
        self.assertEquals(album.artist.name, 'The Artist')
        self.assertEquals(album.filepath, 'T/The Artist/First Album')
        self.assertTrue(os.path.exists(full_path(album.filepath)))
        self.assertEquals(os.listdir(full_path(album.filepath)),
                          ['The First Song.ogg'])

        album.save()

        self.assertEquals(album.title, 'First Album')
        self.assertEquals(album.artist.name, 'The Artist')
        self.assertEquals(album.filepath, 'T/The Artist/First Album')
        self.assertTrue(os.path.exists(full_path(album.filepath)))
        self.assertEquals(os.listdir(full_path(album.filepath)),
                          ['The First Song.ogg'])
        self.assertNoLogError()

    def test_delete_album_removes_folder(self):
        album = Album.objects.get(title='First Album')
        filename = full_path(album.filepath)
        self.assertTrue(os.path.exists(filename))

        album.delete()

        self.assertFalse(os.path.exists(filename))
        self.assertNoLogError()

    def test_delete_last_album_of_artist_deletes_artist(self):
        album1 = Album.objects.get(title='First Album')
        album2 = Album.objects.get(title='Second Album')
        album1.delete()

        # Check that Artist.DoesNotExist is not thrown
        Artist.objects.get(name='The Artist')

        album2.delete()

        self.assertRaises(Artist.DoesNotExist,
                          Artist.objects.get,
                          name='The Artist')
        self.assertNoLogError()


@override_settings(MEDIA_ROOT=TEST_MEDIA_DIR)
class SongModelTest(ModelTest):

    def setUp(self):
        super(SongModelTest, self).setUp()

        artist = Artist.objects.create(name='The Artist')
        album = Album.objects.create(title='The Album', artist=artist)
        self.song = Song(title='The Song', artist=artist, album=album,
                    bitrate=128000, filetype='ogg', first_save=True,
                    filefield=File(open(self.media_file.name)))
        self.song.save()

    def test_save_new_song_creates_file_in_media_directory(self):
        filename = os.path.join(
            self.media_dir, 'T', 'The Artist', 'The Album', 'The Song.ogg'
        )

        self.assertEquals(os.listdir(self.media_dir), ['T'])
        self.assertTrue(os.path.exists(filename))
        self.assertEquals(open(self.media_file.name).read(),
                          open(filename).read())
        self.assertNoLogError()

    def test_rename_song_renames_filename(self):
        old_filename = full_path(self.song.filefield.name)
        self.assertTrue(os.path.exists(old_filename))

        self.song.title = 'La Chanson'
        self.song.save()

        new_filename = os.path.join(
            self.media_dir, 'T', 'The Artist', 'The Album', 'La Chanson.ogg'
        )

        self.assertEquals(full_path(self.song.filefield.name), new_filename)
        self.assertTrue(os.path.exists(new_filename))
        self.assertFalse(os.path.exists(old_filename))
        self.assertNoLogError()

    def test_change_song_album_moves_file_to_new_album_folder(self):
        old_filename = full_path(self.song.filefield.name)
        self.assertTrue(os.path.exists(old_filename))

        new_album = Album.objects.create(title='Live', artist=self.song.artist)
        self.song.album = new_album
        self.song.save()

        new_filename = os.path.join(
            self.media_dir, 'T', 'The Artist', 'Live', 'The Song.ogg'
        )

        self.assertEquals(full_path(self.song.filefield.name), new_filename)
        self.assertTrue(os.path.exists(new_filename))
        self.assertFalse(os.path.exists(old_filename))
        self.assertNoLogError()

    def test_change_song_artist_without_changing_album_raises_error(self):
        old_filename = full_path(self.song.filefield.name)
        self.assertTrue(os.path.exists(old_filename))

        new_artist = Artist.objects.create(name='Bob')
        self.song.artist = new_artist
        self.assertRaises(ValidationError, self.song.save, ())

    def test_change_song_artist_and_album_moves_file_to_new_folder(self):
        old_filename = full_path(self.song.filefield.name)
        self.assertTrue(os.path.exists(old_filename))

        new_artist = Artist.objects.create(name='Bob')
        new_album = Album.objects.create(title='The Album', artist=new_artist)
        self.song.artist = new_artist
        self.song.album = new_album
        self.song.save()

        new_filename = os.path.join(
            self.media_dir, 'B', 'Bob', 'The Album', 'The Song.ogg'
        )

        self.assertEquals(full_path(self.song.filefield.name), new_filename)
        self.assertTrue(os.path.exists(new_filename))
        self.assertFalse(os.path.exists(old_filename))
        self.assertNoLogError()

    def test_save_song_without_change_is_idempotent(self):
        self.assertEquals(self.song.title, 'The Song')
        self.assertEquals(self.song.album.title, 'The Album')
        self.assertEquals(self.song.artist.name, 'The Artist')
        self.assertEquals(self.song.filefield.name,
                          'T/The Artist/The Album/The Song.ogg')
        self.assertTrue(os.path.exists(full_path(self.song.filefield.name)))

        original_content = self.song.filefield.read()

        self.song.save()

        self.assertEquals(self.song.title, 'The Song')
        self.assertEquals(self.song.album.title, 'The Album')
        self.assertEquals(self.song.artist.name, 'The Artist')
        self.assertEquals(self.song.filefield.name,
                          'T/The Artist/The Album/The Song.ogg')
        self.assertTrue(os.path.exists(full_path(self.song.filefield.name)))

        self.song.filefield.seek(0)
        current_content = self.song.filefield.read()

        self.assertEquals(original_content, current_content)
        self.assertNoLogError()

    def test_delete_song_removes_file(self):
        filename = full_path(self.song.filefield.name)
        self.assertTrue(os.path.exists(filename))

        self.song.delete()

        self.assertFalse(os.path.exists(filename))
        self.assertNoLogError()

    def test_delete_last_song_of_album_deletes_album(self):
        # Check that Album.DoesNotExist is not thrown
        Album.objects.get(title='The Album')

        self.song.delete()

        self.assertRaises(Album.DoesNotExist,
                          Album.objects.get,
                          title='The Album')
        self.assertNoLogError()
