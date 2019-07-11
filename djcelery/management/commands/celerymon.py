"""

Start the celery clock service from the Django management command.

"""
from __future__ import absolute_import, unicode_literals

import sys

from djcelery.app import app
from djcelery.management.base import CeleryCommand

try:
    from celerymon.bin.celerymon import MonitorCommand
    mon = MonitorCommand(app=app)
except ImportError:
    mon = None

MISSING = """
You don't have celerymon installed, please install it by running the following
command:

    $ pip install -U celerymon

or if you're still using easy_install (shame on you!)

    $ easy_install -U celerymon
"""


class Command(CeleryCommand):
    """Run the celery monitor."""
    help = 'Run the celery monitor'
    options = (
        tuple(CeleryCommand.options) +
        (
            tuple(mon.get_options()) +
            tuple(getattr(mon, 'preload_options', ()))
        ) if mon else ()
    )

    def handle(self, *args, **options):
        """Handle the management command."""
        if mon is None:
            sys.stderr.write(MISSING)
        else:
            mon.run(**options)
