from django.conf.urls import patterns, include, url
from django.views.generic import ListView, DetailView

from vortex.musique.models import Artist, Album, Song
from vortex.musique.views import (ArtistDetailView,
                                  AlbumDetailView,
                                  update_library)


urlpatterns = patterns('',
    url(r'^artist/$', ListView.as_view(model=Artist)),
    url(r'^artist/(?P<pk>\d+)/$', ArtistDetailView.as_view()),

    url(r'^album/$', ListView.as_view(model=Album)),
    url(r'^album/(?P<pk>\d+)/$', AlbumDetailView.as_view()),

    url(r'^song/$', ListView.as_view(model=Song)),
    url(r'^song/(?P<pk>\d+)/$', DetailView.as_view(model=Song)),

    #FIXME: expose views.update_library to admin only
    url(r'^update/$', update_library),
)
