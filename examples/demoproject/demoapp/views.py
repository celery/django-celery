# Create your views here.

from tasks import add
from django.http import HttpResponse


def foo(request):
    r = add.delay(2, 2)
    return HttpResponse(r.task_id)
