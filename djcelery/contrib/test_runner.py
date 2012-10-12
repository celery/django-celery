from __future__ import absolute_import, unicode_literals

from django.conf import settings
from django.test.simple import DjangoTestSuiteRunner

from djcelery.backends.database import DatabaseBackend
from celery.task import Task


USAGE = """\
Custom test runner to allow testing of celery delayed tasks.
"""


class CeleryTestSuiteRunner(DjangoTestSuiteRunner):
    """Django test runner allowing testing of celery delayed tasks.

    All tasks are run locally, not in a worker.

    To use this runner set ``settings.TEST_RUNNER``::

        TEST_RUNNER = 'djcelery.contrib.test_runner.CeleryTestSuiteRunner'

    """
    def setup_test_environment(self, **kwargs):
        super(CeleryTestSuiteRunner, self).setup_test_environment(**kwargs)
        settings.CELERY_ALWAYS_EAGER = True
        settings.CELERY_EAGER_PROPAGATES_EXCEPTIONS = True  # Issue #75


class CeleryTestSuiteRunnerStoringResult(DjangoTestSuiteRunner):
    """Django test runner allowing testing of celery delayed tasks,
    and storing the results of those tasks in ``TaskMeta``.

    Requires setting CELERY_RESULT_BACKEND = 'database'.

    USAGE:

    In ``settings.py``::

        TEST_RUNNER = '''
            djcelery.contrib.test_runner.CeleryTestSuiteRunnerStoringResult
        '''.strip()

    """

    def setup_test_environment(self, **kwargs):
        # Monkey-patch Task.on_success() method
        def on_success_patched(self, retval, task_id, args, kwargs):
            DatabaseBackend().store_result(task_id, retval, 'SUCCESS')
        Task.on_success = classmethod(on_success_patched)

        super(CeleryTestSuiteRunnerStoringResult, self).setup_test_environment(
            **kwargs
        )

        settings.CELERY_RESULT_BACKEND = 'database'
        settings.CELERY_ALWAYS_EAGER = True
        settings.CELERY_EAGER_PROPAGATES_EXCEPTIONS = True  # Issue #75
