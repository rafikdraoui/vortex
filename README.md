# vortex

A web client to control a [Music Player Daemon (mpd)](http://musicpd.org)
server and to organize music libraries amongst a group of people.

> NOTE: This is still in development and is not yet fully functional. I am
> just exercising some [Readme Driven Development][rdd].


## Description

Audio files are uploaded to a `DROPBOX` folder, from where their tags are
read and used to import them into the music library. The files are moved
into the `MEDIA` folder, which is rigidly organized into a
`artist/album/track-title` hierarchy. This means that untagged files won't
be imported and left into the `DROPBOX`.

A web interface to `mpd` can be used to control playback, load and create
playlists, search the library and download audio files.


## Dependencies
* [django][]
* [mutagen][] (for getting information on audio files)
* [python-mpd][] (for interfacing with the mpd server)

Optional:

* [south][] (for model migrations)

These can all be installed using [pip][]


## Installation and Configuration

This is a Django application. Put it somewhere where your webserver can
make sense of it.

You should change the settings.py file to fit your needs (or create a
local\_settings.py file that overloads it). At the very least you need to
provide the followings:

* `SECRET_KEY`: the secret key used for security in Django. A string of 50
  random characters would do.

* `DATABASES`: configuration info for your database.

Application specific settings are provided in a configuration file (by
default, it is `conf/vortex_config.py`).


## About

This is built by [Rafik Draoui][me] and it is my first
non-trivial personal project. It was made for real-life usage in my
household, but primarily for providing an excuse to learn Django, i18n/l10n
and whatever else would come up in such a multi-faceted project.


[rdd]: http://tom.preston-werner.com/2010/08/23/readme-driven-development.html
[django]: https://www.djangoproject.com
[mutagen]: https://code.google.com/p/mutagen
[python-mpd]: http://pypi.python.org/pypi/python-mpd
[south]: http://south.aeracode.org
[pip]: http://www.pip-installer.org
[me]: https://github.com/rafikdraoui
