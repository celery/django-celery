from celery.task import task


@task(name="c.unittest.SomeAppTask")
def SomeAppTask(**kwargs):
    return 42
