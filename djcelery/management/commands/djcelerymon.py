"""

Curses Celery Event Viewer.

"""
from threading import Thread

from celery.bin.celeryev import run_celeryev, OPTION_LIST

from django.core.management.commands import runserver

from djcelery.management.base import CeleryCommand


class WebserverThread(Thread):

    def __init__(self, addrport="", *args, **options):
        Thread.__init__(self)
        self.addrport = addrport
        self.args = args
        self.options = options

    def run(self):
        runserver.Command().handle(self.addrport, *self.args, **self.options)


class Command(CeleryCommand):
    """Run the celery curses event viewer."""
    args = '[optional port number, or ipaddr:port]'
    option_list = runserver.Command.option_list + OPTION_LIST
    help = 'Starts Django Admin instance and celerycam in the same process.'

    def handle(self, addrport="", *args, **options):
        """Handle the management command."""
        server = WebserverThread(addrport, *args, **options)
        server.start()
        options["camera"] = "djcelery.snapshot.Camera"
        options["prog_name"] = "djcelerymon"
        run_celeryev(*args, **options)
