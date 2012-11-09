import logging
import os

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.db import models, IntegrityError
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _

from vortex.musique.utils import full_path, CustomStorage


class Artist(models.Model):
    name = models.CharField(_('name'), max_length=100, unique=True)
    filepath = models.FilePathField(_('file path'),
                                    path=settings.MEDIA_ROOT,
                                    recursive=True,
                                    max_length=200,
                                    unique=True)

    class Meta:
        ordering = ['name']
        verbose_name = _('artist')
        verbose_name_plural = _('artists')

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ('artist_detail', (), {'pk': str(self.id)})

    def save(self, *args, **kwargs):
        """Overridden to ensure renaming of artist directory
        whenever the artist is renamed.
        """

        old_path = self.filepath
        new_path = os.path.join(self.name[0].upper(), self.name)
        query = Artist.objects.filter(name=self.name).exclude(id=self.id)[:1]
        if query:
            # Artist with that name already exists. Merge the albums.
            new_artist = query[0]
            for album in self.album_set.all():
                for song in album.song_set.all():
                    song.artist = new_artist
                    song.save(clean=False)
                album.artist = new_artist
                album.save()
            self.delete()
        else:
            self.filepath = new_path
            super(Artist, self).save(*args, **kwargs)
            if old_path and new_path != old_path:
                for album in self.album_set.all():
                    album.save()
                try:
                    os.rmdir(full_path(old_path))
                except OSError, msg:
                    handle_delete_error(self, msg)


class Album(models.Model):
    title = models.CharField(_('title'), max_length=100)
    artist = models.ForeignKey(Artist, verbose_name=_('artist'))
    filepath = models.FilePathField(_('file path'),
                                    path=settings.MEDIA_ROOT,
                                    recursive=True,
                                    max_length=200,
                                    unique=True)

    class Meta:
        ordering = ['title']
        verbose_name = _('album')
        verbose_name_plural = _('albums')

    def __unicode__(self):
        return self.title

    @models.permalink
    def get_absolute_url(self):
        return ('album_detail', (), {'pk': str(self.id)})

    #FIXME: Reduce number of SQL queries needed for saving
    def save(self, *args, **kwargs):
        """Overridden to ensure renaming of album directory
        whenever the album is renamed.
        """

        old_path = self.filepath
        new_path = os.path.join(self.artist.filepath, self.title)
        query = Album.objects.filter(artist__id=self.artist_id,
                                     title=self.title
                            ).exclude(id=self.id)[:1]
        if query:
            # Album with that name already exists. Merge the songs.
            new_album = query[0]
            for song in self.song_set.all():
                song.album = new_album
                try:
                    song.save()
                except IntegrityError:
                    # Song already exists under the other album
                    pass
            self.delete()
        else:
            self.filepath = new_path
            super(Album, self).save(*args, **kwargs)
            if old_path and new_path != old_path:
                for song in self.song_set.all():
                    song.save()
                try:
                    os.rmdir(full_path(old_path))
                except OSError, msg:
                    handle_delete_error(self, msg)


def _get_song_filepath(song_instance, filename=None):
    """Returns an appropriate file system path for the song."""

    basename = u'%s.%s' % (song_instance.title, song_instance.filetype)
    if song_instance.track:
        basename = u'%s - %s' % (song_instance.track, basename)
    return os.path.join(song_instance.album.filepath, basename)


class Song(models.Model):
    title = models.CharField(_('title'), max_length=100)
    artist = models.ForeignKey(Artist, verbose_name=_('artist'))
    album = models.ForeignKey(Album, verbose_name=_('album'))
    track = models.CharField(_('track'), max_length=10, default='')
    bitrate = models.IntegerField(_('bitrate'))
    filetype = models.CharField(_('file type'), max_length=10)
    filefield = models.FileField(_('file'),
                                 upload_to=_get_song_filepath,
                                 max_length=200,
                                 storage=CustomStorage())
    original_path = models.CharField(_('original path'),
                                     max_length=200,
                                     default='')
    first_save = models.BooleanField(editable=False)

    class Meta:
        ordering = ['track', 'title']
        unique_together = ('title', 'artist', 'album', 'track')
        verbose_name = _('song')
        verbose_name_plural = _('songs')

    def __unicode__(self):
        return self.title

    @models.permalink
    def get_absolute_url(self):
        return ('song_detail', (), {'pk': str(self.id)})

    def clean(self):
        """Validates that the album belongs to the artist."""

        if self.album not in self.artist.album_set.all():
            raise ValidationError(_(
                    'Album "%(album)s" does not belong '
                    'to artist "%(artist)s".')
                    % {'album': self.album, 'artist': self.artist})

    def save(self, *args, **kwargs):
        """Overridden to ensure renaming of the song file whenever
        the song is renamed.
        """

        if kwargs.get('clean', True):
            self.clean()
        kwargs.pop('clean', None)

        if len(self.track) == 1:
            self.track = '0' + self.track
        thefile = self.filefield
        old_path = thefile.name
        new_path = _get_song_filepath(self)

        if old_path != new_path:
            content = ContentFile(thefile.read())
            thefile.save(new_path, content, save=False)
            if not self.first_save and old_path.lower() != new_path.lower():
                # .lower() hack is for case-insensitive systems
                try:
                    os.remove(full_path(old_path))
                except OSError, msg:
                    handle_delete_error(self, msg)
        self.first_save = False

        super(Song, self).save(*args, **kwargs)


"""The following post_delete hooks ensure that the underlying
files and directories corresponding to the songs, albums and
artists are removed from the file system when they are deleted
from the library."""


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
        os.rmdir(full_path(album.filepath))
        if album.artist.album_set.count() == 0:
            album.artist.delete()
    except Artist.DoesNotExist:
        pass
    except Exception, msg:
        handle_delete_error(album, msg)


@receiver(post_delete, sender=Artist, dispatch_uid='delete_artist')
def remove_artist(sender, **kwargs):
    artist = kwargs['instance']
    try:
        if os.path.exists(full_path(artist.filepath)):
            os.rmdir(full_path(artist.filepath))
    except Exception, msg:
        handle_delete_error(artist, msg)


LOGGER = logging.getLogger(__name__)


def handle_delete_error(instance, msg):
    """Write an error message in the log."""

    if isinstance(instance, Artist):
        LOGGER.info('Problem deleting %s: %s' % (instance.name, msg))
    else:
        LOGGER.info('Problem deleting %s: %s' % (instance.title, msg))
