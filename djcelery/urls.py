"""

URLs defined for celery.

* ``/$task_id/done/``

    URL to :func:`~celery.views.is_successful`.

* ``/$task_id/status/``

    URL  to :func:`~celery.views.task_status`.

"""
from django.conf.urls.defaults import patterns, url

from djcelery import views


urlpatterns = patterns("",
    url(r'^(?P<task_id>[\w\d\-]+)/done/?$', views.is_task_successful,
        name="celery-is_task_successful"),
    url(r'^(?P<task_id>[\w\d\-]+)/status/?$', views.task_status,
        name="celery-task_status"),
)
