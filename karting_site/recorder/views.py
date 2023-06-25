from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse

from celery.result import AsyncResult

import sys

from . import tasks

# Create your views here.
def index (request):
    message = tasks.hello.delay()
    return HttpResponseRedirect(f"/recorder/{message.id}")

def view (request, celery_id):
    res = AsyncResult(celery_id,task_name=tasks.hello)
    return HttpResponse([res.status, " ",res.result])