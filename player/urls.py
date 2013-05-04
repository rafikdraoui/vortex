from django.conf.urls import patterns, url

from .views import (
    play_pause, next, previous, random, repeat, get_current_info,
    PlayerHomeView,
)

urlpatterns = patterns('',
    url(r'^$', PlayerHomeView.as_view(), name='player_home'),

    url(r'play-pause/$', play_pause, name='play_pause'),
    url(r'next/$', next, name='next'),
    url(r'previous/$', previous, name='previous'),
    url(r'random/$', random, name='random'),
    url(r'repeat/$', repeat, name='repeat'),
    url(r'update/$', get_current_info, name='get_current_info'),
)
