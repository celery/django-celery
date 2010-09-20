"""

Start the celery daemon from the Django management command.

"""
from celery.bin import celeryd

from djcelery.management.base import CeleryCommand

worker = celeryd.WorkerCommand()


class Command(CeleryCommand):
    """Run the celery daemon."""
    help = 'Runs a Celery worker node.'
    requires_model_validation = True
    option_list = CeleryCommand.option_list + worker.get_options()

    def handle(self, *args, **options):
        worker.run(*args, **options)
