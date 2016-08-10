# -- XXX This module must not use translation as that causes
# -- a recursive loader import!
from __future__ import absolute_import, unicode_literals

from datetime import datetime

from django.conf import settings
from django.utils import timezone

# Database-related exceptions.
from django.db import DatabaseError
try:
    import MySQLdb as mysql
    _my_database_errors = (mysql.DatabaseError,
                           mysql.InterfaceError,
                           mysql.OperationalError)
except ImportError:
    _my_database_errors = ()      # noqa
try:
    import psycopg2 as pg
    _pg_database_errors = (pg.DatabaseError,
                           pg.InterfaceError,
                           pg.OperationalError)
except ImportError:
    _pg_database_errors = ()      # noqa
try:
    import sqlite3
    _lite_database_errors = (sqlite3.DatabaseError,
                             sqlite3.InterfaceError,
                             sqlite3.OperationalError)
except ImportError:
    _lite_database_errors = ()    # noqa
try:
    import cx_Oracle as oracle
    _oracle_database_errors = (oracle.DatabaseError,
                               oracle.InterfaceError,
                               oracle.OperationalError)
except ImportError:
    _oracle_database_errors = ()  # noqa

DATABASE_ERRORS = ((DatabaseError, ) +
                   _my_database_errors +
                   _pg_database_errors +
                   _lite_database_errors +
                   _oracle_database_errors)


def make_aware(value):
    if settings.USE_TZ:
        # naive datetimes are assumed to be in UTC.
        if timezone.is_naive(value):
            value = timezone.make_aware(value, timezone.utc)
        # then convert to the Django configured timezone.
        default_tz = timezone.get_default_timezone()
        value = timezone.localtime(value, default_tz)
    return value


def make_naive(value):
    if settings.USE_TZ:
        default_tz = timezone.get_default_timezone()
        value = timezone.make_naive(value, default_tz)
    return value


def now():
    return make_aware(timezone.now())


def correct_awareness(value):
    if isinstance(value, datetime):
        if settings.USE_TZ:
            return make_aware(value)
        elif timezone.is_aware(value):
            default_tz = timezone.get_default_timezone()
            return timezone.make_naive(value, default_tz)
    return value


def is_database_scheduler(scheduler):
    if not scheduler:
        return False
    from kombu.utils import symbol_by_name
    from .schedulers import DatabaseScheduler
    return issubclass(symbol_by_name(scheduler), DatabaseScheduler)


def fromtimestamp(value):
    if settings.USE_TZ:
        return make_aware(datetime.utcfromtimestamp(value))
    else:
        return datetime.fromtimestamp(value)
