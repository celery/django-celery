import imp
import importlib

from celery.loaders.base import BaseLoader

_RACE_PROTECTION = False


class DjangoLoader(BaseLoader):
    """The Django loader."""
    _db_reuse = 0

    override_backends = {
            "database": "djcelery.backends.database.DatabaseBackend",
            "cache": "djcelery.backends.cache.CacheBackend"}

    def read_configuration(self):
        """Load configuration from Django settings."""
        from django.conf import settings
        self.configured = True
        return settings

    def on_task_init(self, task_id, task):
        self.close_database()

    def close_database(self):
        from django.db import connection
        db_reuse_max = getattr(self.conf, "CELERY_DB_REUSE_MAX", None)
        if not db_reuse_max:
            return connection.close()
        if self._db_reuse >= db_reuse_max * 2:
            self._db_reuse = 0
            return connection.close()
        self._db_reuse += 1

    def on_process_cleanup(self):
        """Does everything necessary for Django to work in a long-living,
        multiprocessing environment.

        """
        # See http://groups.google.com/group/django-users/
        #            browse_thread/thread/78200863d0c07c6d/
        self.close_database()

        # ## Reset cache connection (if supported).
        try:
            cache.cache.close()
        except AttributeError:
            pass

    def on_worker_init(self):
        """Called when the worker starts.

        Automatically discovers any ``tasks.py`` files in the applications
        listed in ``INSTALLED_APPS``.

        """
        self.import_default_modules()
        autodiscover()


def autodiscover():
    """Include tasks for all applications in ``INSTALLED_APPS``."""
    from django.conf import settings
    global _RACE_PROTECTION

    if _RACE_PROTECTION:
        return
    _RACE_PROTECTION = True
    try:
        return filter(None, [find_related_module(app, "tasks")
                                for app in settings.INSTALLED_APPS])
    finally:
        _RACE_PROTECTION = False


def find_related_module(app, related_name):
    """Given an application name and a module name, tries to find that
    module in the application."""

    try:
        app_path = importlib.import_module(app).__path__
    except AttributeError:
        return

    try:
        imp.find_module(related_name, app_path)
    except ImportError:
        return

    module = importlib.import_module("%s.%s" % (app, related_name))

    try:
        return getattr(module, related_name)
    except AttributeError:
        return
