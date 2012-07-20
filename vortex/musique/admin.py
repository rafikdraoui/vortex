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


class MusiqueAdmin(admin.ModelAdmin):
    change_form_template = 'admin/musique/change_form.html'

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['back_link'] = request.path.replace('admin/', '')
        return super(MusiqueAdmin, self).change_view(
                                                request,
                                                object_id,
                                                form_url,
                                                extra_context=extra_context)


class ArtistAdmin(MusiqueAdmin):
    readonly_fields = ['filepath']
    search_fields = ['name']
    inlines = [AlbumInline]


class AlbumAdmin(MusiqueAdmin):
    readonly_fields = ['filepath']
    search_fields = ['title']
    list_display = ('title', 'artist')
    list_filter = ('artist',)
    inlines = [SongInline]


class SongAdmin(MusiqueAdmin):
    readonly_fields = ['bitrate', 'filetype', 'filefield', 'original_path']
    search_fields = ['title']
    list_display = ('title', 'album', 'artist')


admin.site.register(Artist, ArtistAdmin)
admin.site.register(Album, AlbumAdmin)
admin.site.register(Song, SongAdmin)
