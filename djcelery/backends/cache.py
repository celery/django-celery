"""celery.backends.cache"""
from __future__ import absolute_import, unicode_literals

from datetime import timedelta

from django.core.cache import cache, caches

from celery import current_app
from celery.backends.base import KeyValueStoreBackend

# CELERY_CACHE_BACKEND overrides the django-global(tm) backend settings.
if current_app.conf.CELERY_CACHE_BACKEND:
    cache = caches[current_app.conf.CELERY_CACHE_BACKEND]  # noqa


class CacheBackend(KeyValueStoreBackend):
    """Backend using the Django cache framework to store task metadata."""

    def __init__(self, *args, **kwargs):
        super(CacheBackend, self).__init__(*args, **kwargs)
        expires = kwargs.get('expires',
                             current_app.conf.CELERY_TASK_RESULT_EXPIRES)
        if isinstance(expires, timedelta):
            expires = int(max(expires.total_seconds(), 0))
        self.expires = expires

    def get(self, key):
        return cache.get(key)

    def set(self, key, value):
        cache.set(key, value, self.expires)

    def delete(self, key):
        cache.delete(key)
