from celery.task import Task
from celery.registry import tasks


class SomeAppTask(Task):
    name = "c.unittest.SomeAppTask"

    def run(self, **kwargs):
        return 42
