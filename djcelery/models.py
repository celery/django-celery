from datetime import datetime, timedelta
from time import time, mktime

import django

from django.db import models
from django.db.models import signals
from django.utils.translation import ugettext_lazy as _

from picklefield.fields import PickledObjectField

from celery import conf
from celery import schedules
from celery import states
from celery.registry import tasks
from celery.utils.timeutils import timedelta_seconds

from djcelery.managers import TaskManager, TaskSetManager, ExtendedManager
from djcelery.managers import TaskStateManager, PeriodicTaskManager

HEARTBEAT_EXPIRE = 150 # 2 minutes, 30 seconds
TASK_STATE_CHOICES = zip(states.ALL_STATES, states.ALL_STATES)


class TaskMeta(models.Model):
    """Task result/status."""
    task_id = models.CharField(_(u"task id"), max_length=255, unique=True)
    status = models.CharField(_(u"task status"), max_length=50,
            default=states.PENDING, choices=TASK_STATE_CHOICES)
    result = PickledObjectField(null=True, default=None)
    date_done = models.DateTimeField(_(u"done at"), auto_now=True)
    traceback = models.TextField(_(u"traceback"), blank=True, null=True)

    objects = TaskManager()

    class Meta:
        """Model meta-data."""
        verbose_name = _(u"task meta")
        verbose_name_plural = _(u"task meta")
        db_table = "celery_taskmeta"

    def to_dict(self):
        return {"task_id": self.task_id,
                "status": self.status,
                "result": self.result,
                "date_done": self.date_done,
                "traceback": self.traceback}

    def __unicode__(self):
        return u"<Task: %s state->%s>" % (self.task_id, self.status)


class TaskSetMeta(models.Model):
    """TaskSet result"""
    taskset_id = models.CharField(_(u"task id"), max_length=255, unique=True)
    result = PickledObjectField()
    date_done = models.DateTimeField(_(u"done at"), auto_now=True)

    objects = TaskSetManager()

    class Meta:
        """Model meta-data."""
        verbose_name = _(u"taskset meta")
        verbose_name_plural = _(u"taskset meta")
        db_table = "celery_tasksetmeta"

    def to_dict(self):
        return {"taskset_id": self.taskset_id,
                "result": self.result,
                "date_done": self.date_done}

    def __unicode__(self):
        return u"<TaskSet: %s>" % (self.taskset_id)


PERIOD_CHOICES = (("days", _(u"Days")),
                  ("hours", _(u"Hours")),
                  ("minutes", _(u"Minutes")),
                  ("seconds", _(u"Seconds")),
                  ("microseconds", _(u"Microseconds")))


def get_task_choices():
    t = tasks.regular()
    return zip(t.keys(), t.keys())


class IntervalSchedule(models.Model):
    every = models.IntegerField(_(u"every"), null=False)
    period = models.CharField(_(u"period"), max_length=24,
                                            choices=PERIOD_CHOICES)

    class Meta:
        verbose_name = _(u"interval")
        verbose_name_plural = _(u"intervals")

    @property
    def schedule(self):
        return schedules.schedule(timedelta(**{self.period: self.every}))

    @classmethod
    def from_schedule(cls, schedule):
        return cls(every=timedelta_seconds(schedule.run_every),
                   period="seconds")

    def __unicode__(self):
        if self.every == 1:
            return _(u"every %s") % self.period[:-1]
        return _(u"every %s %s") % (self.every, self.period)


class CrontabSchedule(models.Model):
    minute = models.CharField(_(u"minute"),
                        max_length=64,
                        default="*")
    hour = models.CharField(_(u"hour"),
                        max_length=64,
                        default="*")
    day_of_week = models.CharField(_(u"day of week"),
                        max_length=64,
                        default="*")

    class Meta:
        verbose_name = _(u"crontab")
        verbose_name_plural = _(u"crontabs")

    def __unicode__(self):
        rfield = lambda f: f and str(f).replace(" ", "") or "*"
        return u"%s %s %s (m/h/d)" % (rfield(self.minute),
                                      rfield(self.hour),
                                      rfield(self.day_of_week))

    @property
    def schedule(self):
        return schedules.crontab(minute=self.minute,
                                hour=self.hour,
                                day_of_week=self.day_of_week)

    @classmethod
    def from_schedule(cls, schedule):
        return cls(minute=schedule._orig_minute,
                   hour=schedule._orig_hour,
                   day_of_week=schedule._orig_day_of_week)


class PeriodicTasks(models.Model):
    ident = models.SmallIntegerField(default=1, primary_key=True, unique=True)
    last_update = models.DateTimeField(null=False)

    objects = ExtendedManager()

    @classmethod
    def changed(cls, instance, **kwargs):
        if not instance.no_changes:
            now = datetime.now()
            cls.objects.update_or_create(ident=1,
                                         defaults={"last_update": now})

    @classmethod
    def last_change(cls):
        try:
            return cls.objects.get(ident=1).last_update
        except cls.DoesNotExist:
            pass


