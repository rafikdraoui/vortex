from django.conf.urls import patterns, url

from haystack.views import SearchView

from .views import (
    ArtistListView, AlbumListView, SongListView,
    ArtistDetailView, AlbumDetailView, SongDetailView,
    download_artist, download_album, library_home, update_library
)


urlpatterns = patterns('',
    url(r'^$', library_home, name='library_home'),

    url(r'^artist/$', ArtistListView.as_view(), name='artist_list'),
    url(r'^artist/(?P<pk>\d+)/$', ArtistDetailView.as_view(), name='artist_detail'),
    url(r'^artist/(?P<pk>\d+)/download/$', download_artist, name='download_artist'),

    url(r'^album/$', AlbumListView.as_view(), name='album_list'),
    url(r'^album/(?P<pk>\d+)/$', AlbumDetailView.as_view(), name='album_detail'),
    url(r'^album/(?P<pk>\d+)/download/$', download_album, name='download_album'),

    url(r'^song/$', SongListView.as_view(), name='song_list'),
    url(r'^song/(?P<pk>\d+)/$', SongDetailView.as_view(), name='song_detail'),

    #FIXME: expose views.update_library to admin only
    url(r'^update/$', update_library, name='update_library'),

    url(r'^search/', SearchView(), name='search'),
)
