# Django settings for vortex project.

# This a generic settings file. It assumes that some options have been defined
# in vortex.config and through environment variables. You can override some
# settings or add extra ones (like ADMINS or LANGUAGE_CODE) in a file called
# local.py.

import os
import dj_database_url
from django.core.exceptions import ImproperlyConfigured


PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))


# Import app specific settings.
try:
    from vortex.config import *
except ImportError:
    raise ImproperlyConfigured(
        'vortex.config is missing or is improperly configured')
except KeyError as e:
    raise ImproperlyConfigured(
        '%s configuration option is missing. '
        'It should be defined as an environment variable.' % e)

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

STATIC_ROOT = os.environ.get('VORTEX_STATIC_ROOT', '')

TEMPLATE_DIRS = (
    os.path.join(PROJECT_ROOT, 'templates'),
)

LOCALE_PATHS = (
    os.path.join(PROJECT_ROOT, 'locale'),
)

SECRET_KEY = os.environ.get('VORTEX_SECRET_KEY', '')

ROOT_URLCONF = 'vortex.urls'

WSGI_APPLICATION = 'vortex.wsgi.application'

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
HAYSTACK_SITECONF = 'library.search_sites'
HAYSTACK_SEARCH_ENGINE = 'simple'
HAYSTACK_SEARCH_RESULTS_PER_PAGE = 100
