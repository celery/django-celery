"""

Start the celery daemon from the Django management command.

"""
from celery.bin.celeryd import run_worker, OPTION_LIST

from djcelery.management.base import CeleryCommand


class Command(CeleryCommand):
    """Run the celery daemon."""
    requires_model_validation = True
    # Note: the filter of --version avoids a name conflict with
    # manage.py's --version option.  Still feels a little yuck.
    option_list = CeleryCommand.option_list + \
                  filter(lambda opt: '--version' not in opt._long_opts, \
                         OPTION_LIST)
    help = 'Run the celery daemon'

    def handle(self, *args, **options):
        """Handle the management command."""
        run_worker(**options)
