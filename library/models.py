import os

from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.db import models, IntegrityError
from django.utils.translation import ugettext_lazy as _


class CustomStorage(FileSystemStorage):
    """Custom FileSystemStorage class that overwrites existing files."""

    def _save(self, name, content):
        if self.exists(name):
            self.delete(name)
        return super(CustomStorage, self)._save(name, content)

    def get_available_name(self, name):
        return name


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

    # Overriden to take care of merging two artists.
    def save(self, *args, **kwargs):
        query = Artist.objects.filter(name=self.name).exclude(id=self.id)[:1]
        if query:
            # Artist with that name already exists. Merge the albums.

            new_artist = query[0]

            for album in self.albums.all():
                # Used instead of bulk updating in order to update filepaths
                # and resolve eventual merges of albums.
                album.artist = new_artist
                album.save()

            if self.pk:
                self.delete()

        else:
            self.filepath = os.path.join(self.name[0].upper(), self.name)
            super(Artist, self).save(*args, **kwargs)

            # This is needed to update album filepaths. We could avoid this
            # loop by making `filepath` an attribute of the Album model that is
            # computed from the artist and the title whenever it is needed, but
            # this would imply that each time this attribute would be accessed
            # the artist instance needs to be available, which might entail
            # extra database queries.
            # TODO: profile to see which alternative is best.
            for album in self.albums.all():
                album.save(skip_merge_check=True)


class Album(models.Model):
    title = models.CharField(_('title'), max_length=100)
    artist = models.ForeignKey(
        Artist, verbose_name=_('artist'), related_name='albums')
    filepath = models.FilePathField(_('file path'),
                                    path=settings.MEDIA_ROOT,
                                    recursive=True,
                                    max_length=200,
                                    unique=True)
    cover = models.ImageField(_('cover art'),
                              upload_to=(lambda a, f: a.cover_filepath),
                              max_length=200,
                              storage=CustomStorage())

    #TODO: validate on file upload, change to a choices field
    cover_file_type = models.CharField(_('cover file type'),
                                       max_length=5,
                                       editable=False)

    class Meta:
        ordering = ['title']
        verbose_name = _('album')
        verbose_name_plural = _('albums')

    def __unicode__(self):
        return self.title

    @models.permalink
    def get_absolute_url(self):
        return ('album_detail', (), {'pk': str(self.id)})

    @property
    def cover_filepath(self, filename=''):
        """Return an appropriate file system path for the album cover."""
        return os.path.join(self.filepath, 'cover.%s' % self.cover_file_type)

    # Overriden to take care of merging two albums.
    def save(self, *args, **kwargs):
        skip_merge_check = kwargs.pop('skip_merge_check', False)

        if not skip_merge_check:
            query = Album.objects.filter(artist_id=self.artist_id,
                                         title=self.title
                                ).exclude(id=self.id)[:1]
            if query:
                # Album with that name already exists. Merge the songs.

                new_album = query[0]

                try:
                    self.songs.update(album=new_album)
                except IntegrityError:
                    # At least one of the song already exists under the other
                    # album. We want to ignore these, and so we must save each
                    # song one by one in order to catch the IntegrityError.
                    for song in self.songs.all():
                        song.album = new_album
                        try:
                            song.save()
                        except IntegrityError:
                            pass

                if self.pk:
                    self.delete()

                return

        self.filepath = os.path.join(self.artist.filepath, self.title)
        super(Album, self).save(*args, **kwargs)


class Song(models.Model):
    title = models.CharField(_('title'), max_length=100)
    album = models.ForeignKey(Album, verbose_name=_('album'), related_name='songs')
    track = models.CharField(_('track'), max_length=10, default='', blank=True)
    bitrate = models.IntegerField(_('bitrate'))
    filetype = models.CharField(_('file type'), max_length=10)
    filefield = models.FileField(_('file'),
                                 upload_to=(lambda s, f: s.filepath),
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

    def __unicode__(self):
        return self.title

    @models.permalink
    def get_absolute_url(self):
        return ('song_detail', (), {'pk': str(self.id)})

    @property
    def filepath(self):
        basename = u'%s.%s' % (self.title, self.filetype)
        if self.track:
            basename = u'%s - %s' % (self.track, basename)
        return os.path.join(self.album.filepath, basename)

    def save(self, *args, **kwargs):
        if len(self.track) == 1:
            self.track = '0' + self.track
        super(Song, self).save(*args, **kwargs)
