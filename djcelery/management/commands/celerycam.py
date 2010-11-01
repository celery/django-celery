"""

Curses Celery Event Viewer.

"""
from celery.bin import celeryev

from djcelery.management.base import CeleryCommand

ev = celeryev.EvCommand()


class Command(CeleryCommand):
    """Run the celery curses event viewer."""
    option_list = CeleryCommand.option_list + ev.get_options()
    help = 'Takes snapshots of the clusters state to the database.'

    def handle(self, *args, **options):
        """Handle the management command."""
        options["camera"] = "djcelery.snapshot.Camera"
        ev.run(*args, **options)
