from celery.task import task

@task(name="c.unittest.FunctionalAddTask")
def FunctionalAddTask(a, b):
    return a + b
