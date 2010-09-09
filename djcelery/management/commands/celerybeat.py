"""

Start the celery clock service from the Django management command.

"""
from celery.bin.celerybeat import run_celerybeat, OPTION_LIST

from djcelery.management.base import CeleryCommand


class Command(CeleryCommand):
    """Run the celery periodic task scheduler."""
    option_list = CeleryCommand.option_list + OPTION_LIST
    help = 'Run the celery periodic task scheduler'

    def handle(self, *args, **options):
        """Handle the management command."""
        run_celerybeat(**options)
