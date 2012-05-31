import os
import shutil

from django.conf import settings
from django.core.files.storage import FileSystemStorage


class CustomStorage(FileSystemStorage):

    def _save(self, name, content):
        if self.exists(name):
            self.delete(name)
        return super(CustomStorage, self)._save(name, content)

    def get_available_name(self, name):
        return name


def path_exists(path):
    """Returns True iff the given path exists on the filesystem.

    This is needed for case-insensitive systems (Windows, OS X, ...).
    """
    dirname, basename = os.path.split(path)
    return basename in os.listdir(dirname)


def full_path(name):
    return os.path.join(settings.MEDIA_ROOT, name)
