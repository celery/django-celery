"""

Start detached worker node from the Django management utility.

"""
import os
import sys

from celery.bin import celeryd_multi

from djcelery.management.base import CeleryCommand


class Command(CeleryCommand):
    """Run the celery daemon."""
    args = "[name1, [name2, [...]> [worker options]"
    help = "Manage multiple Celery worker nodes."
    requires_model_validation = True
    option_list = ()

    def run_from_argv(self, argv):
        argv.append("--cmd=%s celeryd_detach" % (argv[0], ))
        celeryd_multi.MultiTool()(argv[2:])
