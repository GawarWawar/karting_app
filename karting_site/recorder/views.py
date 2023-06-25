from django.shortcuts import render
from django.http import HttpResponse

from celery.result import AsyncResult

import sys

from . import tasks

# Create your views here.
def index (request):
    done = tasks.hello.delay()
    return HttpResponse(done)

def view (request, celery_id):
    res = AsyncResult(celery_id,task_name=tasks.hello)
    return HttpResponse([res.status, " ",res.result])