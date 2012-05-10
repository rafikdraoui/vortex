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
