from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse

from django_celery_results.models import TaskResult
from django.db.models.query import EmptyQuerySet

from celery import current_app, Celery, shared_task, _state, current_task
from celery.result import AsyncResult

import sys
import time

from . import tasks
from . import models

# Create your views here.
def index (request):
    task_to_do_name = tasks.hello.name
    
    tasks_that_already_started = TaskResult.objects.filter(status = "STARTED", task_name = task_to_do_name)
    if not tasks_that_already_started:
        message = tasks.hello.delay()
        return HttpResponseRedirect(f"/recorder/{message.id}")
    else:
        tasks_that_already_started = TaskResult.objects.filter(status = "STARTED", task_name = task_to_do_name).values()
        print(tasks_that_already_started)
        return HttpResponse(f"Task with {task_to_do_name} already started on {tasks_that_already_started[0]['task_id']} id")

def view (request, celery_id):
    res = AsyncResult(celery_id,task_name=tasks.hello)
    return HttpResponse([res.status, " ",res.result, " ",])