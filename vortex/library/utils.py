import os
import zipfile

from django.conf import settings
from django.core.files.storage import FileSystemStorage


class CustomStorage(FileSystemStorage):
    """Custom FileSystemStorage class that overwrites existing files."""

    def _save(self, name, content):
        if self.exists(name):
            self.delete(name)
        return super(CustomStorage, self)._save(name, content)

    def get_available_name(self, name):
        return name


def full_path(name):
    return os.path.join(settings.MEDIA_ROOT, name)


def titlecase(s):
    """Title case a string with correct handling of apostrophes and non-ascii
    characters.
    """
    split_titled = [w[0].upper() + w[1:].lower() for w in s.split()]
    return ' '.join(split_titled)


def _safe_rmdir(path):
    """Remove a directory with the given path from the file system if it is
    empty, logging any eventual error.
    """
    if not os.listdir(path):
        try:
            os.rmdir(path)
        except OSError as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.info('Problem deleting folder %s: %s' % (path, e))


def remove_empty_directories(root=None):
    """Remove empty directories from the media folder, starting at the given
    root directory (if not given, the whole media folder is processed).
    """
    top = root or settings.MEDIA_ROOT
    for dirpath, dirnames, filenames in os.walk(top, topdown=False):
        for directory in dirnames:
            path = os.path.join(dirpath, directory)
            _safe_rmdir(path)
    _safe_rmdir(top)


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
