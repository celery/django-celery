import multiprocessing
import atexit

from celery.apps import worker
from celery.signals import worker_ready

class WorkerInThread(multiprocessing.Process):
    """
    Class for running a worker in a thread

    Will not work with an in-memory SQLite3 database, which means you have to add "TEST_NAME" 
    to the DATABASES configuration.

    However Django has a working implementation of a shared SQLite3 database in its LiveServerTestCase,
    but I have failed trying to get that to work with Celery.

    If this was to work, the setup and teardown of the tests would speed up significantly.
    """

    daemon = True
    is_ready = None

    def __init__(self):
        self.error = None
        self.is_ready = multiprocessing.Event()

        def at_exit_handler(worker):
            if worker.is_alive():
                worker.terminate()
        atexit.register(at_exit_handler, self)

        super(WorkerInThread, self).__init__()

    def run(self):
        try:
            threaded_worker = self
            def on_worker_ready(*args, **kwargs):
                threaded_worker.is_ready.set()
            worker_ready.connect(on_worker_ready)

            worker.Worker(concurrency=1, loglevel='WARN', pool_cls='solo').run()

        except Exception as e:
            self.error = e
            self.is_ready.set()
            raise

    def start(self):
        super(WorkerInThread, self).start()
        self.is_ready.wait()
