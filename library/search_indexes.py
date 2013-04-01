from haystack.indexes import CharField, Indexable, SearchIndex

from .models import Artist, Album, Song


class ArtistIndex(SearchIndex, Indexable):
    text = CharField(document=True, use_template=True)

    def get_model(self):
        return Artist


class AlbumIndex(SearchIndex, Indexable):
    text = CharField(document=True, use_template=True)
    artist = CharField(model_attr='artist')

    def get_model(self):
        return Album


class SongIndex(SearchIndex, Indexable):
    text = CharField(document=True, use_template=True)
    artist = CharField(model_attr='album__artist')
    album = CharField(model_attr='album')

    def get_model(self):
        return Song
