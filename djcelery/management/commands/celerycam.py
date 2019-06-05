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
    cc_options = CeleryCommand.options if CeleryCommand.options else []
    ev_options = ev.get_options() if ev.get_options() else []
    preload_options = getattr(ev, 'preload_options', []) or []
    options = cc_options + ev_options + preload_options

    def handle(self, *args, **options):
        """Handle the management command."""
        options['camera'] = 'djcelery.snapshot.Camera'
        ev.run(*args, **options)
