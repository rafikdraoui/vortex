from django.contrib import admin
from django.forms import ModelForm
from django.utils.translation import ugettext_lazy as _

from .models import Artist, Album, Song


class ArtistModelForm(ModelForm):

    # Do not validate in form. This is needed for renaming an artist to
    # an existing artist (and thus merge the albums, see models.Artist.save)
    def validate_unique(self):
        pass


class SongInline(admin.StackedInline):
    model = Song
    fields = [('track', 'title')]
    has_add_permission = lambda x, y: False


class AlbumInline(admin.StackedInline):
    model = Album
    fields = ('title',)
    has_add_permission = lambda x, y: False


class ArtistAdmin(admin.ModelAdmin):
    readonly_fields = ['filepath']
    search_fields = ['name']
    inlines = [AlbumInline]
    form = ArtistModelForm


class AlbumAdmin(admin.ModelAdmin):
    readonly_fields = ['filepath']
    search_fields = ['title']
    list_display = ('title', 'artist')
    list_filter = ('artist',)
    inlines = [SongInline]


class SongAdmin(admin.ModelAdmin):

    def get_song_artist(self, song):
        return '%s' % song.album.artist
    get_song_artist.short_description = _('Artist')

    readonly_fields = (
        'bitrate', 'filetype', 'filefield', 'original_path',
        'date_added', 'date_modified'
    )
    search_fields = ['title']
    list_display = ('title', 'album', 'get_song_artist')
    has_add_permission = lambda x, y: False


admin.site.register(Artist, ArtistAdmin)
admin.site.register(Album, AlbumAdmin)
admin.site.register(Song, SongAdmin)
