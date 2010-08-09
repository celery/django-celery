from pprint import pformat

from django.contrib import admin
from django.contrib.admin import helpers
from django.contrib.admin.views import main as main_views
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.encoding import force_unicode
from django.utils.html import escape
from django.utils.translation import ugettext_lazy as _

from celery import states
from celery.messaging import establish_connection
from celery.registry import tasks
from celery.task.control import broadcast, revoke, rate_limit
from celery.utils import truncate_text, abbrtask
from celery.utils.functional import wraps

from .models import TaskState, WorkerState


TASK_STATE_COLORS = {states.SUCCESS: "green",
                     states.FAILURE: "red",
                     states.REVOKED: "magenta",
                     states.STARTED: "yellow",
                     states.RETRY: "orange",
                     "RECEIVED": "blue"}
NODE_STATE_COLORS = {"ONLINE": "green",
                     "OFFLINE": "gray"}


class MonitorList(main_views.ChangeList):

    def __init__(self, *args, **kwargs):
        super(MonitorList, self).__init__(*args, **kwargs)
        self.title = self.model_admin.list_page_title


def attrs(**kwargs):
    def _inner(fun):
        for attr_name, attr_value in kwargs.items():
            setattr(fun, attr_name, attr_value)
        return fun
    return _inner


def display_field(short_description, admin_order_field, allow_tags=True,
        **kwargs):
    return attrs(short_description=short_description,
                 admin_order_field=admin_order_field,
                 allow_tags=allow_tags, **kwargs)


def action(short_description, **kwargs):
    return attrs(short_description=short_description, **kwargs)


@display_field(_("state"), "state")
def colored_state(task):
    state = escape(task.state)
    color = TASK_STATE_COLORS.get(task.state, "black")
    return """<b><span style="color: %s;">%s</span></b>""" % (color, state)


@display_field(_("state"), "last_timestamp")
def node_state(node):
    state = node.is_alive() and "ONLINE" or "OFFLINE"
    color = NODE_STATE_COLORS[state]
    return """<b><span style="color: %s;">%s</span></b>""" % (color, state)


@display_field(_("ETA"), "eta")
def eta(task):
    return escape(task.eta) or \
            """<span style="color: gray;">disabled</span>"""


@display_field(_("name"), "name")
def name(task):
    return """<b>%s</b>""" % (escape(abbrtask(task.name, 16)), )


def fixedwidth(field, name=None, pt=6, width=16, maxlen=64, pretty=False):

    @display_field(name or field, field)
    def f(task):
        val = getattr(task, field)
        if pretty:
            val = pformat(val, width=width)
        if val.startswith("u'") or val.startswith('u"'):
            val = val[2:-1]
        val.replace(",", ",\n")
        val.replace("\n", "<br />")

        if len(val) > maxlen:
            val = val[:maxlen] + "..."
        return """<span style="font-size: %spt;
                               font-family: Menlo, Courier;
                  ">%s</span>""" % (pt, escape(val), )
    return f


class ModelMonitor(admin.ModelAdmin):
    can_add = False
    can_delete = False

    def get_changelist(self, request, **kwargs):
        return MonitorList

    def change_view(self, request, object_id, extra_context=None):
        extra_context = extra_context or {}
        extra_context.setdefault("title", self.detail_title)
        return super(ModelMonitor, self).change_view(request, object_id,
                                                     extra_context)

    def has_delete_permission(self, request, obj=None):
        if not self.can_delete:
            return False
        return super(ModelMonitor, self).has_delete_permission(request, obj)

    def has_add_permission(self, request):
        if not self.can_add:
            return False
        return super(ModelMonitor, self).has_add_permission(request)


class TaskMonitor(ModelMonitor):
    detail_title = _("Task detail")
    list_page_title = _("Tasks")
    rate_limit_confirmation_template = "djcelery/confirm_rate_limit.html"
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
    list_display = (fixedwidth("task_id", name=_("UUID"), pt=8),
                    colored_state,
                    name,
                    fixedwidth("args", pretty=True),
                    fixedwidth("kwargs", pretty=True),
                    eta,
                    "worker")
    readonly_fields = ("state", "task_id", "name", "args", "kwargs",
                       "eta", "runtime", "worker", "result", "traceback",
                       "expires")
    list_filter = ("state", "name", "timestamp", "eta", "worker")
    search_fields = ("name", "task_id", "args", "kwargs", "worker__hostname")
    actions = ["revoke_tasks",
               "rate_limit_tasks"]

    @action(_("Revoke selected tasks"))
    def revoke_tasks(self, request, queryset):
        connection = establish_connection()
        try:
            for state in queryset:
                revoke(state.task_id, connection=connection)
        finally:
            connection.close()

    @action(_("Rate limit selected tasks"))
    def rate_limit_tasks(self, request, queryset):
        tasks = set([task.name for task in queryset])
        opts = self.model._meta
        app_label = opts.app_label
        if request.POST.get("post"):
            rate = request.POST["rate_limit"]
            connection = establish_connection()
            try:
                for task_name in tasks:
                    rate_limit(task_name, rate, connection=connection)
            finally:
                connection.close()
            return None

        context = {
            "title": _("Rate limit selection"),
            "queryset": queryset,
            "object_name": force_unicode(opts.verbose_name),
            "action_checkbox_name": helpers.ACTION_CHECKBOX_NAME,
            "opts": opts,
            "root_path": self.admin_site.root_path,
            "app_label": app_label,
        }

        return render_to_response(self.rate_limit_confirmation_template,
                context, context_instance=RequestContext(request))

    def get_actions(self, request):
        actions = super(TaskMonitor, self).get_actions(request)
        actions.pop("delete_selected", None)
        return actions


class WorkerMonitor(ModelMonitor):
    can_add = True
    detail_title = _("Node detail")
    list_page_title = _("Worker Nodes")
    list_display = ("hostname", node_state)
    readonly_fields = ("last_heartbeat", )
    actions = ["shutdown_nodes",
               "enable_events",
               "disable_events"]

    @action(_("Shutdown selected worker nodes"))
    def shutdown_nodes(self, request, queryset):
        broadcast("shutdown", destination=
                  [n.hostname for n in queryset])

    @action(_("Enable event mode for selected nodes."))
    def enable_events(self, request, queryset):
        broadcast("enable_events",
                  destination=[n.hostname for n in queryset])

    @action(_("Disable event mode for selected nodes."))
    def disable_events(self, request, queryset):
        broadcast("disable_events",
                  destination=[n.hostname for n in queryset])

    def get_actions(self, request):
        actions = super(WorkerMonitor, self).get_actions(request)
        actions.pop("delete_selected", None)
        return actions

admin.site.register(TaskState, TaskMonitor)
admin.site.register(WorkerState, WorkerMonitor)
