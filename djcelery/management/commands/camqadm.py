"""

Celery AMQP Administration Tool using the AMQP API.

"""
from celery.bin import camqadm

from djcelery.app import app
from djcelery.management.base import CeleryCommand

command = camqadm.AMQPAdminCommand(app=app)


class Command(CeleryCommand):
    """Run the celery daemon."""
    option_list = CeleryCommand.option_list + command.get_options()
    help = 'Celery AMQP Administration Tool using the AMQP API.'

    def handle(self, *args, **options):
        """Handle the management command."""
        command.run(*args, **options)
