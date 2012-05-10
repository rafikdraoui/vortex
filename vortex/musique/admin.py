from django.contrib import admin
from vortex.musique.models import Artist, Album, Song


class MusiqueAdmin(admin.ModelAdmin):
    readonly_fields = ['filepath']
    change_form_template = 'admin/musique/change_form.html'

    def get_back_link(self, request):
        return request.path.replace('admin/musique/', '')

    def change_view(self, request, object_id, extra_context=None):
        extra_context = extra_context or {}
        extra_context['back_link'] = self.get_back_link(request)
        return super(MusiqueAdmin, self).change_view(
                            request, object_id, extra_context=extra_context)


#TODO

class ArtistAdmin(MusiqueAdmin):
    search_fields = ['name']


class AlbumAdmin(MusiqueAdmin):
    search_fields = ['title']


class SongAdmin(MusiqueAdmin):
    readonly_fields = ['bitrate', 'filetype', 'filefield', 'original_path']
    search_fields = ['title']


admin.site.register(Artist, ArtistAdmin)
admin.site.register(Album, AlbumAdmin)
admin.site.register(Song, SongAdmin)
