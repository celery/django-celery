"""

Curses Celery Event Viewer.

"""
from django.core.management.base import BaseCommand

from celery.bin.celeryctl import celeryctl, Command as _Command

from djcelery import __version__

# Django hijacks the version output and prints its version before our
# version. So display the names of the products so the output is sensible.
_Command.version = "celery %s\ndjango-celery %s" % (_Command.version,
                                                    __version__)

class Command(BaseCommand):
    """Run the celery control utility."""
    help = "celery control utility"

    def run_from_argv(self, argv):
        util = celeryctl()
        util.execute_from_commandline(argv[1:])
