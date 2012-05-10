# The directory in which files that are to be imported into the music
# library are uploaded.
DROPBOX = '/path/to/dropbox'

# The directory in which media files will be kept. This should be the same
# as the `music_directory` option in the `mpd.conf` file of the mpd server.
MEDIA_ROOT = '/path/to/media/root'

# Files that are removed from the dropbox by the file import routine.
DUMMY_FILES = ['.DS_Store', 'Thumbs.db', 'desktop.ini']

# Supported audio formats.
SUPPORTED_FORMATS = ['mp3', 'mp4', 'ogg', 'flac']

# The file used for logging.
LOGFILE = '/path/to/logfile'

# See http://docs.python.org/library/logging.html#logrecord-attributes for
# valid attributes for log record format expansion.
LOGFORMAT = '%(asctime)s: %(message)s'

# Make this unique, and don't share it with anybody.
# Example:  'f8u=!_ql(0slj4y-n)4-1^qfe5sf5jhg$*(ms)a1%m&_te89-%'
SECRET_KEY = '___SECRET_KEY___'