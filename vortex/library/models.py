import logging
import os

from django.conf import settings
from django.core.files.base import ContentFile
from django.db import models, IntegrityError
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _

from vortex.library.utils import (full_path,
                                  remove_empty_directories,
                                  CustomStorage)


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

    # Overridden to ensure changes in the model are reflected in the media
    # directory on the file system.
    def save(self, *args, **kwargs):
        old_path = self.filepath
        query = Artist.objects.filter(name=self.name).exclude(id=self.id)[:1]
        if query:
            # Artist with that name already exists. Merge the albums.

            new_artist = query[0]

            for album in self.album_set.all():
                album.artist = new_artist
                album.save(rename_files=False, remove_empties=False)

            cleanup_filenames(
                Song.objects.filter(album__artist=self).select_related())
            remove_empty_directories(full_path(old_path))

            if self.pk:
                self.delete()

        else:
            self.filepath = os.path.join(self.name[0].upper(), self.name)
            super(Artist, self).save(*args, **kwargs)
            if old_path and self.filepath != old_path:
                for album in self.album_set.all():
                    # This is needed to move the files to the new folder
                    album.save(remove_empties=False)
                remove_empty_directories(full_path(old_path))


class Album(models.Model):
    title = models.CharField(_('title'), max_length=100)
    artist = models.ForeignKey(Artist, verbose_name=_('artist'))
    filepath = models.FilePathField(_('file path'),
                                    path=settings.MEDIA_ROOT,
                                    recursive=True,
                                    max_length=200,
                                    unique=True)
    cover = models.ImageField(
        _('cover art'),
        upload_to=(lambda a, f: Album.get_cover_filepath(a, f)),
        max_length=200,
        storage=CustomStorage())

    class Meta:
        ordering = ['title']
        verbose_name = _('album')
        verbose_name_plural = _('albums')

    @classmethod
    def get_cover_filepath(cls, album, filename=''):
        """Return an appropriate file system path for the album cover."""

        extension = os.path.splitext(filename)[1].lower() or '.jpg'
        return os.path.join(album.filepath, 'cover%s' % extension)

    def __unicode__(self):
        return self.title

    @models.permalink
    def get_absolute_url(self):
        return ('album_detail', (), {'pk': str(self.id)})

    # Overridden to ensure changes in the model are reflected in the media
    # directory on the file system.
    def save(self, *args, **kwargs):
        """Takes two custom keyword arguments:

            rename_files: boolean indicating if cleanup_filenames must be
                          called after saving (default: True).
            remove_empties: boolean indicating if remove_empty_directories must
                            be called after saving (default: True).
        """

        query = Album.objects.filter(artist_id=self.artist_id,
                                     title=self.title
                            ).exclude(id=self.id)[:1]
        if query:
            # Album with that name already exists. Merge the songs.

            new_album = query[0]

            try:
                self.song_set.update(album=new_album)
            except IntegrityError:
                # At least one of the song already exists under the other
                # album. We want to ignore these, and so we must save each
                # song one by one in order to catch the IntegrityError.
                for song in self.song_set.all():
                    song.album = new_album
                    try:
                        song.save(rename_file=False)
                    except IntegrityError:
                        pass

            cleanup_filenames(new_album.song_set.select_related())

            if self.pk:
                self.delete()
        else:
            old_path = self.filepath
            self.filepath = os.path.join(self.artist.filepath, self.title)
            rename_files = kwargs.pop('rename_files', True)
            remove_empties = kwargs.pop('remove_empties', True)
            if old_path and self.filepath != old_path:

                # move cover image to new directory
                content = ContentFile(self.cover.read())
                new_cover_path = Album.get_cover_filepath(
                    self, self.cover.name)
                self.cover.delete(save=False)
                self.cover.save(new_cover_path, content, save=False)

                super(Album, self).save(*args, **kwargs)

                if rename_files:
                    cleanup_filenames(self.song_set.select_related())
                if remove_empties:
                    # Start from the parent (i.e. artist) directory in case
                    # the previous artist only had this album.
                    remove_empty_directories(
                        os.path.dirname(full_path(old_path)))

                    old_artist_name = old_path.split('/')[1]
                    old_artist = Artist.objects.get(name=old_artist_name)
                    if old_artist.album_set.count() == 0:
                        old_artist.delete()
            else:
                super(Album, self).save(*args, **kwargs)


