from datetime import datetime
from time import time

from anyjson import deserialize
from django.db import transaction

from celery.beat import Scheduler, ScheduleEntry

from djcelery.models import PeriodicTask, PeriodicTasks


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
        self.last_run_at = model.last_run_at

    def next(self):
        self.model.last_run_at = datetime.now()
        self.model.total_run_count += 1
        self.model.no_changes = True
        return self.__class__(self.model)

    def save(self):
        self.model.save()


class DatabaseScheduler(Scheduler):
    Entry = ModelEntry
    Model = PeriodicTask
    Changes = PeriodicTasks
    _schedule = None
    _last_timestamp = None

    def __init__(self, *args, **kwargs):
        Scheduler.__init__(self, *args, **kwargs)
        self.max_interval = 5
        self._dirty = set()
        self._last_flush = None
        self._flush_every = 3 * 60

    def setup_schedule(self):
        pass

    def all_as_schedule(self):
        self.logger.debug("DatabaseScheduler: Fetching database schedule")
        return dict((model.name, self.Entry(model))
                        for model in self.Model.objects.enabled())

    def schedule_changed(self):
        if self._last_timestamp is not None:
            ts = self.Changes.last_change()
            if not ts or ts < self._last_timestamp:
                return False
            self.logger.debug("LAST TIMESTAMP:%s CURRENT: %s" % (
                self._last_timestamp, ts))

        self._last_timestamp = datetime.now()
        return True

    def reserve(self, entry):
        new_entry = Scheduler.reserve(self, entry)
        self._dirty.add(new_entry.name)
        now = time()
        if not self._last_flush or \
                now - self._last_flush > self._flush_every:
            self.logger.debug("Celerybest: Writing schedule changes...")
            self.flush()
            self._last_flush = now
        return new_entry

    @transaction.commit_manually()
    def flush(self):
        if not self._dirty:
            return
        try:
            while self._dirty:
                try:
                    n = self._dirty.pop()
                except KeyError:
                    break
                self[n].save()
        except:
            transaction.rollback()
        else:
            transaction.commit()

    def get_schedule(self):
        if self.schedule_changed():
            self.logger.debug("DatabaseScheduler: Schedule changed.")
            self._schedule = self.all_as_schedule()
        return self._schedule
