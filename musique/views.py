from django.shortcuts import render_to_response
from django.views.generic import DetailView

from models import Artist, Album, Song


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
    return render_to_response('musique/home.html')
