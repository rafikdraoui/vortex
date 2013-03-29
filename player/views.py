import json

from mpd import MPDClient, MPDError, ConnectionError

from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render
from django.utils.translation import ugettext_lazy as _


def player_home(request):
    return render(request,
                  'player/home.html',
                  {'REFRESH_INTERVAL': settings.PLAYER_REFRESH_INTERVAL})


def mpd_command(func):
    """Decorator for mpd commands. Handle connection, disconnection, error
    catching and json conversion of output.
    """

    def wrapper(request):
        client = MPDClient()
        try:
            client.connect(settings.MPD_HOST, settings.MPD_PORT)
            if settings.MPD_PASSWORD:
                client.password(settings.MPD_PASSWORD)
            result = func(client) or {'success': True}
        except (MPDError, IOError) as e:
            result = {
                'success': False,
                'error': _(
                    'Error while executing %(command)s: %(error_message)s'
                ) % {'command': func.__name__, 'error_message': e}
            }
        finally:
            try:
                client.close()
                client.disconnect()
            except ConnectionError:
                pass

        # add a success key in the result dict if not already present.
        result.setdefault('success', True)

        data = json.dumps(result)
        return HttpResponse(data, mimetype='application/json')

    return wrapper


@mpd_command
def play_pause(client):
    """Toggle playback."""
    state = client.status().get('state')
    if state == 'play':
        client.pause()
    else:
        client.play()


@mpd_command
def next(client):
    """Play next song."""
    client.next()


@mpd_command
def previous(client):
    """Play previous song."""
    client.previous()


@mpd_command
def random(client):
    """Toggle playlist randomization."""
    is_random = int(client.status().get('random'))
    client.random(1 - is_random)


@mpd_command
def repeat(client):
    """Toggle playlist repetition (i.e. looping)."""
    is_repeat = int(client.status().get('repeat'))
    client.repeat(1 - is_repeat)


@mpd_command
def get_current_info(client):
    """Retrieve information about the currently playing song and the
    state of the player.
    """
    song = client.currentsong()
    status = client.status()
    state = status.get('state')
    random = status.get('random') == '1'
    repeat = status.get('repeat') == '1'
    return dict(song=song, state=state, random=random, repeat=repeat)
