import os
import zipfile

from django.conf import settings
from django.core.files.base import ContentFile

from .models import Artist, Album, Song


def full_path(name):
    return os.path.join(settings.MEDIA_ROOT, name)


def titlecase(s):
    """Title case a string with correct handling of apostrophes and non-ascii
    characters.
    """
    split_titled = [w[0].upper() + w[1:].lower() for w in s.split()]
    return ' '.join(split_titled)


def zip_folder(src_path, dst_path):
    """Zip a directory structure at src_path into the file
    given by dst_path.
    """
    zfile = zipfile.ZipFile(dst_path, 'w')
    dirname = os.path.dirname(src_path) + os.path.sep
    for root, dirs, files in os.walk(src_path, topdown=False):
        for name in files:
            full_name = os.path.join(root, name)
            zfile.write(full_name, full_name.replace(dirname, '', 1))
    zfile.close()


def get_alphabetized_list(model):
    """Returns a list of dict with keys 'initial' and 'instance', where
    'instance' is an instance of the model given as input and 'initial' the
    first letter of the unicode representation of the instance. The list
    contains a dict for every instance of the model.

    The output is meant to be used by the 'regroup' built-in template tag.
    """
    instances = model.objects.all()
    thelist = [{'initial': unicode(instance)[0].upper(), 'instance': instance}
               for instance in instances]
    return sorted(thelist, key=lambda d: d['initial'])


def _sync_files(model, filefield_attr, filepath_attr, candidates=None):
    """Synchronize the files in the media directory with their corresponding
    model instances given in `candidates`. `filefield_attr` and `filepath_attr`
    are the names of the instances attributes corresponding to the filefield to
    be updated and the filepath of the file.
    """

    if not candidates:
        candidates = model.objects.select_related().iterator()
    for instance in candidates:
        thefile = getattr(instance, filefield_attr)
        current_path = thefile.name
        correct_path = getattr(instance, filepath_attr)
        if current_path != correct_path:
            content = ContentFile(thefile.read())
            thefile.delete(save=False)
            thefile.save(correct_path, content)


def sync_song_files(candidates=None):
    """Ensure that each song instance in the candidates has its file field at
    the right place in the media directory on the file system.
    """
    _sync_files(Song, 'filefield', 'filepath', candidates)


def sync_cover_images(candidates=None):
    """Ensure that each album instance in the candidates has its cover image
    file at the right place in the media directory on the file system.
    """
    _sync_files(Album, 'cover', 'cover_filepath', candidates)


def remove_empty_directories(root=None):
    """Remove empty directories from the media folder, starting at the given
    root directory (if not given, the whole media folder is processed).
    """
    top = full_path(root) if root else settings.MEDIA_ROOT
    for dirpath, dirnames, filenames in os.walk(top, topdown=False):
        for directory in dirnames:
            path = os.path.join(dirpath, directory)
            if not os.listdir(path):
                os.rmdir(path)
    if not os.listdir(top):
        os.rmdir(top)


def delete_empty_instances():
    """Delete every album that has no song and every artist that has no album.
    This is used by the `syncfiles` custom management command.
    """
    to_delete = []
    for album in Album.objects.iterator():
        if album.song_set.count() == 0:
            to_delete.append(album.pk)
    Album.objects.filter(id__in=to_delete).delete()

    to_delete = []
    for artist in Artist.objects.iterator():
        if artist.album_set.count() == 0:
            to_delete.append(artist.pk)
    Artist.objects.filter(id__in=to_delete).delete()
