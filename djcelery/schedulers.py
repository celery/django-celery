import logging

from datetime import datetime
from time import time

from anyjson import deserialize, serialize
from django.db import transaction

from celery import schedules
from celery.beat import Scheduler, ScheduleEntry

from djcelery.models import (PeriodicTask, PeriodicTasks,
                             CrontabSchedule, IntervalSchedule)


class ModelEntry(ScheduleEntry):
    model_schedules = ((schedules.crontab, CrontabSchedule, "crontab"),
                       (schedules.schedule, IntervalSchedule, "interval"))
    save_fields = ["last_run_at", "total_run_count", "no_changes"]

    def __init__(self, model):
        self.name = model.name
        self.task = model.task
        self.schedule = model.schedule
        try:
            self.args = deserialize(model.args or u"[]")
            self.kwargs = deserialize(model.kwargs or u"{}")
        except ValueError:
            # disable because of error deserializing args/kwargs
            model.no_changes = True
            model.enabled = False
            model.save()
            raise

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
        # Object may not be synchronized, so only
        # change the fields we care about.
        obj = self.model._default_manager.get(pk=self.model.pk)
        for field in self.save_fields:
            setattr(obj, field, getattr(self.model, field))
        obj.save()

    @classmethod
    def to_model_schedule(cls, schedule):
        for schedule_type, model_type, model_field in cls.model_schedules:
            if isinstance(schedule, schedule_type):
                model_schedule = model_type.from_schedule(schedule)
                model_schedule.save()
                return model_schedule, model_field
        raise ValueError("Can't convert schedule type %r to model" % schedule)

    @classmethod
    def from_entry(cls, name, skip_fields=("relative", "options"), **entry):
        fields = dict(entry)
        for skip_field in skip_fields:
            fields.pop(skip_field, None)
        schedule = fields.pop("schedule")
        model_schedule, model_field = cls.to_model_schedule(schedule)
        fields[model_field] = model_schedule
        fields["args"] = serialize(fields.get("args") or [])
        fields["kwargs"] = serialize(fields.get("kwargs") or {})
        return cls(PeriodicTask._default_manager.update_or_create(name=name,
                                                            defaults=fields))

    def __repr__(self):
        return "<ModelEntry: %s %s(*%s, **%s) {%s}" % (self.name,
                                                        self.task,
                                                        self.args,
                                                        self.kwargs,
                                                        self.schedule)


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
        s = {}
        for model in self.Model.objects.enabled():
            try:
                s[model.name] = self.Entry(model)
            except ValueError:
                pass
        return s

    def schedule_changed(self):
        if self._last_timestamp is not None:
            ts = self.Changes.last_change()
            if not ts or ts < self._last_timestamp:
                return False

        self._last_timestamp = datetime.now()
        return True

    def should_flush(self):
        return not self._last_flush or \
                    (time() - self._last_flush) > self._flush_every

    def reserve(self, entry):
        new_entry = Scheduler.reserve(self, entry)
        # Need to story entry by name, because the entry may change
        # in the mean time.
        self._dirty.add(new_entry.name)
        if self.should_flush():
            self.logger.debug("Celerybeat: Writing schedule changes...")
            self.flush()
        return new_entry

    @transaction.commit_manually()
    def flush(self):
        self.logger.debug("Writing dirty entries...")
        if not self._dirty:
            return
        try:
            while self._dirty:
                try:
                    name = self._dirty.pop()
                    self.schedule[name].save()
                except KeyError:
                    continue
        except:
            transaction.rollback()
            raise
        else:
            transaction.commit()
            self._last_flush = time()

    def update_from_dict(self, dict_):
        s = {}
        for name, entry in dict_.items():
            try:
                s[name] = self.Entry.from_entry(name, **entry)
            except Exception, exc:
                self.logger.error(
                    "Couldn't add entry %r to database schedule: %r. "
                    "Contents: %r" % (name, exc, entry))
        self.schedule.update(s)

    def get_schedule(self):
        if self.schedule_changed():
            self.flush()
            self.logger.debug("DatabaseScheduler: Schedule changed.")
            self._schedule = self.all_as_schedule()
            if self.logger.isEnabledFor(logging.DEBUG):
                self.logger.debug(
                        "Current schedule:\n" +
                        "\n".join(repr(entry)
                                    for entry in self._schedule.values()))
        return self._schedule
