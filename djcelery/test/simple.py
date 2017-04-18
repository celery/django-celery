from django.conf import settings
from django.test.simple import DjangoTestSuiteRunner as DjangoTestSuiteRunnerBase

USAGE = """\
Custom test runner to allow testing of celery delayed tasks.
"""

class DjangoTestSuiteRunner(DjangoTestSuiteRunnerBase):
    """Django test runner allowing testing of celery delayed tasks.

    All tasks are run locally, not in a worker.

    To use this runner set ``settings.TEST_RUNNER``::

        TEST_RUNNER = "djcelery.contrib.test_runner.DjangoTestSuiteRunner"

    """
    def __init__(self, *args, **kwargs):
        settings.CELERY_ALWAYS_EAGER = True
        super(DjangoTestSuiteRunner, self).__init__(*args, **kwargs)