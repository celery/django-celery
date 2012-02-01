from __future__ import absolute_import

import os
import sys
import types

DEFAULT_APPS = ("django.contrib.auth",
                "django.contrib.contenttypes",
                "django.contrib.sessions",
                "django.contrib.admin",
                "django.contrib.admindocs",
                "djcelery")

DEFAULTS = {"ROOT_URLCONF": "djcelery.monproj.urls",
            "DATABASE_ENGINE": "sqlite3",
            "DATABASE_NAME": "djcelerymon.db",
            "DATABASES": {"default": {
                            "ENGINE": "django.db.backends.sqlite3",
                            "NAME": "djcelerymon.db"}},
            "BROKER_URL": "amqp://",
            "SITE_ID": 1,
            "INSTALLED_APPS": DEFAULT_APPS,
            "DEBUG": False}


def default_settings(name="__default_settings__"):
    c = type(name, (types.ModuleType, ), DEFAULTS)(name)
    c.__dict__.update({"__file__": __file__})
    sys.modules[name] = c
    return name


def configure():
    from celery import current_app
    from celery.loaders.default import DEFAULT_CONFIG_MODULE
    from django.conf import settings

    if not settings.configured:
        if current_app.loader.configured:
            settings_module = os.environ.get("CELERY_CONFIG_MODULE",
                                             DEFAULT_CONFIG_MODULE)
        else:
            settings_module = default_settings()
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
