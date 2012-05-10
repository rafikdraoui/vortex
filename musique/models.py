import os
import shutil

from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import FileSystemStorage

from vortex.musique.utils import full_path


class Artist(models.Model):
    name = models.CharField(max_length=100, unique=True)
    filepath = models.FilePathField(path=settings.MEDIA_ROOT,
                                    recursive=True,
                                    max_length=200,
                                    unique=True)

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ['name']

    def save(self, *args, **kwargs):
        old_path = self.filepath
        new_path = os.path.join(self.name[0].upper(), self.name)
        query = Artist.objects.filter(name=self.name).exclude(id=self.id)[:1]
        if query:
            new_artist = query[0]
            for album in self.album_set.all():
                album.artist = new_artist
                album.save()
            self.delete()
        elif new_path != old_path:
            self.filepath = new_path
            super(Artist, self).save(*args, **kwargs)
            for album in self.album_set.all():
                album.save()
            try:
                os.removedirs(full_path(old_path))
            except OSError, msg:
                handle_delete_error(self, msg)
        else:
            super(Artist, self).save(*args, **kwargs)


class Album(models.Model):
    title = models.CharField(max_length=100)
    artist = models.ForeignKey(Artist)
    filepath = models.FilePathField(path=settings.MEDIA_ROOT,
                                    recursive=True,
                                    max_length=200,
                                    unique=True)

    class Meta:
        ordering = ['title']

    def __unicode__(self):
        return self.title

    #FIXME: Reduce number of SQL queries needed for saving
    def save(self, *args, **kwargs):
        old_path = self.filepath
        new_path = os.path.join(self.artist.filepath, self.title)
        query = Album.objects.filter(artist__id=self.artist_id,
                                     title=self.title
                            ).exclude(id=self.id)[:1]
        if query:
            new_album = query[0]
            for song in self.song_set.all():
                song.album = new_album
                song.save()
            self.delete()
        elif new_path != old_path:
            self.filepath = new_path
            super(Album, self).save(*args, **kwargs)
            for song in self.song_set.all():
                song.save()
            try:
                os.removedirs(full_path(old_path))
            except OSError, msg:
                handle_delete_error(self, msg)
        else:
            super(Album, self).save(*args, **kwargs)


class _CustomStorage(FileSystemStorage):

    def _save(self, name, content):
        if self.exists(name):
            self.delete(name)
        return super(_CustomStorage, self)._save(name, content)

    def get_available_name(self, name):
        return name


def _get_song_filepath(song_instance, filename=None):
    basename = u'%s.%s' % (song_instance.title, song_instance.filetype)
    if song_instance.track:
        basename = u'%s - %s' % (song_instance.track, basename)
    return os.path.join(song_instance.album.filepath, basename)


class Song(models.Model):
    title = models.CharField(max_length=100)
    artist = models.ForeignKey(Artist)
    album = models.ForeignKey(Album)
    track = models.CharField(max_length=10)
    bitrate = models.IntegerField()
    filetype = models.CharField(max_length=10)
    filefield = models.FileField(upload_to=_get_song_filepath,
                                 max_length=200,
                                 storage=_CustomStorage())
    original_path = models.CharField(max_length=200)
    first_save = models.BooleanField(editable=False)

    class Meta:
        ordering = ['track', 'title']
        unique_together = ('title', 'artist', 'album', 'track', 'bitrate')

    def __unicode__(self):
        return self.title

    def save(self, *args, **kwargs):
        file = self.filefield
        old_path = file.name
        new_path = _get_song_filepath(self)

        if old_path != new_path:
            content = ContentFile(file.read())
            file.save(new_path, content, save=False)
            if not self.first_save and old_path.lower() != new_path.lower():
                # .lower() hack is for case-insensitive systems
                try:
                    os.remove(full_path(old_path))
                except OSError, msg:
                    handle_delete_error(song, error)
        self.first_save = False

        super(Song, self).save(*args, **kwargs)


@receiver(post_delete, sender=Song, dispatch_uid='delete_song')
def remove_song(sender, **kwargs):
    try:
        song = kwargs['instance']
        song.filefield.delete(save=False)
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
        os.removedirs(full_path(album.filepath))
        if album.artist.album_set.count() == 0:
            album.artist.delete()
    except Artist.DoesNotExist:
        pass
    except Exception, msg:
        handle_delete_error(album, msg)


@receiver(post_delete, sender=Artist, dispatch_uid='delete_artist')
def remove_artist(sender, **kwargs):
    artist = kwargs['instance']

    if os.path.exists(full_path(artist.filepath)):
        os.removedirs(full_path(artist.filepath))


def handle_delete_error(instance, msg):
    import logging
    logger = logging.getLogger(__name__)
    if isinstance(instance, Artist):
        logger.info('Problem deleting %s: %s' % (instance.name, msg))
    else:
        logger.info('Problem deleting %s: %s' % (instance.title, msg))
