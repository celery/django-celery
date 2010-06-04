"""

Curses Celery Event Viewer.

"""
from django.core.management.base import BaseCommand

from celery.bin.celeryev import run_celeryev, OPTION_LIST


class Command(BaseCommand):
    """Run the celery curses event viewer."""
    option_list = BaseCommand.option_list + OPTION_LIST
    help = 'curses celery event viewer'

    def handle(self, *args, **options):
        """Handle the management command."""
        run_celeryev(*args, **options)
