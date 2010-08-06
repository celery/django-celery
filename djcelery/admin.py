from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from celery import states

from .models import TaskState, WorkerState

STATE_COLORS = {states.SUCCESS: "green",
                states.FAILURE: "red",
                states.REVOKED: "magenta",
                states.STARTED: "yellow",
                states.RETRY: "orange",
                "RECEIVED": "blue"}


def colored_state(task):
    color = STATE_COLORS.get(task.state, "black")
    return """<b><span style="color: %s;">%s</span></b>""" % (color,
                                                              task.state)
colored_state.allow_tags = True
colored_state.short_description = _("state")
colored_state.admin_order_field = "state"

def eta(task):
    return task.eta or \
            """<span style="color: gray;">disabled</span>"""
eta.short_description = _("ETA")
eta.allow_tags = True
eta.admin_order_field = "eta"


def fixedwidth(field, name=None):
    def f(task):
        return """<code>%s</code>""" % getattr(task, field)
    f.allow_tags = True
    f.short_description = name or field
    f.admin_order_field = field
    return f


class TaskMonitor(admin.ModelAdmin):
    date_hierarchy = "timestamp"
    fieldsets = (
            (None, {
                "fields": ("state", "task_id", "name", "args", "kwargs",
                           "eta", "runtime", "worker"),
                "classes": ("extrapretty", ),
            }),
            ("Details", {
                "classes": ("collapse", "extrapretty"),
                "fields": ("result", "traceback", "expires"),
            }),
    )
    list_display = (fixedwidth("task_id", name=_("UUID")),
                    colored_state,
                    "name",
                    fixedwidth("args"),
                    fixedwidth("kwargs"),
                    eta,
                    "worker")
    readonly_fields = ("state", "task_id", "name", "args", "kwargs",
                       "eta", "runtime", "worker", "result", "traceback",
                       "expires")
    list_filter = ("state", "name", "timestamp", "eta", "worker")
    search_fields = ("name", "task_id", "args", "kwargs", "worker__hostname")


class WorkerMonitor(admin.ModelAdmin):
    pass


admin.site.register(TaskState, TaskMonitor)
admin.site.register(WorkerState, WorkerMonitor)

