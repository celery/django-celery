"""

Start the celery clock service from the Django management command.

"""
from __future__ import absolute_import

from celery.bin import celerybeat

from djcelery.app import app
from djcelery.management.base import CeleryCommand

beat = celerybeat.BeatCommand(app=app)


class Command(CeleryCommand):
    """Run the celery periodic task scheduler."""
    option_list = CeleryCommand.option_list + beat.get_options()
    help = 'Runs the Celery periodic task scheduler'

    def handle(self, *args, **options):
        beat.run(*args, **options)
