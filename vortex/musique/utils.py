import os
import re
import zipfile
import tempfile

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


def titlecase(s):
    """Title case a string with correct handling of apostrophes.
    Code taken from the official Python documentation.
    """
    return re.sub(r"[A-Za-z]+('[A-Za-z]+)?",
                  lambda mo: mo.group(0)[0].upper() +
                             mo.group(0)[1:].lower(),
                  s)

def zip_folder(src_path, dst_path=None):
    """Zip a directory structure at src_path and returns the path of
    the resulting zip file.
    """
    if dst_path is None:
        dst_file = tempfile.NamedTemporaryFile(suffix='.zip', delete=False)
    else:
        dst_file = open(dst_path, 'w')
    zfile = zipfile.ZipFile(dst_file, 'w')
    dirname = os.path.dirname(src_path) + os.path.sep
    for root, dirs, files in os.walk(src_path, topdown=False):
        for name in files:
            full_name = os.path.join(root, name)
            zfile.write(full_name, full_name.replace(dirname, '', 1))
    zfile.close()
    dst_file.close()
    return dst_file.name
