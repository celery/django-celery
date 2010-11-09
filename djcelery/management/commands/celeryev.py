"""

Curses Celery Event Viewer.

"""
from celery.bin import celeryev

from djcelery.app import app
from djcelery.management.base import CeleryCommand

ev = celeryev.EvCommand(app=app)


class Command(CeleryCommand):
    """Run the celery curses event viewer."""
    option_list = CeleryCommand.option_list + ev.get_options()
    help = 'curses celery event viewer'

    def handle(self, *args, **options):
        """Handle the management command."""
        ev.run(*args, **options)
