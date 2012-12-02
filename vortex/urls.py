from django.conf import settings
from django.conf.urls import patterns, include, url, handler404
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from vortex.library.views import page_not_found
from vortex.player.views import player_home


admin.autodiscover()

handler404 = page_not_found

urlpatterns = patterns('',
    url(r'^$', player_home, name='home'),
    url(r'^library/', include('vortex.library.urls')),
    url(r'^player/', include('vortex.player.urls')),
    url(r'^admin/', include(admin.site.urls)),
)

urlpatterns += staticfiles_urlpatterns()

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve',
                                  {'document_root': settings.MEDIA_ROOT})
    )
