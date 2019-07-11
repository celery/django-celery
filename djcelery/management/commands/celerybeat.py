"""

Start the celery clock service from the Django management command.

"""
from __future__ import absolute_import, unicode_literals

from celery.bin import beat

from djcelery.app import app
from djcelery.management.base import CeleryCommand

beat = beat.beat(app=app)


class Command(CeleryCommand):
    """Run the celery periodic task scheduler."""
    help = 'Old alias to the "celery beat" command.'
    options = (
        tuple(CeleryCommand.options) +
        tuple(beat.get_options()) +
        tuple(getattr(beat, 'preload_options', ()))
    )

    def handle(self, *args, **options):
        beat.run(*args, **options)
