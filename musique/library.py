import os
import shutil
import re
import logging

import mutagen

from django.core.files import File
from django.db import IntegrityError

from vortex.musique.models import Artist, Album, Song


logger = logging.getLogger(__name__)


def get_mutagen_audio_options():
    """Build the list of options to give mutagen.File for reading
    audio tags according to the supported formats in the config
    """

    formats = settings.SUPPORTED_FORMATS

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


#TODO: log exceptions
def update():
    """Import into the library all files in the directory structure
    rooted at `DROPBOX`.

    The files that are successfully imported are moved into the
    `MEDIA_ROOT` folder. The others are left in place, except for those
    whose name matches one in `DUMMY_FILES`, which are deleted.
    """

    mutagen_options = get_mutagen_audio_options()
    for root, dirs, files in os.walk(settings.DROPBOX, topdown=False):
        for name in files:
            if name in settings.DUMMY_FILES \
               or name.endswith(('jpg', 'jpeg', 'gif', 'png')):
                #FIXME: keep images for cover image
                try:
                    os.remove(os.path.join(root, name))
                except Exception:
                    pass
            else:
                import_file(unicode(os.path.join(root, name)),
                            mutagen_options)
        try:
            if root != settings.DROPBOX:
                os.rmdir(root)
        except Exception:
            pass


def import_file(filename, mutagen_options):
    """Import the song referred to by filename into the library

    Arguments:
        filename - the filename of the audio file to import
        mutagen_options - list of options needed by mutagen.File
    """

    try:
        info = get_song_info(filename, mutagen_options)
    except ValueError:
        handle_import_error(filename, 'mutagen error')
        return

    artist_name = info['artist'].title()
    artist_path = os.path.join(artist_name[0], artist_name)
    artist, created = Artist.objects.get_or_create(name=artist_name,
                                                   filepath=artist_path)

    album_path = os.path.join(artist_path, info['album'].title())
    album, created = Album.objects.get_or_create(title=info['album'].title(),
                                                 artist=artist,
                                                 filepath=album_path)

    filetype = filename.rsplit('.')[-1].lower()
    original_path = filename.replace(settings.DROPBOX, '', 1)

    #TODO: Handle Unknown Title by Unknown Artist
    try:
        song, created = Song.objects.get_or_create(
            title=info['title'], artist=artist, album=album,
            track=info['track'], bitrate=info['bitrate'], filetype=filetype,
            defaults={'filefield': File(open(filename, 'rb')),
                      'original_path': original_path})
    except IntegrityError, msg:
        handle_import_error(filename, msg)
        return
    except Exception, msg:
        handle_import_error(filename, msg)
        return

    if not created:
        # Song already exists, keep only if better bitrate
        if song.bitrate >= info['bitrate']:
            #FIXME: uncomment when Unknown songs are handled correctly
            #os.remove(filename)
            logger.info('%s (by %s) already exists'
                            % (song.title, song.artist.name))
            return
        else:
            song.bitrate = info['bitrate']
            song.filefield = File(open(filename, 'rb'))
            song.original_path = original_path
            song.save()


def get_tag_field(container, tag_name):
    tag = container.get(tag_name, [u'Unknown %s' % tag_name.capitalize()])[0]
    tag = tag or u'Unknown %s' % tag_name.capitalize()
    return tag.replace('/', '-')


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

    title = get_tag_field(audio, 'title')
    artist = get_tag_field(audio, 'artist')
    album = get_tag_field(audio, 'album')
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


def handle_import_error(filename, error_msg=None):
    log_msg = 'Problem importing file %s' % filename
    if error_msg:
        log_msg = '%s (%s)' % (log_msg, error_msg)
    logger.info(log_msg)
