from django.conf import settings
from django.contrib import admin
from django.conf.urls.defaults import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from vortex.musique.views import home, page_not_found


admin.autodiscover()

handler404 = page_not_found

urlpatterns = patterns('',
    url(r'^$', home),
    url(r'^musique/', include('vortex.musique.urls')),
    url(r'^admin/', include(admin.site.urls)),
)

urlpatterns += staticfiles_urlpatterns()

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve',
                                  {'document_root': settings.MEDIA_ROOT})
    )
