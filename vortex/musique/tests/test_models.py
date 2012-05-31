import os
import shutil
import tempfile

from django.utils import unittest
from django.test import TestCase
from django.test.utils import override_settings
from django.core.files import File

from vortex.musique.models import Artist, Album, Song
from vortex.musique.utils import CustomStorage, full_path


TEST_MEDIA_FOLDER = tempfile.mkdtemp()


@override_settings(MEDIA_ROOT=TEST_MEDIA_FOLDER)
class ArtistModelTest(TestCase):

    def setUp(self):
        self.media_folder = TEST_MEDIA_FOLDER
        if not os.path.exists(TEST_MEDIA_FOLDER):
            os.mkdir(TEST_MEDIA_FOLDER)
        self.media_file = tempfile.NamedTemporaryFile(suffix='.ogg',
                                                      delete=False)
        self.media_file.write("""
        Lorem ipsum dolor sit amet, consectetur adipiscing elit. Quisque
        feugiat sem velit, sed rutrum urna. Etiam sed varius risus. Aenean
        consequat enim magna. Praesent sed metus tellus, eget sagittis sem.
        """)
        self.media_file.close()

        # Swap CustomStorage for filefield for testing so that it uses
        # the temporary media folder instead of settings.MEDIA_ROOT
        self._field = Song._meta.get_field_by_name('filefield')[0]
        self._default_storage = self._field.storage
        test_storage = CustomStorage(location=self.media_folder)
        self._field.storage = test_storage

        # Save songs in the database
        self._save_songs()

    def tearDown(self):
        os.remove(self.media_file.name)
        shutil.rmtree(self.media_folder)
        self._field = self._default_storage

    def _save_songs(self):
        artist1 = Artist.objects.create(name='First Artist',
                                        filepath='F/First Artist')
        album1 = Album.objects.create(title='First Album',
                                      artist=artist1,
                                      filepath='F/First Artist/First Album')
        Song.objects.create(title='The First Song',
                            artist=artist1,
                            album=album1,
                            bitrate=128000,
                            filetype='ogg',
                            first_save=True,
                            filefield=File(open(self.media_file.name)))

        artist2 = Artist.objects.create(name='Other Artist',
                                        filepath='O/Other Artist')
        album2 = Album.objects.create(title='Second Album',
                                      artist=artist2,
                                      filepath='O/Other Artist/Second Album')
        Song.objects.create(title='Second Song',
                            artist=artist2,
                            album=album2,
                            bitrate=128000,
                            track='02',
                            filetype='ogg',
                            first_save=True,
                            filefield=File(open(self.media_file.name)))

    def test_rename_artist_to_non_existent_artist_renames_folder(self):
        artist = Artist.objects.get(name='First Artist')
        original_filename = full_path(artist.filepath)

        self.assertTrue(os.path.exists(original_filename))
        self.assertRaises(Artist.DoesNotExist,
                          Artist.objects.get,
                          name='Premier Artiste')

        artist.name = 'Premier Artiste'
        artist.save()

        # Check that Artist.DoesNotExist is not thrown
        Artist.objects.get(name='Premier Artiste')

        self.assertEquals(artist.filepath,
                          os.path.join('P', 'Premier Artiste'))

        new_filename = full_path(artist.filepath)

        self.assertTrue(os.path.exists(new_filename))
        self.assertFalse(os.path.exists(original_filename))

        # TODO: check that album was preserved during artist renaming

    def test_rename_artist_to_existing_artist_merges_folders(self):
        artist1 = Artist.objects.get(name='First Artist')
        artist2 = Artist.objects.get(name='Other Artist')
        original_filename = full_path(artist1.filepath)

        self.assertEquals(len(artist1.album_set.all()), 1)
        self.assertEquals(len(artist2.album_set.all()), 1)

        artist1.name = 'Other Artist'
        artist1.save()

        self.assertRaises(Artist.DoesNotExist,
                          Artist.objects.get,
                          name='First Artist')
        self.assertFalse(os.path.exists(original_filename))

        # Check the Album.DoesNotExist is not thrown
        Album.objects.get(title='First Album')

        albums = artist2.album_set.all()
        self.assertEquals(len(albums), 2)
        self.assertEquals(os.listdir(full_path(artist2.filepath)),
                          ['First Album', 'Second Album'])
        #TODO: more tests

    def test_save_artist_without_change_is_idempotent(self):
        artist = Artist.objects.get(name='First Artist')
        self.assertEquals(artist.name, 'First Artist')
        self.assertEquals(artist.filepath, 'F/First Artist')
        self.assertTrue(os.path.exists(full_path(artist.filepath)))
        self.assertEquals(os.listdir(full_path(artist.filepath)),
                          ['First Album'])

        artist.save()

        self.assertEquals(artist.name, 'First Artist')
        self.assertEquals(artist.filepath, 'F/First Artist')
        self.assertTrue(os.path.exists(full_path(artist.filepath)))
        self.assertEquals(os.listdir(full_path(artist.filepath)),
                          ['First Album'])

    def test_delete_artist_removes_folder(self):
        artist = Artist.objects.get(name='First Artist')
        filename = full_path(artist.filepath)
        self.assertTrue(os.path.exists(filename))

        artist.delete()

        self.assertFalse(os.path.exists(filename))


