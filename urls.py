from django.conf.urls.defaults import patterns, include, url
from django.views.generic import ListView, DetailView

from musique.models import Artist, Album, Song
from musique.views import ArtistDetailView, AlbumDetailView

from musique import utils, views

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', views.home),

    url(r'^admin/', include(admin.site.urls)),
    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    url(r'^artist/$', ListView.as_view(model=Artist)),
    url(r'^artist/(?P<pk>\d+)/$', ArtistDetailView.as_view()),

    url(r'^album/$', ListView.as_view(model=Album)),
    url(r'^album/(?P<pk>\d+)/$', AlbumDetailView.as_view()),

    url(r'^song/$', ListView.as_view(model=Song)),
    url(r'^song/(?P<pk>\d+)$', DetailView.as_view(model=Song)),
)
