from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib import admin

from library.views import page_not_found
from player.views import player_home


admin.autodiscover()

handler404 = page_not_found

urlpatterns = patterns('',
    url(r'^$', player_home, name='home'),
    url(r'^library/', include('library.urls')),
    url(r'^player/', include('player.urls')),
    url(r'^admin/', include(admin.site.urls)),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.MEDIA_ROOT
        })
    )
