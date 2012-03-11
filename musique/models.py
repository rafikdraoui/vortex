from django.db import models
from django.contrib.auth.models import User

from vortex.settings import MEDIA_ROOT


class Artist(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ['name']


class Album(models.Model):
    title = models.CharField(max_length=100)
    artist = models.ForeignKey(Artist)

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
                                    max_length=500,
                                    unique=True,
                                    editable=False)

    class Meta:
        ordering = ['track', 'title']
        unique_together = ('title', 'artist', 'album', 'bitrate')

    def __unicode__(self):
        return self.title
