from datetime import datetime

from anyjson import deserialize

from celery.beat import Scheduler, ScheduleEntry

from djcelery.models import PeriodicTask


class ModelEntry(ScheduleEntry):

    def __init__(self, model):
        self.name = model.task
        self.schedule = model.schedule
        self.args = deserialize(model.args)
        self.kwargs = deserialize(model.kwargs)
        self.options = {"queue": model.queue,
                        "exchange": model.exchange,
                        "routing_key": model.routing_key,
                        "expires": model.expires}
        self.total_run_count = model.total_run_count
        self.model = model

        if not model.last_run_at:
            model.last_run_at = datetime.now()
            model.save()
        self.last_run_at = model.last_run_at

    def next(self):
        self.model.last_run_at = datetime.now()
        self.model.total_run_count += 1
        self.model.save()
        return self.__class__(self.model)


class DatabaseScheduler(Scheduler):
    Entry = ModelEntry
    Model = PeriodicTask

    def setup_schedule(self):
        pass

    def all_as_schedule(self):
        return dict((model.name, self.Entry(model))
                        for model in self.Model.objects.filter(enabled=True))

    @property
    def schedule(self):
        return self.all_as_schedule()

