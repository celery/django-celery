"""

Shortcut to the Django snapshot service.

"""
from __future__ import absolute_import, unicode_literals

from celery.bin import events

from djcelery.app import app
from djcelery.management.base import CeleryCommand

ev = events.events(app=app)


class Command(CeleryCommand):
    """Run the celery curses event viewer."""
    help = 'Takes snapshots of the clusters state to the database.'
    options = (
        tuple(CeleryCommand.options) +
        tuple(ev.get_options()) +
        tuple(getattr(ev, 'preload_options', ()))
    )

    def handle(self, *args, **options):
        """Handle the management command."""
        options['camera'] = 'djcelery.snapshot.Camera'
        ev.run(*args, **options)
