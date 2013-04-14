"""
This a generic settings file. It assumes that some options have been defined in
vortex.config and through environment variables. You can override some settings
or add extra ones (like ADMINS or LANGUAGE_CODE) by creating another setting
file that imports all the variables from this file (see dev.py for an example)
and pointing to this custom file through the --settings option or
DJANGO_SETTINGS_MODULE environment variable.
"""
from __future__ import unicode_literals

import os
import dj_database_url
from django.core.exceptions import ImproperlyConfigured

from ..utils import get_from_env


PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))


# Import app specific settings.
try:
    from vortex.config import *
except ImportError:
    raise ImproperlyConfigured(
        'vortex.config is missing or is improperly configured')

# Parse database configuration from $DATABASE_URL environment variable.
DATABASES = {'default': dj_database_url.config()}

SITE_ID = 1

USE_L10N = True

FILE_UPLOAD_PERMISSIONS = 0644

MEDIA_URL = '/media/'

STATIC_URL = '/static/'

STATICFILES_DIRS = (
    os.path.join(PROJECT_ROOT, 'static'),
)

STATIC_ROOT = get_from_env('VORTEX_STATIC_ROOT', '')

TEMPLATE_DIRS = (
    os.path.join(PROJECT_ROOT, 'templates'),
)

LOCALE_PATHS = (
    os.path.join(PROJECT_ROOT, 'locale'),
)

SECRET_KEY = get_from_env('VORTEX_SECRET_KEY', required=True)

ROOT_URLCONF = 'vortex.urls'

WSGI_APPLICATION = 'vortex.wsgi.application'

ALLOWED_HOSTS = ('localhost', )

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',

    'south',
    'haystack',

    'library',
    'player',
)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'formatters': {
        'vortex_fmt': {
            'format': LOGFORMAT
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'vortex_log': {
            'class': 'logging.FileHandler',
            'filename': LOGFILE,
            'formatter': 'vortex_fmt'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        'library.models': {
            'handlers': ['vortex_log'],
            'level': 'INFO'
        },
        'library.update': {
            'handlers': ['vortex_log'],
            'level': 'INFO'
        }
    }
}

# Haystack settings
HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.simple_backend.SimpleEngine'
    }
}
HAYSTACK_SEARCH_RESULTS_PER_PAGE = 100
