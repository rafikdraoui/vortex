# vortex

A web client to control a [Music Player Daemon (mpd)][mpd] server and to
organize music libraries amongst a group of people.

> NOTE: This is still in development and is not yet fully functional. I am
> just exercising some [Readme Driven Development][rdd].


## Description

Audio files are uploaded to a `DROPBOX` folder, from where their tags are read
and used to import them into the music library. The files are moved into the
`MEDIA` folder, which is rigidly organized into a `artist/album/track-title`
hierarchy. This means that untagged files won't be imported and left into the
`DROPBOX`.

A web interface to `mpd` can be used to control playback, load and create
playlists, search the library and download audio files.


## Dependencies
* [django][]
* [south][] (for model migrations)
* [mutagen][] (for getting information on audio files)
* [haystack][] (for searching the library)
* [python-mpd][] (for interfacing with the mpd server)

Optional:

* [selenium][] (for running some unit tests)

These can all be installed using [pip][] with the command `pip install -r
requirements.txt`.


## Installation and Configuration

This is a Django application. Put it somewhere where your webserver can make
sense of it.

Before running the application, you need to sync the database and migrate the
table schemas with the following commands:

```
python manage.py syncdb
python manage.py migrate
```

You can also verify that all unit tests are passing with `python manage.py
test musique`.

You should change the `settings.py` file to fit your needs (or create
a `local_settings.py` file that overloads it). At the very least you need to
provide the followings:

* `SECRET_KEY`: the secret key used for security in Django. A string of 50
  random characters would do.

* `DATABASES`: configuration info for your database.

* `STATIC_ROOT`: the root folder on the file system from where static files
  will be served.

You might also want to change the Haystack search engine to a proper one, like
Solr or ElasticSearch.

Application specific settings are provided in a configuration file (by
default, it is `conf/vortex_config.py`).


## About

This is built by [Rafik Draoui][] and it is my first non-trivial personal
project. It was made for real-life usage in my household, but primarily for
providing an excuse to learn Django, i18n/l10n and whatever else would come up
in such a multi-faceted project.

[mpd]: http://musicpd.org
[rdd]: http://tom.preston-werner.com/2010/08/23/readme-driven-development.html
[django]: https://www.djangoproject.com
[mutagen]: https://code.google.com/p/mutagen
[haystack]: http://haystacksearch.org
[python-mpd]: http://pypi.python.org/pypi/python-mpd
[south]: http://south.aeracode.org
[selenium]: https://code.google.com/p/selenium
[pip]: http://www.pip-installer.org
[Rafik Draoui]: http://www.rafik.ca
