from django.conf.urls import patterns, url

from vortex.player.views import *

urlpatterns = patterns('',
    url(r'^$', player_home, name='player_home'),

    url(r'play-pause/$', play_pause, name='play_pause'),
    url(r'next/$', next, name='next'),
    url(r'previous/$', previous, name='previous'),
    url(r'random/$', random, name='random'),
    url(r'repeat/$', repeat, name='repeat'),
    url(r'update/$', get_current_info, name='get_current_info'),
)
