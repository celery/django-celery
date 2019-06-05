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
    cc_options = CeleryCommand.options if CeleryCommand.options else []
    worker_options = worker.get_options() if worker.get_options() else []
    preload_options = getattr(worker, 'preload_options', []) or []
    options = cc_options + worker_options + preload_options

    def handle(self, *args, **options):
        worker.check_args(args)
        worker.run(**options)
