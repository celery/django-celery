from __future__ import absolute_import

import os
import sys

from django.core.management.base import BaseCommand

import celery
import djcelery


class CeleryCommand(BaseCommand):

    def get_version(self):
        return "celery %s\ndjango-celery %s" % (celery.__version__,
                                                djcelery.__version__)

    def handle_default_options(self, argv):
        acc = []
        for arg in argv:
            if "--settings=" in arg:
                _, settings_module = arg.split("=")
                os.environ["DJANGO_SETTINGS_MODULE"] = settings_module
            elif "--pythonpath=" in arg:
                _, pythonpath = arg.split("=")
                sys.path.insert(0, pythonpath)
            else:
                acc.append(arg)
        return acc

    def die(self, msg):
        sys.stderr.write(msg)
        sys.stderr.write("\n")
        sys.exit()
