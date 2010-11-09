from celery import Celery

app = Celery(loader="djcelery.loaders.DjangoLoader")
