from django.contrib import admin

from .models import TaskState, WorkerState


class TaskMonitor(admin.ModelAdmin):
    pass


class WorkerMonitor(admin.ModelAdmin):
    pass


admin.site.register(TaskState, TaskMonitor)
admin.site.register(WorkerState, WorkerMonitor)

