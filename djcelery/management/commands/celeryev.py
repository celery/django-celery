"""

Curses Celery Event Viewer.

"""
from __future__ import absolute_import, unicode_literals

from celery.bin import celeryev

from djcelery.app import app
from djcelery.management.base import CeleryCommand

ev = celeryev.EvCommand(app=app)

SS_TRANSPORTS = ['amqplib', 'kombu.transport.amqplib',
                 'redis', 'kombu.transport.redis',
                 'pika', 'kombu.transport.pika']

SS_COMPAT = """
ERROR: Snapshots not currently supported by {0} transport.
Please use one of: {1}
"""


class Command(CeleryCommand):
    """Run the celery curses event viewer."""
    options = (CeleryCommand.options
             + ev.get_options()
             + ev.preload_options)
    help = 'Old alias to the "celery events" command'

    def handle(self, *args, **options):
        """Handle the management command."""
        transport = app.conf.BROKER_TRANSPORT or 'amqplib'
        if options['camera']:
            if transport not in SS_TRANSPORTS:
                self.die(SS_COMPAT.format(transport,
                    ', '.join(t for t in SS_TRANSPORTS if '.' not in t)))
        ev.run(*args, **options)
