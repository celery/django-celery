"""

Start the celery daemon from the Django management command.

"""
from __future__ import absolute_import, unicode_literals

from celery.bin import worker

from djcelery.app import app
from djcelery.management.base import CeleryCommand

worker = worker.worker(app=app)


class Command(CeleryCommand):
    """Run the celery daemon."""
    help = 'Old alias to the "celery worker" command.'
    options = (
        tuple(CeleryCommand.options) +
        tuple(worker.get_options()) +
        tuple(getattr(worker, 'preload_options', ()))
    )

    def handle(self, *args, **options):
        worker.check_args(args)
        worker.run(**options)
