import multiprocessing
import atexit

from celery.apps import worker
from celery.signals import worker_ready

# A status variable that the parent thread waits for. Is connected with celery's signal worker_ready
# I did not find a good way to make this variable part of the class, instead of the module.
is_ready = multiprocessing.Event()

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

    def __init__(self):
        self.error = None
        self.is_ready = is_ready

        def at_exit_handler(worker):
            if worker.is_alive():
                worker.terminate()

        atexit.register(at_exit_handler, self)

        super(WorkerInThread, self).__init__()

    def run(self):
        try:
            worker.Worker(concurrency=1, loglevel='DEBUG', pool='solo').run()

        except Exception as e:
            self.error = e
            self.is_ready.set()
            raise

    def start(self):
        super(WorkerInThread, self).start()
        self.is_ready.wait()

@worker_ready.connect
def on_worker_ready(**kwargs):
    is_ready.set()
