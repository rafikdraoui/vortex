from django.conf.urls import patterns, url
from django.views.generic import ListView, DetailView

from haystack.views import SearchView

from vortex.musique.models import Artist, Album, Song
from vortex.musique.views import (ArtistDetailView,
                                  AlbumDetailView,
                                  download_artist,
                                  download_album,
                                  update_library)


urlpatterns = patterns('',
    url(r'^artist/$', ListView.as_view(model=Artist), name='artist_list'),
    url(r'^artist/(?P<pk>\d+)/$', ArtistDetailView.as_view(), name='artist_detail'),
    url(r'^artist/(?P<pk>\d+)/download/$', download_artist, name='download_artist'),

    url(r'^album/$', ListView.as_view(model=Album), name='album_list'),
    url(r'^album/(?P<pk>\d+)/$', AlbumDetailView.as_view(), name='album_detail'),
    url(r'^album/(?P<pk>\d+)/download/$', download_album, name='download_album'),

    url(r'^song/$', ListView.as_view(model=Song), name='song_list'),
    url(r'^song/(?P<pk>\d+)/$', DetailView.as_view(model=Song), name='song_detail'),

    #FIXME: expose views.update_library to admin only
    url(r'^update/$', update_library, name='update_library'),

    url(r'^search/', SearchView(), name='search'),
)
