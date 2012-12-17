from django.core.management.base import NoArgsCommand

from vortex.library.utils import (delete_empty_instances,
                                  remove_empty_directories,
                                  sync_cover_images,
                                  sync_song_files)


class Command(NoArgsCommand):
    help = """Delete empty album and artist instances and synchronizes the
files in the media folder with the models in the music library."""

    def handle_noargs(self, **options):
        delete_empty_instances()
        sync_song_files()
        sync_cover_images()
        remove_empty_directories()
