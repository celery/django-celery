from celery.task import task


@task
def add(x, y):
    return x + y


@task
def sleeptask(i):
    from time import sleep
    sleep(i)
    return i


@task
def raisetask():
    raise KeyError("foo")
