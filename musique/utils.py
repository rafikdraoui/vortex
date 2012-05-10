import os
import shutil

from django.conf import settings


def path_exists(path):
    """Returns True iff the given path exists on the filesystem.

    This is needed for case-insensitive systems (Windows, OS X, ...).
    """
    dirname, basename = os.path.split(path)
    return basename in os.listdir(dirname)


def full_path(name):
    return os.path.join(settings.MEDIA_ROOT, name)


def move_album(src, dst):
    if path_exists(full_path(dst)):
        for song in os.listdir(full_path(src)):
            shutil.move(full_path(os.path.join(src, song)), full_path(dst))
        os.rmdir(full_path(src))
    else:
        shutil.copytree(full_path(src), full_path(dst))
        shutil.rmtree(full_path(src))
