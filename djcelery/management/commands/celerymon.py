"""

Start the celery clock service from the Django management command.

"""
import sys

from djcelery.management.base import CeleryCommand

try:
    from celerymonitor.bin.celerymond import run_monitor, OPTION_LIST
except ImportError:
    OPTION_LIST = ()
    run_monitor = None

MISSING = """
You don't have celerymon installed, please install it by running the following
command:

    $ pip install -U celerymon

or if you're still using easy_install (shame on you!)

    $ easy_install -U celerymon
"""


class Command(CeleryCommand):
    """Run the celery monitor."""
    option_list = CeleryCommand.option_list + OPTION_LIST
    help = 'Run the celery monitor'

    def handle(self, *args, **options):
        """Handle the management command."""
        if run_monitor is None:
            sys.stderr.write(MISSING)
        else:
            run_monitor(**options)
