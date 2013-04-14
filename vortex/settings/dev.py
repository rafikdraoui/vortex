from .base import *


DEBUG = True
TEMPLATE_DEBUG = DEBUG

#LANGUAGE_CODE = 'fr'

MIDDLEWARE_CLASSES += (
    'debug_toolbar.middleware.DebugToolbarMiddleware',
)

INSTALLED_APPS += (
    'devserver',
    'debug_toolbar',
)

INTERNAL_IPS = ('127.0.0.1',)
