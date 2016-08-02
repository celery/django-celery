from __future__ import absolute_import, unicode_literals

from datetime import datetime
from itertools import count
from time import time

from celery import states
from celery.events import Event as _Event
from celery.events.state import State, Worker, Task
from celery.utils import gen_unique_id

from django.test.utils import override_settings
from django.utils import timezone

from djcelery import celery
from djcelery import snapshot
from djcelery import models
from djcelery.utils import make_aware
from djcelery.tests.utils import unittest
from djcelery.compat import unicode


_ids = count(0)
_clock = count(1)


def Event(*args, **kwargs):
    kwargs.setdefault('clock', next(_clock))
    kwargs.setdefault('local_received', time())
    return _Event(*args, **kwargs)


def create_task(worker, **kwargs):
    d = dict(uuid=gen_unique_id(),
             name='djcelery.unittest.task{0}'.format(next(_ids)),
             worker=worker)
    return Task(**dict(d, **kwargs))


class test_Camera(unittest.TestCase):
    Camera = snapshot.Camera

    def setUp(self):
        self.state = State()
        self.cam = self.Camera(self.state)

    def test_constructor(self):
        cam = self.Camera(State())
        self.assertTrue(cam.state)
        self.assertTrue(cam.freq)
        self.assertTrue(cam.cleanup_freq)
        self.assertTrue(cam.logger)

    def test_get_heartbeat(self):
        worker = Worker(hostname='fuzzie')
        self.assertIsNone(self.cam.get_heartbeat(worker))
        t1 = time()
        t2 = time()
        t3 = time()
        for t in t1, t2, t3:
            worker.event('heartbeat', t, t, {})
        self.state.workers[worker.hostname] = worker
        self.assertEqual(self.cam.get_heartbeat(worker),
                         make_aware(datetime.fromtimestamp(t3)))

    def test_handle_worker(self):
        worker = Worker(hostname='fuzzie')
        worker.event('online', time(), time(), {})
        self.cam._last_worker_write.clear()
        m = self.cam.handle_worker((worker.hostname, worker))
        self.assertTrue(m)
        self.assertTrue(m.hostname)
        self.assertTrue(m.last_heartbeat)
        self.assertTrue(m.is_alive())
        self.assertEqual(unicode(m), unicode(m.hostname))
        self.assertTrue(repr(m))

    def test_handle_task_received(self):
        worker = Worker(hostname='fuzzie')
        worker.event('online', time(), time(), {})
        self.cam.handle_worker((worker.hostname, worker))

        task = create_task(worker)
        task.event('received', time(), time(), {})
        self.assertEqual(task.state, 'RECEIVED')
        mt = self.cam.handle_task((task.uuid, task))
        self.assertEqual(mt.name, task.name)
        self.assertTrue(unicode(mt))
        self.assertTrue(repr(mt))
        mt.eta = celery.now()
        self.assertIn('eta', unicode(mt))
        self.assertIn(mt, models.TaskState.objects.active())

    def test_handle_task(self):
        worker1 = Worker(hostname='fuzzie')
        worker1.event('online', time(), time(), {})
        mw = self.cam.handle_worker((worker1.hostname, worker1))
        task1 = create_task(worker1)
        task1.event('received', time(), time(), {})
        mt = self.cam.handle_task((task1.uuid, task1))
        self.assertEqual(mt.worker, mw)

        worker2 = Worker(hostname=None)
        task2 = create_task(worker2)
        task2.event('received', time(), time(), {})
        mt = self.cam.handle_task((task2.uuid, task2))
        self.assertIsNone(mt.worker)

        task1.event('succeeded', time(), time(), {'result': 42})
        self.assertEqual(task1.state, states.SUCCESS)
        self.assertEqual(task1.result, 42)
        mt = self.cam.handle_task((task1.uuid, task1))
        self.assertEqual(mt.name, task1.name)
        self.assertEqual(mt.result, 42)

        task3 = create_task(worker1, name=None)
        task3.event('revoked', time(), time(), {})
        mt = self.cam.handle_task((task3.uuid, task3))
        self.assertIsNone(mt)

    def test_handle_task_timezone(self):
        worker = Worker(hostname='fuzzie')
        worker.event('online', time(), time(), {})
        self.cam.handle_worker((worker.hostname, worker))

        tstamp = 1464793200.0  # 2016-06-01T15:00:00Z

        with override_settings(USE_TZ=True, TIME_ZONE='Europe/Helsinki'):
            task = create_task(worker,
                               eta='2016-06-01T15:16:17.654321+00:00',
                               expires='2016-07-01T15:16:17.765432+03:00')
            task.event('received', tstamp, tstamp, {})
            mt = self.cam.handle_task((task.uuid, task))
            self.assertEqual(
                mt.tstamp,
                datetime(2016, 6, 1, 15, 0, 0, tzinfo=timezone.utc),
            )
            self.assertEqual(
                mt.eta,
                datetime(2016, 6, 1, 15, 16, 17, 654321, tzinfo=timezone.utc),
            )
            self.assertEqual(
                mt.expires,
                datetime(2016, 7, 1, 12, 16, 17, 765432, tzinfo=timezone.utc),
            )

            task = create_task(worker, eta='2016-06-04T15:16:17.654321')
            task.event('received', tstamp, tstamp, {})
            mt = self.cam.handle_task((task.uuid, task))
            self.assertEqual(
                mt.eta,
                datetime(2016, 6, 4, 15, 16, 17, 654321, tzinfo=timezone.utc),
            )

        with override_settings(USE_TZ=False, TIME_ZONE='Europe/Helsinki'):
            task = create_task(worker,
                               eta='2016-06-01T15:16:17.654321+00:00',
                               expires='2016-07-01T15:16:17.765432+03:00')
            task.event('received', tstamp, tstamp, {})
            mt = self.cam.handle_task((task.uuid, task))
            self.assertEqual(mt.tstamp, datetime(2016, 6, 1, 18, 0, 0))
            self.assertEqual(mt.eta, datetime(2016, 6, 1, 18, 16, 17, 654321))
            self.assertEqual(mt.expires,
                             datetime(2016, 7, 1, 15, 16, 17, 765432))

            task = create_task(worker, eta='2016-06-04T15:16:17.654321')
            task.event('received', tstamp, tstamp, {})
            mt = self.cam.handle_task((task.uuid, task))
            self.assertEqual(mt.eta, datetime(2016, 6, 4, 15, 16, 17, 654321))

    def assertExpires(self, dec, expired, tasks=10):
        # Cleanup leftovers from previous tests
        self.cam.on_cleanup()

        worker = Worker(hostname='fuzzie')
        worker.event('online', time(), time(), {})
        for total in range(tasks):
            task = create_task(worker)
            task.event('received', time() - dec, time() - dec, {})
            task.event('succeeded', time() - dec, time() - dec, {'result': 42})
            self.assertTrue(task.name)
            self.assertTrue(self.cam.handle_task((task.uuid, task)))
        self.assertEqual(self.cam.on_cleanup(), expired)

    def test_on_cleanup_expires(self, dec=332000):
        self.assertExpires(dec, 10)

    def test_on_cleanup_does_not_expire_new(self, dec=0):
        self.assertExpires(dec, 0)

    def test_on_shutter(self):
        state = self.state
        cam = self.cam

        ws = ['worker1.ex.com', 'worker2.ex.com', 'worker3.ex.com']
        uus = [gen_unique_id() for i in range(50)]

        events = [Event('worker-online', hostname=ws[0]),
                  Event('worker-online', hostname=ws[1]),
                  Event('worker-online', hostname=ws[2]),
                  Event('task-received',
                        uuid=uus[0], name='A', hostname=ws[0]),
                  Event('task-started',
                        uuid=uus[0], name='A', hostname=ws[0]),
                  Event('task-received',
                        uuid=uus[1], name='B', hostname=ws[1]),
                  Event('task-revoked',
                        uuid=uus[2], name='C', hostname=ws[2])]

        for event in events:
            event['local_received'] = time()
            state.event(event)
        cam.on_shutter(state)

        for host in ws:
            worker = models.WorkerState.objects.get(hostname=host)
            self.assertTrue(worker.is_alive())

        t1 = models.TaskState.objects.get(task_id=uus[0])
        self.assertEqual(t1.state, 'STARTED')
        self.assertEqual(t1.name, 'A')
        t2 = models.TaskState.objects.get(task_id=uus[1])
        self.assertEqual(t2.state, 'RECEIVED')
        t3 = models.TaskState.objects.get(task_id=uus[2])
        self.assertEqual(t3.state, 'REVOKED')

        events = [Event('task-succeeded',
                        uuid=uus[0], hostname=ws[0], result=42),
                  Event('task-failed',
                        uuid=uus[1], exception="KeyError('foo')",
                        hostname=ws[1]),
                  Event('worker-offline', hostname=ws[0])]
        list(map(state.event, events))
        cam._last_worker_write.clear()
        cam.on_shutter(state)

        w1 = models.WorkerState.objects.get(hostname=ws[0])
        self.assertFalse(w1.is_alive())

        t1 = models.TaskState.objects.get(task_id=uus[0])
        self.assertEqual(t1.state, 'SUCCESS')
        self.assertEqual(t1.result, '42')
        self.assertEqual(t1.worker, w1)

        t2 = models.TaskState.objects.get(task_id=uus[1])
        self.assertEqual(t2.state, 'FAILURE')
        self.assertEqual(t2.result, "KeyError('foo')")
        self.assertEqual(t2.worker.hostname, ws[1])

        cam.on_shutter(state)
