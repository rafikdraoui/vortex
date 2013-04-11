from __future__ import unicode_literals

import os
import sys

from django.core.exceptions import ImproperlyConfigured
from django.utils.encoding import smart_text


def get_from_env(var, default=None, required=False):
    """Helper function to convert bytestrings retrieved from the environment to unicode."""

    encoding = sys.getfilesystemencoding()
    s = os.environ.get(var, default)

    if required and s is None:
        raise ImproperlyConfigured(
            'Configuration setting "{}" is required. '
            'It should be defined as an environment variable'.format(var))

    return smart_text(s, encoding=encoding, strings_only=True)


# The directory in which files that are to be imported into the music
# library are uploaded.
DROPBOX = get_from_env('VORTEX_DROPBOX', required=True)

# The directory in which media files will be kept. This should be the same
# as the `music_directory` option in the `mpd.conf` file of the mpd server.
MEDIA_ROOT = get_from_env('VORTEX_MEDIA_ROOT', required=True)

# Files that are removed from the dropbox by the file import routine.
# (specified as python regular expressions).
DUMMY_FILES = [r'\.DS_Store', r'Thumbs\.db', r'desktop\.ini', r'\._*']

# Supported audio formats.
SUPPORTED_FORMATS = ['mp3', 'mp4', 'ogg', 'flac', 'wma']

# The file used for logging.
LOGFILE = get_from_env('VORTEX_LOGFILE', required=True)

# See http://docs.python.org/library/logging.html#logrecord-attributes for
# valid attributes for log record format expansion.
LOGFORMAT = '%(asctime)s: %(message)s'

# Option to automatically titlecase the names of artists and albums that are
# uploaded from the dropbox.
TITLECASE_ARTIST_AND_ALBUM_NAMES = False

# MPD configuration.
MPD_HOST = get_from_env('MPD_HOST', 'localhost')
MPD_PORT = int(get_from_env('MPD_PORT', 6600))
MPD_PASSWORD = get_from_env('MPD_PASSWORD')

# Time (in ms) between updating of player interface (put 0 for never).
PLAYER_REFRESH_INTERVAL = 5000
