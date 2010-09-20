from django.core.management.base import BaseCommand

import celery
import djcelery


class CeleryCommand(BaseCommand):

    def get_version(self):
        return "celery %s\ndjango-celery %s" % (celery.__version__,
                                                djcelery.__version__)