class Song(models.Model):
    title = models.CharField(_('title'), max_length=100)
    album = models.ForeignKey(Album, verbose_name=_('album'))
    track = models.CharField(_('track'), max_length=10, default='', blank=True)
    bitrate = models.IntegerField(_('bitrate'))
    filetype = models.CharField(_('file type'), max_length=10)
    filefield = models.FileField(_('file'),
                                 upload_to=(lambda s, f: Song.get_filepath(s)),
                                 max_length=200,
                                 storage=CustomStorage())
    original_path = models.CharField(_('original path'),
                                     max_length=200,
                                     default='')
    date_added = models.DateTimeField(_('date added'), auto_now_add=True)
    date_modified = models.DateTimeField(_('date last modified'),
                                         auto_now=True)
    first_save = models.BooleanField(editable=False)

    class Meta:
        ordering = ['track', 'title']
        unique_together = ('title', 'album', 'track')
        verbose_name = _('song')
        verbose_name_plural = _('songs')

    @classmethod
    def get_filepath(cls, song):
        """Return an appropriate file system path for the song."""

        basename = u'%s.%s' % (song.title, song.filetype)
        if song.track:
            basename = u'%s - %s' % (song.track, basename)
        return os.path.join(song.album.filepath, basename)

    def __unicode__(self):
        return self.title

    @models.permalink
    def get_absolute_url(self):
        return ('song_detail', (), {'pk': str(self.id)})

    # Overridden to ensure changes in the model are reflected in the media
    # directory on the file system.
    def save(self, *args, **kwargs):
        """Takes a custom keyword argument `rename_file`, a boolean indicating
        if the underlying file corresponding to this song instance must be
        renamed after saving (default: True).
        """

        rename = kwargs.pop('rename_file', True)

        if len(self.track) == 1:
            self.track = '0' + self.track

        super(Song, self).save(*args, **kwargs)

        if rename:
            cleanup_filenames([self])


def cleanup_filenames(candidates=None):
    """Ensure that each song instance in the candidates has its file field at
    the right place in the media directory on the file system.
    """
    songs = candidates or Song.objects.select_related().iterator()
    for song in songs:
        filepath = Song.get_filepath(song)
        thefile = song.filefield
        current_path = thefile.name
        if filepath != current_path:
            content = ContentFile(thefile.read())
            thefile.delete(save=False)
            thefile.save(filepath, content, save=False)
            song.save(rename_file=False)


# The following post_delete hooks ensure that the underlying files and
# directories corresponding to the songs, albums and artists are removed from
# the file system when they are deleted from the library.

LOGGER = logging.getLogger(__name__)


@receiver(post_delete, sender=Song, dispatch_uid='delete_song')
def remove_song(sender, **kwargs):
    try:
        song = kwargs['instance']
        song.filefield.delete(save=False)
        if song.album.song_set.count() == 0:
            song.album.delete()
    except Album.DoesNotExist:
        pass


@receiver(post_delete, sender=Album, dispatch_uid='delete_album')
def remove_album(sender, **kwargs):
    try:
        album = kwargs['instance']
        os.remove(full_path(album.cover.name))
        os.rmdir(full_path(album.filepath))
        if album.artist.album_set.count() == 0:
            album.artist.delete()
    except Artist.DoesNotExist:
        pass
    except OSError as e:
        LOGGER.info('Problem deleting %s: %s' % (album.title, e))


@receiver(post_delete, sender=Artist, dispatch_uid='delete_artist')
def remove_artist(sender, **kwargs):
    artist = kwargs['instance']
    try:
        if os.path.exists(full_path(artist.filepath)):
            os.rmdir(full_path(artist.filepath))
    except OSError as e:
        LOGGER.info('Problem deleting %s: %s' % (artist.name, e))
