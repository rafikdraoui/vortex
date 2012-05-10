# Django settings for vortex project.

# This is a generic public settings file. To have a working app you should
# put your local settings into a file called local_settings.py

import os

try:
    from conf import *
except:
    #FIXME: more informative error
    raise

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.',  # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': '',                      # Or path to database file if using sqlite3.
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

SITE_ID = 1

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

FILE_UPLOAD_PERMISSIONS = 0644

STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(os.path.dirname(__file__), 'static'),
)

TEMPLATE_DIRS = (
    os.path.join(os.path.dirname(__file__), 'templates'),
)

ROOT_URLCONF = 'vortex.urls'

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'south',
    'vortex.musique',
)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'vortex_fmt': {
            'format': LOGFORMAT
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
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
        'vortex.musique.library': {
            'handlers': ['vortex_log'],
            'level': 'INFO'
        },
        'vortex.musique.models': {
            'handlers': ['vortex_log'],
            'level': 'INFO'
        }
    }
}

try:
    from local_settings import *
except:
    pass
