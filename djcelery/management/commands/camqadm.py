"""

Celery AMQP Administration Tool using the AMQP API.

"""
from celery.bin.camqadm import camqadm, OPTION_LIST

from djcelery.management.base import CeleryCommand


class Command(CeleryCommand):
    """Run the celery daemon."""
    option_list = CeleryCommand.option_list + OPTION_LIST
    help = 'Celery AMQP Administration Tool using the AMQP API.'

    def handle(self, *args, **options):
        """Handle the management command."""
        camqadm(*args, **options)
