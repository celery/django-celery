import sys

from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.test.testcases import TestCase as DjangoTestCase
from django.template import TemplateDoesNotExist

from anyjson import deserialize

from celery import conf
from celery import states
from celery.backends import default_backend
from celery.exceptions import RetryTaskError
from celery.datastructures import ExceptionInfo
from celery.decorators import task
from celery.utils import gen_unique_id, get_full_cls_name
from celery.utils.functional import curry

from djcelery.views import task_webhook
from djcelery.tests.req import MockRequest


def reversestar(name, **kwargs):
    return reverse(name, kwargs=kwargs)


task_is_successful = curry(reversestar, "celery-is_task_successful")
task_status = curry(reversestar, "celery-task_status")
task_apply = curry(reverse, "celery-apply")
registered_tasks = curry(reverse, "celery-tasks")
scratch = {}


@task()
def mytask(x, y):
    ret = scratch["result"] = int(x) * int(y)
    return ret


def create_exception(name, base=Exception):
    return type(name, (base, ), {})


def catch_exception(exception):
    try:
        raise exception
    except exception.__class__, exc:
        exc = default_backend.prepare_exception(exc)
        return exc, ExceptionInfo(sys.exc_info()).traceback


class ViewTestCase(DjangoTestCase):

    def assertJSONEqual(self, json, py):
        json = isinstance(json, HttpResponse) and json.content or json
        try:
            self.assertEqual(deserialize(json), py)
        except TypeError, exc:
            raise TypeError("%s: %s" % (exc, json))

    def assertIn(self, expected, source, *args):
        try:
            DjangoTestCase.assertIn(self, expected, source, *args)
        except AttributeError:
            self.assertTrue(expected in source)

    def assertDictContainsSubset(self, a, b, *args):
        try:
            DjangoTestCase.assertDictContainsSubset(self, a, b, *args)
        except AttributeError:
            for key, value in a.items():
                self.assertTrue(key in b)
                self.assertEqual(b[key], value)


class test_task_apply(ViewTestCase):

    def test_apply(self):
        conf.ALWAYS_EAGER = True
        try:
            self.client.get(task_apply(kwargs={"task_name":
                mytask.name}) + "?x=4&y=4")
            self.assertEqual(scratch["result"], 16)
        finally:
            conf.ALWAYS_EAGER = False

    def test_apply_raises_404_on_unregistered_task(self):
        conf.ALWAYS_EAGER = True
        try:
            name = "xxx.does.not.exist"
            action = curry(self.client.get, task_apply(kwargs={
                        "task_name": name}) + "?x=4&y=4")
            self.assertRaises(TemplateDoesNotExist, action)
        finally:
            conf.ALWAYS_EAGER = False


class test_registered_tasks(ViewTestCase):

    def test_list_registered_tasks(self):
        json = self.client.get(registered_tasks())
        tasks = deserialize(json.content)
        self.assertIn("celery.ping", tasks["regular"])


class test_webhook_task(ViewTestCase):

    def test_successful_request(self):

        @task_webhook
        def add_webhook(request):
            x = int(request.GET["x"])
            y = int(request.GET["y"])
            return x + y

        request = MockRequest().get("/tasks/add", dict(x=10, y=10))
        response = add_webhook(request)
        self.assertDictContainsSubset({"status": "success", "retval": 20},
                                      deserialize(response.content))

    def test_failed_request(self):

        @task_webhook
        def error_webhook(request):
            x = int(request.GET["x"])
            y = int(request.GET["y"])
            raise KeyError(x + y)

        request = MockRequest().get("/tasks/error", dict(x=10, y=10))
        response = error_webhook(request)
        self.assertDictContainsSubset({"status": "failure",
                                       "reason": "20"},
                                      deserialize(response.content))


class test_task_status(ViewTestCase):

    def assertStatusForIs(self, status, res, traceback=None):
        uuid = gen_unique_id()
        default_backend.store_result(uuid, res, status,
                                     traceback=traceback)
        json = self.client.get(task_status(task_id=uuid))
        expect = dict(id=uuid, status=status, result=res)
        if status in default_backend.EXCEPTION_STATES:
            instore = default_backend.get_result(uuid)
            self.assertEqual(str(instore.args), str(res.args))
            expect["result"] = repr(res)
            expect["exc"] = get_full_cls_name(res.__class__)
            expect["traceback"] = traceback

        self.assertJSONEqual(json, dict(task=expect))

    def test_success(self):
        self.assertStatusForIs(states.SUCCESS, "The quick brown fox")

    def test_failure(self):
        exc, tb = catch_exception(KeyError("foo"))
        self.assertStatusForIs(states.FAILURE, exc, tb)

    def test_retry(self):
        oexc, _ = catch_exception(KeyError("Resource not available"))
        exc, tb = catch_exception(RetryTaskError(str(oexc), oexc))
        self.assertStatusForIs(states.RETRY, exc, tb)


class test_task_is_successful(ViewTestCase):

    def assertStatusForIs(self, status, outcome):
        uuid = gen_unique_id()
        result = gen_unique_id()
        default_backend.store_result(uuid, result, status)
        json = self.client.get(task_is_successful(task_id=uuid))
        self.assertJSONEqual(json, {"task": {"id": uuid,
                                             "executed": outcome}})

    def test_success(self):
        self.assertStatusForIs(states.SUCCESS, True)

    def test_pending(self):
        self.assertStatusForIs(states.PENDING, False)

    def test_failure(self):
        self.assertStatusForIs(states.FAILURE, False)

    def test_retry(self):
        self.assertStatusForIs(states.RETRY, False)
