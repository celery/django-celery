"""

Curses Celery Event Viewer.

"""
from celery.bin.celeryev import run_celeryev, OPTION_LIST

from djcelery.management.base import CeleryCommand


class Command(CeleryCommand):
    """Run the celery curses event viewer."""
    option_list = CeleryCommand.option_list + OPTION_LIST
    help = 'Takes snapshots of the clusters state to the database.'

    def handle(self, *args, **options):
        """Handle the management command."""
        options["camera"] = "djcelery.snapshot.Camera"
        run_celeryev(*args, **options)
