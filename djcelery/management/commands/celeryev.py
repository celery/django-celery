"""

Curses Celery Event Viewer.

"""
from celery.bin.celeryev import run_celeryev, OPTION_LIST

from djcelery.management.base import CeleryCommand


class Command(CeleryCommand):
    """Run the celery curses event viewer."""
    option_list = CeleryCommand.option_list + OPTION_LIST
    help = 'curses celery event viewer'

    def handle(self, *args, **options):
        """Handle the management command."""
        run_celeryev(*args, **options)
