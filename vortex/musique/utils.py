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


def path_exists(path):
    """Returns True iff the given path exists on the filesystem.

    This is needed for case-insensitive systems (Windows, OS X, ...).
    """
    dirname, basename = os.path.split(path)
    return basename in os.listdir(dirname)


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
