from celery.task import task

from .models import Thing


@task(name='c.unittest.SomeAppTask')
def SomeAppTask(**kwargs):
    return 42


@task(name='c.unittest.SomeModelTask')
def SomeModelTask(pk):
    thing = Thing.objects.get(pk=pk)
    return thing.name
