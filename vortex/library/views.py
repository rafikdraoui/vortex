import re
import tempfile

from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views import defaults
from django.views.decorators.csrf import requires_csrf_token
from django.views.generic import DetailView, ListView
from django.utils.encoding import iri_to_uri
from django.utils.http import urlquote
from django.utils.translation import ugettext_lazy as _

from vortex.library import update
from vortex.library.models import Artist, Album, Song
from vortex.library.utils import (full_path,
                                  get_alphabetized_list,
                                  remove_empty_directories,
                                  sync_cover_images,
                                  sync_song_files,
                                  zip_folder)


class AlphabetizedListView(ListView):
    def get_context_data(self, **kwargs):
        context = super(AlphabetizedListView, self).get_context_data(**kwargs)
        context['alpha_list'] = get_alphabetized_list(self.model)
        return context


# Subclassed to ensure that the download url is up to date.
class SongDetailView(DetailView):
    def get_object(self, queryset=None):
        obj = super(SongDetailView, self).get_object(queryset)
        sync_song_files([obj])
        return obj


def library_home(request):
    return render(request, 'library/home.html')


def update_library(request):
    #TODO: run asynchronously (using celery?)
    update.update()
    messages.add_message(request,
                         messages.INFO,
                         _('Library successfully updated'),
                         fail_silently=True)
    return redirect(reverse(library_home))


def _download(instance):
    """Returns a HTTP response that is a ZIP file of the folder
    at instance.filepath.
    """
    tfile = tempfile.NamedTemporaryFile(suffix='.zip')
    zip_folder(full_path(instance.filepath), tfile.name)

    #TODO: Use iterator instead in case data is too big for memory. This
    # implies that the temporary file needs to stay on disk during download,
    # and that it is deleted at some later time.
    tfile.seek(0)
    data = tfile.read()
    tfile.close()

    response = HttpResponse(data, content_type='application/zip')
    filename = iri_to_uri(urlquote(unicode(instance)))
    response['Content-Disposition'] = \
        u'attachment; filename=%s.zip' % filename
    return response


def download_artist(request, pk):
    artist = Artist.objects.get(pk=pk)
    num_songs = Song.objects.filter(album__artist=artist).count()
    if num_songs == 0:
        messages.add_message(
            request, messages.INFO, _('The artist does not have any song'))
        return redirect(artist.get_absolute_url())
    else:
        sync_song_files(Song.objects.filter(album__artist=artist))
        sync_cover_images(Album.objects.filter(artist=artist))
        remove_empty_directories(artist.filepath)
        return _download(artist)


def download_album(request, pk):
    album = Album.objects.get(pk=pk)
    if album.song_set.count() == 0:
        messages.add_message(
            request, messages.INFO, _('The album does not have any song'))
        return redirect(album.get_absolute_url())
    else:
        sync_song_files(Song.objects.filter(album=album))
        sync_cover_images([album])
        remove_empty_directories(album.filepath)
        return _download(album)


@requires_csrf_token
def page_not_found(request, template_name='404.html'):
    """Overridden so that a 404 to non-existing artist, album or
    song redirects to the artist list, album list or song list
    views instead of serving a 404 error.
    """

    if re.match(r'/library/artist/\d+/', request.path):
        return redirect(reverse('artist_list'))
    if re.match(r'/library/album/\d+/', request.path):
        return redirect(reverse('album_list'))
    if re.match(r'/library/song/\d+/', request.path):
        return redirect(reverse('song_list'))

    if re.match(r'/admin/library/artist/(\d+|None)/', request.path):
        return redirect(reverse('admin:library_artist_changelist'))
    if re.match(r'/admin/library/album/(\d+|None)/', request.path):
        return redirect(reverse('admin:library_album_changelist'))
    if re.match(r'/admin/library/song/(\d+|None)/', request.path):
        return redirect(reverse('admin:library_song_changelist'))

    return defaults.page_not_found(request, template_name)
