import re

from django.shortcuts import render, redirect
from django.views.generic import DetailView
from django.views import defaults
from django.views.decorators.csrf import requires_csrf_token

from vortex.musique.models import Artist, Album
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


@requires_csrf_token
def page_not_found(request, template_name='404.html'):

    if re.match(r'/musique/artist/\d+/', request.path):
        return redirect('/musique/artist/')
    if re.match(r'/musique/album/\d+/', request.path):
        return redirect('/musique/album/')
    if re.match(r'/musique/song/\d+/', request.path):
        return redirect('/musique/song/')
    return defaults.page_not_found(request, template_name)
