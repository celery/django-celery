from time import time, mktime

import django
from django.db import models
from django.utils.translation import ugettext_lazy as _

from picklefield.fields import PickledObjectField

from celery import conf
from celery import states

from djcelery.managers import TaskManager, TaskSetManager, ExtendedManager
from djcelery.managers import TaskStateManager

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


class WorkerState(models.Model):
    hostname = models.CharField(_("hostname"), max_length=255, unique=True)
    last_heartbeat = models.DateTimeField(_("last heartbeat"), null=True)

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
    state = models.CharField(_("state"),
                max_length=64,
                choices=TASK_STATE_CHOICES)
    task_id = models.CharField(_("UUID"),
                max_length=36, unique=True)
    name = models.CharField(_("name"),
                max_length=200, null=True)
    timestamp = models.DateTimeField(_("event received at"),
                editable=False)
    args = models.CharField(_("Arguments"),
                max_length=200, null=True)
    kwargs = models.CharField(_("Keyword arguments"),
                max_length=200, null=True)
    eta = models.DateTimeField(_("ETA"), null=True,
                help_text="date to execute")
    expires = models.DateTimeField(_("expires"), null=True)
    result = models.CharField(_("result"),
                max_length=200, null=True)
    traceback = models.TextField(_("traceback"), null=True)
    runtime = models.FloatField(_("execution time"), null=True,
                help_text=_("in seconds if task successful"))
    retries = models.IntegerField(_("number of retries"), default=0),
    worker = models.ForeignKey(WorkerState, null=True)
    hidden = models.BooleanField(editable=False, default=False)

    objects = TaskStateManager()

    class Meta:
        """Model meta-data."""
        verbose_name = _(u"task")
        verbose_name_plural = _(u"tasks")
        get_latest_by = "timestamp"
        ordering = ["-timestamp"]

    def __unicode__(self):
        name = self.name or "UNKNOWN"
        s = u"%s %s %s" % (self.state.ljust(10),
                           self.task_id.ljust(36),
                           self.name)
        if self.eta:
            s += " eta:%s" % (self.eta, )
        return s

    def __repr__(self):
        name = self.name or "UNKNOWN"
        return "<TaskState: %s %s(%s)>" % (self.state, name, self.task_id, )


if (django.VERSION[0], django.VERSION[1]) >= (1, 1):
    # keep models away from syncdb/reset if database backend is not
    # being used.
    if conf.RESULT_BACKEND != 'database':
        TaskMeta._meta.managed = False
        TaskSetMeta._meta.managed = False
