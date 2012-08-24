================
 Unit Testing
================

Testing with Django
-------------------

The first problem you'll run in to when trying to write a test that runs a
task is that Django's test runner doesn't use the same database as your celery
daemon is using. If you're using the database backend, this means that your
tombstones won't show up in your test database and you won't be able to
get the return value or check the status of your tasks.

There are two ways to get around this. You can either take advantage of
``CELERY_ALWAYS_EAGER = True`` to skip the daemon, or you can avoid testing
anything that needs to check the status or result of a task.

Using a custom test runner to test with celery
----------------------------------------------

If you're going the ``CELERY_ALWAYS_EAGER`` route, which is probably better than
just never testing some parts of your app, a custom Django test runner does the
trick. Celery provides two simple test runner classes, but it's easy enough
to roll your own if you have other things that need to be done.
http://docs.djangoproject.com/en/dev/topics/testing/#defining-a-test-runner

``CeleryTestSuiteRunner`` eagerly runs all tasks in tests, but result is not stored anywhere.
``CeleryTestSuiteRunnerStoringResult`` --- this test runner in addition stores
result of task execution or failure in ``djcelery.models.TaskState`` model,
likewise django-celery does during normal operation when workers
and ``celerycam`` are launched.

For this example, we'll use the ``djcelery.contrib.test_runner`` to test the
``add`` task from the `User Guide: Tasks`_ examples in the Celery
documentation.

.. _`User Guide: Tasks`: http://docs.celeryq.org/en/latest/userguide/tasks.html

To enable the test runner, set the following settings:

.. code-block:: python

    TEST_RUNNER = 'djcelery.contrib.test_runner.' \
        'CeleryTestSuiteRunnerStoringResult'

Then we can put the tests in a ``tests.py`` somewhere:

.. code-block:: python

    from django.test import TestCase
    from djcelery.models import TaskState
    from myapp.tasks import add

    class AddTestCase(TestCase):

        def testNoError(self):
            """Test that the ``add`` task runs with no errors,
            and returns the correct result."""
            result = add.delay(8, 8)

            self.assertEquals(result.get(), 16)
            self.assertTrue(result.successful())

            # Run another task
            add.delay(4, 4)

            # Assert we have 2 task results in the test database
            self.assertEqual(TaskState.objects.count(), 2)

            # Assert results
            self.assertEqual([task_state.result for task_state
                              in TaskState.objects.all()], [16, 8])

This test assumes that you put your example ``add`` task in ``maypp.tasks``
so adjust the import for wherever you put the class.

If you're  going to use
``'djcelery.contrib.test_runner.CeleryTestSuiteRunnerStoringResult``
then if your task will raise exception it will propagate through.
If you need to test ``on_failure`` behavior of your task,
set ``settings.CELERY_EAGER_PROPAGATES_EXCEPTIONS`` to ``False``:

.. code-block:: python

    settings.CELERY_EAGER_PROPAGATES_EXCEPTIONS = False
