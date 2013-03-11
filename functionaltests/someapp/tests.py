from someapp.tasks import FunctionalAddTask

from utils import WorkerInThread

def test_worker_in_thread():
    worker = WorkerInThread()
    worker.start()

    result = FunctionalAddTask.apply_async(args=(2,2))
    computation = result.get(timeout=60)
    assert computation == 4, "Was not the expected result"
    worker.terminate()
