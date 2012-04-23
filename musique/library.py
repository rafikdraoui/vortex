import os
import shutil
import logging
import re

import mutagen

import vortex
from vortex.musique.models import Artist, Album, Song


config = vortex.get_config()
vortex.add_logging_config()
logger = logging.getLogger(__name__)


def get_mutagen_audio_options():
    """Build the list of options to give mutagen.File for reading
    audio tags according to the supported formats in the config
    """

    formats_string = config.get('vortex', 'formats')
    formats = [fmt.strip() for fmt in formats_string.split(',')]

    from mutagen.easyid3 import EasyID3FileType
    audio_options = [EasyID3FileType]
    for fmt in formats:
        if fmt == 'mp3':
            from mutagen.mp3 import EasyMP3
            audio_options.append(EasyMP3)
        elif fmt == 'mp4':
            from mutagen.easymp4 import EasyMP4
            audio_options.append(EasyMP4)
        elif fmt == 'ogg':
            from mutagen.oggvorbis import OggVorbis
            from mutagen.oggspeex import OggSpeex
            from mutagen.oggflac import OggFLAC
            audio_options += [OggVorbis, OggSpeex, OggFLAC]
        elif fmt == 'flac':
            from mutagen.flac import FLAC
            audio_options.append(FLAC)
        else:
            logger.info('"%s" support not implemented yet' % fmt)

    return audio_options


def update():
    """Import into the library all files in the directory structure
    rooted at `dropbox`.

    The files that are successfully imported are moved into the
    `media_root` folder. The others are left in place, except for those
    whose name matches one in `dummy_files`, which are deleted.
    """

    dummy_files = [f.strip() for f in
                   config.get('vortex', 'dummy_files').split(',')]
    dropbox = unicode(config.get('vortex', 'dropbox'))
    media_root = unicode(config.get('vortex', 'media_root'))
    mutagen_options = get_mutagen_audio_options()
    for root, dirs, files in os.walk(dropbox, topdown=False):
        for name in files:
            if name in dummy_files \
               or name.endswith(('jpg', 'jpeg', 'gif', 'png')):
                #FIXME: keep images for cover image
                os.remove(os.path.join(root, name))
            else:
                import_file(unicode(os.path.join(root, name)),
                            media_root,
                            mutagen_options)
        try:
            if root != dropbox:
                os.rmdir(root)
        except Exception:
            pass


def import_file(filename, media_root, mutagen_options):
    """Import the song referred to by filename into the library

    Arguments:
        filename - the filename of the audio file to import
        media_root - the base directory to which the file will be moved
        mutagen_options - list of options needed by mutagen.File
    """

    try:
        info = get_song_info(filename, mutagen_options)
    except ValueError:
        handle_import_error(filename)
        return

    artist_name = info['artist'].title()
    artist_path = u'%s/%s' % (artist_name[0], artist_name)
    artist, created = Artist.objects.get_or_create(name=artist_name,
                                                   filepath=artist_path)

    album_path = u'%s/%s' % (artist_path, info['album'].title())
    album, created = Album.objects.get_or_create(title=info['album'].title(),
                                                 artist=artist,
                                                 filepath=album_path)

    extension = filename.rsplit('.')[-1].lower()
    basename = u'%s.%s' % (info['title'], extension)
    if info['track']:
        basename = u'%s - %s' % (info['track'], basename)

    filepath = u'%s/%s' % (album_path, basename)
    fullpath = media_root + filepath

    #TODO: Handle Unkown Title by Unknown Artist
    song, created = Song.objects.get_or_create(title=info['title'],
                                               artist=artist,
                                               album=album,
                                               track=info['track'],
                                               bitrate=info['bitrate'],
                                               filepath=filepath)
    if not created:
        # Song already exists, keep only if better bitrate
        if song.bitrate >= info['bitrate']:
            os.remove(filename)
            logger.info('%s already exists' % basename)
            return
        else:
            song.bitrate = info['bitrate']
            os.chmod(filename, 0644)
            shutil.move(filename, fullpath)
            return

    # if we get here this is a brand new song
    if not os.path.exists(os.path.dirname(fullpath)):
        os.makedirs(os.path.dirname(fullpath))
    os.chmod(filename, 0644)
    shutil.move(filename, fullpath)


def get_song_info(filename, mutagen_options):
    """Returns a dictionnary describing attributes of the audio file
    referred to by `filename`.

    Arguments:
        filename - the full path of the audio file
        mutagen_options - list of options needed by mutagen.File
    """

    audio = mutagen.File(filename, options=mutagen_options)
    if audio is None:
        raise ValueError

    get_tag_field = lambda tag: \
        audio.get(tag,
                 [u'Unknown %s' % tag.capitalize()])[0].replace('/', '-')

    title = get_tag_field('title')
    artist = get_tag_field('artist')
    album = get_tag_field('album')
    track = audio.get('tracknumber', [u''])[0]

    try:
        track = re.match(r'\d+', track).group()
        if len(track) == 1:
            track = u'0' + track
    except AttributeError:
        track = u''

    try:
        bitrate = audio.info.bitrate
    except AttributeError:
        # Flac files have no bitrate attribute
        bitrate = 0

    return {'title': title, 'artist': artist, 'album': album,
            'track': track, 'bitrate': bitrate}


def handle_import_error(filename):
    logger.info('Problem importing file %s' % filename)
