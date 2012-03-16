import os

from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver

from vortex.settings import MEDIA_ROOT


class Artist(models.Model):
    name = models.CharField(max_length=100, unique=True)
    filepath = models.FilePathField(path=MEDIA_ROOT,
                                    recursive=True,
                                    max_length=200,
                                    unique=True,
                                    editable=False)

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ['name']


class Album(models.Model):
    title = models.CharField(max_length=100)
    artist = models.ForeignKey(Artist)
    filepath = models.FilePathField(path=MEDIA_ROOT,
                                    recursive=True,
                                    max_length=200,
                                    unique=True,
                                    editable=False)

    def __unicode__(self):
        return self.title

    class Meta:
        ordering = ['title']


class Song(models.Model):
    title = models.CharField(max_length=100)
    artist = models.ForeignKey(Artist)
    album = models.ForeignKey(Album)
    track = models.CharField(max_length=10)
    bitrate = models.IntegerField()
    filepath = models.FilePathField(path=MEDIA_ROOT,
                                    recursive=True,
                                    max_length=200,
                                    unique=True,
                                    editable=False)

    class Meta:
        ordering = ['track', 'title']
        unique_together = ('title', 'artist', 'album', 'bitrate')

    def __unicode__(self):
        return self.title


@receiver(post_delete, sender=Song, dispatch_uid='delete_song')
def remove_song(sender, **kwargs):
    try:
        song = kwargs['instance']
        os.remove(song.filepath)
        if song.album.song_set.count() == 0:
            song.album.delete()
    except Album.DoesNotExist:
        pass
    except Exception:
        handle_delete_error(song)


@receiver(post_delete, sender=Album, dispatch_uid='delete_album')
def remove_album(sender, **kwargs):
    try:
        album = kwargs['instance']
        os.removedirs(album.filepath)
        if album.artist.album_set.count() == 0:
            album.artist.delete()
    except Artist.DoesNotExist:
        pass
    except Exception:
        handle_delete_error(album)


@receiver(post_delete, sender=Artist, dispatch_uid='delete_artist')
def remove_artist(sender, **kwargs):
    artist = kwargs['instance']

    if os.path.exists(artist.filepath):
        os.removedirs(artist.filepath)


def handle_delete_error(instance):
    import logging
    logger = logging.getLogger(__name__)
    logger.info("Problem deleting %s (%s)" % (instance.title,
                                              instance.filepath))
