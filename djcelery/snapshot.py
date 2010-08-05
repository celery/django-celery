from datetime import datetime

from celery.events.snapshot import Polaroid
from celery.events.state import Worker
from celery.utils import maybe_iso8601

from djcelery.models import WorkerState, TaskState


class Camera(Polaroid):

    def handle_worker(self, (hostname, worker)):
        return WorkerState.objects.update_or_create(hostname=hostname,
                    defaults={"last_heartbeat":
                            datetime.fromtimestamp(worker.heartbeats[-1])})

    def handle_task(self, (uuid, task), worker=None):
        if task.worker.hostname:
            worker = self.handle_worker((task.worker.hostname, task.worker))
        return TaskState.objects.update_or_create(task_id=uuid,
                defaults={"name": task.name,
                          "args": task.args,
                          "kwargs": task.kwargs,
                          "eta": maybe_iso8601(task.eta),
                          "expires": maybe_iso8601(task.expires),
                          "state": task.state,
                          "timestamp": datetime.fromtimestamp(task.timestamp),
                          "result": task.result or task.exception,
                          "traceback": task.traceback,
                          "runtime": task.runtime,
                          "worker": worker})

    def on_shutter(self, state):
        map(self.handle_worker, state.workers.items())
        map(self.handle_task, state.tasks.items())