@override_settings(MEDIA_ROOT=TEST_MEDIA_FOLDER)
class AlbumModelTest(TestCase):

    def setUp(self):
        self.media_folder = TEST_MEDIA_FOLDER
        if not os.path.exists(TEST_MEDIA_FOLDER):
            os.mkdir(TEST_MEDIA_FOLDER)
        self.media_file = tempfile.NamedTemporaryFile(suffix='.ogg',
                                                      delete=False)
        self.media_file.write("""
        Lorem ipsum dolor sit amet, consectetur adipiscing elit. Quisque
        feugiat sem velit, sed rutrum urna. Etiam sed varius risus. Aenean
        consequat enim magna. Praesent sed metus tellus, eget sagittis sem.
        """)
        self.media_file.close()

        # Swap CustomStorage for filefield for testing so that it uses
        # the temporary media folder instead of settings.MEDIA_ROOT
        self._field = Song._meta.get_field_by_name('filefield')[0]
        self._default_storage = self._field.storage
        test_storage = CustomStorage(location=self.media_folder)
        self._field.storage = test_storage

        # Save songs in the database
        self._save_songs()

    def tearDown(self):
        os.remove(self.media_file.name)
        shutil.rmtree(self.media_folder)
        self._field = self._default_storage

    def _save_songs(self):
        artist = Artist.objects.create(name='The Artist',
                                       filepath='T/The Artist')
        album1 = Album.objects.create(title='First Album',
                                      artist=artist,
                                      filepath='T/The Artist/First Album')
        Song.objects.create(title='The First Song',
                            artist=artist,
                            album=album1,
                            bitrate=128000,
                            filetype='ogg',
                            first_save=True,
                            filefield=File(open(self.media_file.name)))

        album2 = Album.objects.create(title='Second Album',
                                      artist=artist,
                                      filepath='T/The Artist/Second Album')
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
        self.assertEquals(os.listdir(full_path(album2.filepath)),
                          ['02 - Second Song.ogg', 'The First Song.ogg'])
        #TODO: more tests

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

    def test_delete_album_removes_folder(self):
        album = Album.objects.get(title='First Album')
        filename = full_path(album.filepath)
        self.assertTrue(os.path.exists(filename))

        album.delete()

        self.assertFalse(os.path.exists(filename))

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


@override_settings(MEDIA_ROOT=TEST_MEDIA_FOLDER)
class SongModelTest(TestCase):

    def setUp(self):
        self.media_folder = TEST_MEDIA_FOLDER
        if not os.path.exists(TEST_MEDIA_FOLDER):
            os.mkdir(TEST_MEDIA_FOLDER)
        self.media_file = tempfile.NamedTemporaryFile(suffix='.ogg',
                                                      delete=False)
        self.media_file.write("""
        Lorem ipsum dolor sit amet, consectetur adipiscing elit. Quisque
        feugiat sem velit, sed rutrum urna. Etiam sed varius risus. Aenean
        consequat enim magna. Praesent sed metus tellus, eget sagittis sem.
        """)
        self.media_file.close()

        # Swap CustomStorage for filefield for testing so that it uses
        # the temporary media folder instead of settings.MEDIA_ROOT
        self._field = Song._meta.get_field_by_name('filefield')[0]
        self._default_storage = self._field.storage
        test_storage = CustomStorage(location=self.media_folder)
        self._field.storage = test_storage

        # Save a song in the database
        self.song = self._save_song()

    def tearDown(self):
        os.remove(self.media_file.name)
        self._field = self._default_storage
        shutil.rmtree(self.media_folder)

    def _save_song(self):
        artist = Artist.objects.create(name='The Artist',
                                       filepath='T/The Artist')
        album = Album.objects.create(title='The Album',
                                     artist=artist,
                                     filepath='T/The Artist/The Album')
        song = Song(title='The Song', artist=artist, album=album,
                    bitrate=128000, filetype='ogg', first_save=True,
                    filefield=File(open(self.media_file.name)))
        song.save()

        return song

    def test_save_new_song_creates_file_in_media_folder(self):
        filename = os.path.join(
            self.media_folder, 'T', 'The Artist', 'The Album', 'The Song.ogg'
        )

        self.assertEquals(os.listdir(self.media_folder), ['T'])
        self.assertTrue(os.path.exists(filename))
        self.assertEquals(open(self.media_file.name).read(),
                          open(filename).read())

    def test_rename_song_renames_filename(self):
        old_filename = full_path(self.song.filefield.name)
        self.assertTrue(os.path.exists(old_filename))

        self.song.title = 'La Chanson'
        self.song.save()

        new_filename = os.path.join(
            self.media_folder, 'T', 'The Artist', 'The Album', 'La Chanson.ogg'
        )

        self.assertEquals(
            full_path(self.song.filefield.name),
            new_filename
        )
        self.assertTrue(os.path.exists(new_filename))
        self.assertFalse(os.path.exists(old_filename))

    def test_change_song_album_moves_file_to_new_album_folder(self):
        pass

    def test_change_song_artist_moves_file_to_new_artist_folder(self):
        pass

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

    def test_delete_song_removes_file(self):
        filename = full_path(self.song.filefield.name)
        self.assertTrue(os.path.exists(filename))

        self.song.delete()

        self.assertFalse(os.path.exists(filename))

    def test_delete_last_song_of_album_deletes_album(self):
        # Check that Album.DoesNotExist is not thrown
        Album.objects.get(title='The Album')

        self.song.delete()

        self.assertRaises(Album.DoesNotExist,
                          Album.objects.get,
                          title='The Album')
