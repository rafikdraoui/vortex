# Django settings for vortex project.

# This is a generic public settings file. To have a working app you should
# put your local settings into a file called local_settings.py

import os

PROJECT_DIR = os.path.dirname(__file__)

try:
    from vortex.conf import *
except:
    from django.core.exceptions import ImproperlyConfigured
    raise ImproperlyConfigured(
                'vortex.conf is missing or is improperly configured')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.',  # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': '',                       # Or path to database file if using sqlite3.
        'USER': '',                       # Not used with sqlite3.
        'PASSWORD': '',                   # Not used with sqlite3.
        'HOST': '',                       # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                       # Set to empty string for default. Not used with sqlite3.
    }
}

SITE_ID = 1

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

FILE_UPLOAD_PERMISSIONS = 0644

MEDIA_URL = '/media/'

STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(PROJECT_DIR, 'static'),
)

TEMPLATE_DIRS = (
    os.path.join(PROJECT_DIR, 'templates'),
)

LOCALE_PATHS = (
    os.path.join(PROJECT_DIR, 'locale'),
)

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

    'vortex.library',
    'vortex.player',
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
        'vortex.library.update': {
            'handlers': ['vortex_log'],
            'level': 'INFO'
        },
        'vortex.library.models': {
            'handlers': ['vortex_log'],
            'level': 'INFO'
        }
    }
}

HAYSTACK_SITECONF = 'vortex.library.search_sites'
HAYSTACK_SEARCH_ENGINE = 'simple'
HAYSTACK_SEARCH_RESULTS_PER_PAGE = 100

try:
    from local_settings import *
except:
    pass
