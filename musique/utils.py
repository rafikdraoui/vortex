import os
import shutil

from vortex.settings import MEDIA_ROOT


def path_exists(path):
    """Returns True iff the given path exists on the filesystem.

    This is needed for case-insensitive systems (Windows, OS X, ...).
    """
    dirname, basename = os.path.split(path)
    return basename in os.listdir(dirname)


def full_path(name):
    return os.path.join(MEDIA_ROOT, name)
