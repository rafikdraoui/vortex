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
* [Python Imaging Library (PIL)][PIL] (for dealing with album cover art)
* [dj-database-url][] (for parsing a `$DATABASE_URL` env variable into a proper
                       database setting as required by Django)

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
test library`.

Configuration options are specified through environment variables, as Python
variables in `config.py` and optionally in a `local_settings.py` file that is
sourced by `django.conf.settings`.

### Environment variables

* `DATABASE_URL`: The URL for the database in a format suitable for
  `dj_database_url`. Eg: postgres://user@host:5432/vortex

* `VORTEX_MEDIA_ROOT`: The path of the directory in which music files are kept.
  This should be the same as the `music_directory` option in the configuration
  file of the mpd server.

* `VORTEX_DROPBOX`: The path of the directory in which files that are to be
  imported into the music library are uploaded.

* `VORTEX_LOGFILE`: The file used for logging. Note that this will probably be
  removed in the future to log directly to standard output in order for
  `vortex` to be more easily run as a managed app.

#### Optional

* `VORTEX_SECRET_KEY`: the secret key used for security in Django. A string of 50
  random characters would do.

* `VORTEX_STATIC_ROOT`: the root folder on the file system from where static files
  will be served.

* `MPD_HOST`, `MPD_PORT`, `MPD_PASSWORD`: MPD configuration.

### Other settings

The other settings are described in `config.py`. You might want to change the
Haystack search engine to a proper one, like Solr or ElasticSearch.


## About

This is built by [Rafik Draoui][] and it is my first non-trivial personal
project. It was made for real-life usage in my household, but primarily for
providing an excuse to learn Django, i18n and whatever else would come up in
such a multi-faceted project.

[mpd]: http://musicpd.org
[rdd]: http://tom.preston-werner.com/2010/08/23/readme-driven-development.html
[django]: https://www.djangoproject.com
[mutagen]: https://code.google.com/p/mutagen
[haystack]: http://haystacksearch.org
[python-mpd]: http://pypi.python.org/pypi/python-mpd
[PIL]: http://www.pythonware.com/products/pil
[south]: http://south.aeracode.org
[dj-database-url]: https://github.com/kennethreitz/dj-database-url
[pip]: http://www.pip-installer.org
[Rafik Draoui]: http://www.rafik.ca
