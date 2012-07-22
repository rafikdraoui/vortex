from django.contrib import admin

from vortex.musique.models import Artist, Album, Song


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


class AlbumAdmin(admin.ModelAdmin):
    readonly_fields = ['filepath']
    search_fields = ['title']
    list_display = ('title', 'artist')
    list_filter = ('artist',)
    inlines = [SongInline]


class SongAdmin(admin.ModelAdmin):
    readonly_fields = ['bitrate', 'filetype', 'filefield', 'original_path']
    search_fields = ['title']
    list_display = ('title', 'album', 'artist')


admin.site.register(Artist, ArtistAdmin)
admin.site.register(Album, AlbumAdmin)
admin.site.register(Song, SongAdmin)
