from haystack import site
from haystack.indexes import SearchIndex, CharField

from vortex.library.models import Artist, Album, Song


class ArtistIndex(SearchIndex):
    text = CharField(document=True, use_template=True)


class AlbumIndex(SearchIndex):
    text = CharField(document=True, use_template=True)
    artist = CharField(model_attr='artist')


class SongIndex(SearchIndex):
    text = CharField(document=True, use_template=True)
    artist = CharField(model_attr='album__artist')
    album = CharField(model_attr='album')


site.register(Artist, ArtistIndex)
site.register(Album, AlbumIndex)
site.register(Song, SongIndex)
