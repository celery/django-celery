"""

Curses Celery Event Viewer.

"""
from threading import Thread

from celery.bin import celeryev

from django.core.management.commands import runserver

from djcelery.management.base import CeleryCommand

ev = celeryev.EvCommand()


class WebserverThread(Thread):

    def __init__(self, addrport="", *args, **options):
        Thread.__init__(self)
        self.addrport = addrport
        self.args = args
        self.options = options

    def run(self):
        options = dict(self.options, use_reloader=False)
        runserver.Command().handle(self.addrport, *self.args, **options)


class Command(CeleryCommand):
    """Run the celery curses event viewer."""
    args = '[optional port number, or ipaddr:port]'
    option_list = runserver.Command.option_list + ev.get_options()
    help = 'Starts Django Admin instance and celerycam in the same process.'

    def handle(self, addrport="", *args, **options):
        """Handle the management command."""
        server = WebserverThread(addrport, *args, **options)
        server.start()
        options["camera"] = "djcelery.snapshot.Camera"
        options["prog_name"] = "djcelerymon"
        ev.run(*args, **options)
