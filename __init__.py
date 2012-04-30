import ConfigParser

from vortex.settings import LOGGING


def get_config(config_path='config/vortex.conf'):
    """Return the configuration file as a ConfigParser object"""
    config = ConfigParser.ConfigParser()
    config.read(config_path)
    return config


def add_logging_config(config_path='config/vortex.conf'):
    """Add logging configuration to the settings to create a custom logger"""
    config = get_config(config_path)
    logfile = config.get('log', 'logfile')
    logformat = config.get('log', 'logformat', raw=1)

    if not 'formatters' in LOGGING:
        LOGGING['formatters'] = {}
    LOGGING['formatters']['vortex_fmt'] = {'format': logformat}

    if not 'handlers' in LOGGING:
        LOGGING['handlers'] = {}
    LOGGING['handlers']['vortex_log'] = {'class': 'logging.FileHandler',
                                         'filename': logfile,
                                         'formatter': 'vortex_fmt'}
    if not 'loggers' in LOGGING:
        LOGGING['loggers'] = {}
    LOGGING['loggers']['vortex.musique.library'] = {'handlers': ['vortex_log'],
                                                    'level': 'INFO'}
    LOGGING['loggers']['vortex.musique.models'] = {'handlers': ['vortex_log'],
                                                   'level': 'INFO'}


add_logging_config()
