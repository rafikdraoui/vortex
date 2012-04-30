import os

from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver

import vortex


config = vortex.get_config()
MEDIA_ROOT = unicode(config.get('vortex', 'media_root'))


class Artist(models.Model):
    name = models.CharField(max_length=100, unique=True)
    filepath = models.FilePathField(path=MEDIA_ROOT,
                                    recursive=True,
                                    max_length=200,
                                    unique=True)

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
                                    unique=True)

    class Meta:
        ordering = ['title']

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
    filetype = models.CharField(max_length=10)
    filepath = models.FilePathField(path=MEDIA_ROOT,
                                    recursive=True,
                                    max_length=200,
                                    unique=True)
    original_path = models.CharField(max_length=200)

    class Meta:
        ordering = ['track', 'title']
        unique_together = ('title', 'artist', 'album', 'track', 'bitrate')

    def __unicode__(self):
        return self.title


@receiver(post_delete, sender=Song, dispatch_uid='delete_song')
def remove_song(sender, **kwargs):
    try:
        song = kwargs['instance']
        os.remove(os.path.join(MEDIA_ROOT, song.filepath))
        if song.album.song_set.count() == 0:
            song.album.delete()
    except Album.DoesNotExist:
        pass
    except Exception, msg:
        handle_delete_error(song, msg)


@receiver(post_delete, sender=Album, dispatch_uid='delete_album')
def remove_album(sender, **kwargs):
    try:
        album = kwargs['instance']
        os.removedirs(os.path.join(MEDIA_ROOT, album.filepath))
        if album.artist.album_set.count() == 0:
            album.artist.delete()
    except Artist.DoesNotExist:
        pass
    except Exception, msg:
        handle_delete_error(album, msg)


@receiver(post_delete, sender=Artist, dispatch_uid='delete_artist')
def remove_artist(sender, **kwargs):
    artist = kwargs['instance']

    if os.path.exists(os.path.join(MEDIA_ROOT, artist.filepath)):
        os.removedirs(os.path.join(MEDIA_ROOT, artist.filepath))


def handle_delete_error(instance, msg):
    import logging
    logger = logging.getLogger(__name__)
    logger.info("Problem deleting %s (%s): %s" % (instance.title,
                                                  instance.filepath,
                                                  msg))
