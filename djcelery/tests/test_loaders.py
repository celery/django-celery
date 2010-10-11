from celery import loaders

from djcelery import loaders as djloaders
from djcelery.tests.utils import unittest


class TestDjangoLoader(unittest.TestCase):

    def setUp(self):
        self.loader = djloaders.DjangoLoader()

    def test_get_loader_cls(self):

        self.assertEqual(loaders.get_loader_cls("django"),
                          self.loader.__class__)
        # Execute cached branch.
        self.assertEqual(loaders.get_loader_cls("django"),
                          self.loader.__class__)

    def test_on_worker_init(self):
        from django.conf import settings
        old_imports = getattr(settings, "CELERY_IMPORTS", None)
        settings.CELERY_IMPORTS = ("xxx.does.not.exist", )
        try:
            self.assertRaises(ImportError, self.loader.on_worker_init)
        finally:
            settings.CELERY_IMPORTS = old_imports

    def test_race_protection(self):
        djloaders._RACE_PROTECTION = True
        try:
            self.assertFalse(self.loader.on_worker_init())
        finally:
            djloaders._RACE_PROTECTION = False

    def test_find_related_module_no_path(self):
        self.assertFalse(djloaders.find_related_module("sys", "tasks"))

    def test_find_related_module_no_related(self):
        self.assertFalse(djloaders.find_related_module("someapp",
                                                       "frobulators"))

    def test_close_database(self):

        class Connection(object):
            closed = False

            def close(self):
                self.closed = True

        def with_db_reuse_max(reuse_max, fun):
            prev = getattr(self.loader.conf, "CELERY_DB_REUSE_MAX", None)
            from django import db
            prev_conn = db.connection
            self.loader.conf.CELERY_DB_REUSE_MAX = reuse_max
            conn = db.connection = Connection()
            try:
                fun(conn)
                return conn
            finally:
                self.loader.conf.CELERY_DB_REUSE_MAX = prev
                db.connection = prev_conn

        def test_max_3(conn):
            for i in range(3 * 2):
                self.loader.close_database()
                self.assertFalse(conn.closed)
            self.loader.close_database()
            self.assertTrue(conn.closed)

        def test_max_None(conn):
            self.loader.close_database()
            self.assertTrue(conn.closed)

        with_db_reuse_max(3, test_max_3)
        with_db_reuse_max(None, test_max_None)
