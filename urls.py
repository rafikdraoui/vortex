from django.conf import settings
from django.conf.urls.defaults import patterns, include, url
from django.views.generic import ListView, DetailView
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from vortex.musique.models import Artist, Album, Song
from vortex.musique import views

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', views.home),

    url(r'^admin/', include(admin.site.urls)),

    url(r'^artist/$', ListView.as_view(model=Artist)),
    url(r'^artist/(?P<pk>\d+)/$', views.ArtistDetailView.as_view()),

    url(r'^album/$', ListView.as_view(model=Album)),
    url(r'^album/(?P<pk>\d+)/$', views.AlbumDetailView.as_view()),

    url(r'^song/$', ListView.as_view(model=Song)),
    url(r'^song/(?P<pk>\d+)/$', DetailView.as_view(model=Song)),

    #FIXME: expose views.update_library to admin only
    url(r'^update/$', views.update_library),
)

urlpatterns += staticfiles_urlpatterns()

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve',
                                  {'document_root': settings.MEDIA_ROOT})
    )
