import os
import sys

from django.core.exceptions import ImproperlyConfigured
from django.utils.encoding import smart_text


def get_from_env(var, default=None, required=False):
    """Helper function to convert bytestrings retrieved from the environment
    to unicode.
    """
    encoding = sys.getfilesystemencoding()
    s = os.environ.get(var, default)

    if required and s is None:
        raise ImproperlyConfigured(
            'Configuration setting "{}" is required. '
            'It should be defined as an environment variable'.format(var))

    return smart_text(s, encoding=encoding, strings_only=True)
