from django.conf import settings
from django.test.simple import DjangoTestSuiteRunner

USAGE = """\
Custom test runner to allow testing of celery delayed tasks.
"""


class DjangoCeleryTestSuiteRunner(DjangoTestSuiteRunner):
    def run_tests(self, test_labels, *args, **kwargs):
        """Django test runner allowing testing of celery delayed tasks.

        All tasks are run locally, not in a worker.

        To use this runner set ``settings.TEST_RUNNER``::

            TEST_RUNNER = "celery.contrib.test_runner.DjangoCeleryTestSuiteRunner"

        """
        settings.CELERY_ALWAYS_EAGER = True
        return super(DjangoCeleryTestSuiteRunner, self).run_tests(test_labels, *args, **kwargs)
