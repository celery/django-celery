"""

Start the celery clock service from the Django management command.

"""
from celery.bin import celerybeat

from djcelery.management.base import CeleryCommand

beat = celerybeat.BeatCommand()


class Command(CeleryCommand):
    """Run the celery periodic task scheduler."""
    option_list = CeleryCommand.option_list + beat.get_options()
    help = 'Runs the Celery periodic task scheduler'

    def handle(self, *args, **options):
        beat.run(*args, **options)
