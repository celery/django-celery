import unittest2 as unittest

from celery import loaders

from djcelery.loaders import djangoapp


class TestDjangoLoader(unittest.TestCase):

    def setUp(self):
        self.loader = djangoapp.Loader()

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
        djangoapp._RACE_PROTECTION = True
        try:
            self.assertFalse(self.loader.on_worker_init())
        finally:
            djangoapp._RACE_PROTECTION = False

    def test_find_related_module_no_path(self):
        self.assertFalse(djangoapp.find_related_module("sys", "tasks"))

    def test_find_related_module_no_related(self):
        self.assertFalse(djangoapp.find_related_module("someapp",
                                                       "frobulators"))
