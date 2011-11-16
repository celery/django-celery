from __future__ import absolute_import

import os
import sys

DEFAULT_APPS = ("django.contrib.auth",
                "django.contrib.contenttypes",
                "django.contrib.sessions",
                "django.contrib.sites",
                "django.contrib.admin",
                "django.contrib.admindocs",
                "djcelery")

DEFAULTS = {"ROOT_URLCONF": "djcelery.monproj.urls",
            "DATABASE_ENGINE": "sqlite3",
            "DATABASE_NAME": "djcelerymon.db",
            "BROKER_HOST": "localhost",
            "BROKER_USER": "guest",
            "BROKER_PASSWORD": "guest",
            "BROKER_VHOST": "/",
            "SITE_ID": 1,
            "INSTALLED_APPS": DEFAULT_APPS,
            "DEBUG": True}


def configure():
    from celery import current_app
    from django.conf import settings

    if not settings.configured:
        settings_module = os.environ.get("CELERY_CONFIG_MODULE",
                                         "celeryconfig")
        settings.configure(SETTINGS_MODULE=settings_module,
                           **dict(DEFAULTS, **current_app.loader.conf))
        settings.DEBUG = True


def run_monitor(argv):
    from .management.commands import djcelerymon
    djcelerymon.Command().run_from_argv([argv[0], "djcelerymon"] + argv[1:])


def main(argv=sys.argv):
    from django.core import management
    os.environ["CELERY_LOADER"] = "default"
    configure()
    management.call_command("syncdb")
    run_monitor(argv)

if __name__ == "__main__":
    main()