class PeriodicTask(models.Model):
    name = models.CharField(_(u"name"), max_length=200, unique=True,
                            help_text=_(u"Useful description"))
    task = models.CharField(_(u"task name"),
                            max_length=200,
                            choices=get_task_choices())
    interval = models.ForeignKey(IntervalSchedule, null=True, blank=True,
                                 verbose_name=_(u"interval"))
    crontab = models.ForeignKey(CrontabSchedule, null=True, blank=True,
                                verbose_name=_(u"crontab"),
                                help_text=_(u"Use one of interval/schedule"))
    args = models.TextField(_(u"Arguments"),
                            blank=True, default="[]",
                            help_text=_(u"JSON encoded positional arguments"))
    kwargs = models.TextField(_(u"Keyword arguments"),
                              blank=True, default="{}",
                              help_text=_("JSON encoded keyword arguments"))
    queue = models.CharField(_("queue"),
                             max_length=200, blank=True,
                             null=True, default=None,
                             help_text=_(u"Queue defined in CELERY_QUEUES"))
    exchange = models.CharField(_(u"exchange"),
                              max_length=200, blank=True,
                              null=True, default=None)
    routing_key = models.CharField(_(u"routing key"),
                              max_length=200, blank=True,
                              null=True, default=None)
    expires = models.DateTimeField(_(u"expires"),
                              blank=True, null=True)
    enabled = models.BooleanField(_(u"enabled"), default=True)
    last_run_at = models.DateTimeField(
                              auto_now=False, auto_now_add=False,
                              editable=False, blank=True, null=True)
    total_run_count = models.PositiveIntegerField(default=0, editable=False)
    date_changed = models.DateTimeField(auto_now=True)

    objects = PeriodicTaskManager()
    no_changes = False

    class Meta:
        verbose_name = _(u"periodic task")
        verbose_name_plural = _(u"periodic tasks")

    def save(self, *args, **kwargs):
        self.exchange = self.exchange or None
        self.routing_key = self.routing_key or None
        self.queue = self.queue or None
        super(PeriodicTask, self).save(*args, **kwargs)

    def __unicode__(self):
        if self.interval:
            return u"%s: %s" % (self.name, unicode(self.interval))
        if self.crontab:
            return u"%s: %s" % (self.name, unicode(self.crontab))
        return u"%s: {no schedule}" % (self.name, )

    @property
    def schedule(self):
        if self.interval:
            return self.interval.schedule
        if self.crontab:
            return self.crontab.schedule

signals.pre_delete.connect(PeriodicTasks.changed, sender=PeriodicTask)
signals.pre_save.connect(PeriodicTasks.changed, sender=PeriodicTask)


class WorkerState(models.Model):
    hostname = models.CharField(_(u"hostname"), max_length=255, unique=True)
    last_heartbeat = models.DateTimeField(_(u"last heartbeat"), null=True)

    objects = ExtendedManager()

    class Meta:
        """Model meta-data."""
        verbose_name = _(u"worker")
        verbose_name_plural = _(u"workers")
        get_latest_by = "last_heartbeat"
        ordering = ["-last_heartbeat"]

    def __unicode__(self):
        return self.hostname

    def __repr__(self):
        return "<WorkerState: %s>" % (self.hostname, )

    def is_alive(self):
        if self.last_heartbeat:
            return time() < self.heartbeat_timestamp + HEARTBEAT_EXPIRE
        return False

    @property
    def heartbeat_timestamp(self):
        return mktime(self.last_heartbeat.timetuple())


class TaskState(models.Model):
    state = models.CharField(_(u"state"),
                max_length=64,
                choices=TASK_STATE_CHOICES)
    task_id = models.CharField(_(u"UUID"),
                max_length=36, unique=True)
    name = models.CharField(_(u"name"),
                max_length=200, null=True)
    tstamp = models.DateTimeField(_(u"event received at"),
                editable=False)
    args = models.CharField(_(u"Arguments"),
                max_length=200, null=True)
    kwargs = models.CharField(_(u"Keyword arguments"),
                max_length=200, null=True)
    eta = models.DateTimeField(_(u"ETA"), null=True,
                help_text=u"date to execute")
    expires = models.DateTimeField(_(u"expires"), null=True)
    result = models.TextField(_(u"result"), null=True)
    traceback = models.TextField(_(u"traceback"), null=True)
    runtime = models.FloatField(_(u"execution time"), null=True,
                help_text=_(u"in seconds if task successful"))
    retries = models.IntegerField(_(u"number of retries"), default=0),
    worker = models.ForeignKey(WorkerState, null=True,
                               verbose_name=_("worker"))
    hidden = models.BooleanField(editable=False, default=False)

    objects = TaskStateManager()

    class Meta:
        """Model meta-data."""
        verbose_name = _(u"task")
        verbose_name_plural = _(u"tasks")
        get_latest_by = "tstamp"
        ordering = ["-tstamp"]

    def __unicode__(self):
        name = self.name or "UNKNOWN"
        s = u"%s %s %s" % (self.state.ljust(10),
                           self.task_id.ljust(36),
                           name)
        if self.eta:
            s += u" eta:%s" % (self.eta, )
        return s

    def __repr__(self):
        return "<TaskState: %s %s(%s) ts:%s>" % (self.state,
                                                 self.name or "UNKNOWN",
                                                 self.task_id,
                                                 self.tstamp)


if (django.VERSION[0], django.VERSION[1]) >= (1, 1):
    # keep models away from syncdb/reset if database backend is not
    # being used.
    if conf.RESULT_BACKEND != 'database':
        TaskMeta._meta.managed = False
        TaskSetMeta._meta.managed = False
