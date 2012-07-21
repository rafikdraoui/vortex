import re
import tempfile

from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views.generic import DetailView
from django.views import defaults
from django.views.decorators.csrf import requires_csrf_token

from vortex.musique.models import Artist, Album
from vortex.musique.utils import full_path, zip_folder
from vortex.musique import library


class ArtistDetailView(DetailView):
    model = Artist

    def get_context_data(self, **kwargs):
        context = super(ArtistDetailView, self).get_context_data(**kwargs)
        context['albums'] = context['object'].album_set.all()
        return context


class AlbumDetailView(DetailView):
    model = Album

    def get_context_data(self, **kwargs):
        context = super(AlbumDetailView, self).get_context_data(**kwargs)
        context['songs'] = context['object'].song_set.all()
        return context


def home(request):
    return render(request, 'musique/home.html')


def update_library(request):
    #TODO: run asynchronously (using celery?)
    library.update()
    return redirect('/')


def _download(instance):
    tfile = tempfile.NamedTemporaryFile(suffix='.zip')
    zip_folder(full_path(instance.filepath), tfile.name)

    #TODO: Use iterator in case data is too big for memory. This implies
    # that the temporary file needs to stay on disk during download, and
    # that it is deleted at some later time.
    tfile.seek(0)
    data = tfile.read()
    tfile.close()

    response = HttpResponse(data, content_type='application/zip')
    response['Content-Disposition'] = \
        u'attachment; filename=%s.zip' % unicode(instance)
    return response


def download_artist(request, pk):
    return _download(Artist.objects.get(pk=pk))


def download_album(request, pk):
    return _download(Album.objects.get(pk=pk))


@requires_csrf_token
def page_not_found(request, template_name='404.html'):
    #TODO??: use redirect(Model) with suitable Model.get_absolute_url()
    if re.match(r'/musique/artist/\d+/', request.path):
        return redirect('/musique/artist/')
    if re.match(r'/musique/album/\d+/', request.path):
        return redirect('/musique/album/')
    if re.match(r'/musique/song/\d+/', request.path):
        return redirect('/musique/song/')
    return defaults.page_not_found(request, template_name)
