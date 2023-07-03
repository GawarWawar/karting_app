from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.views import generic

from django_celery_results.models import TaskResult
from django.db.models.query import EmptyQuerySet
from django.core.exceptions import ObjectDoesNotExist

from celery import current_app, Celery, shared_task, _state, current_task
from celery.result import AsyncResult

import sys
import time
import json

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

def view_races_records (request, race_id):
    context = {}
    try:
        race = models.Race.objects.get(pk = race_id)
    except ObjectDoesNotExist:
        pass
    else:
        context["race"] = race
    records = models.RaceRecords.objects.filter(race = race_id).values()
    context["all_races_records"] = records 
    print(records)
    return render(request, "races_records.html", context)
    
class ViewRaceRecords(generic.ListView):     
    model = models.RaceRecords
    template_name = "races_records.html"
    context_object_name = "all_races_records_list"

    def get(self, request, *args, **kwargs):
        print(kwargs)
        self.race_id = kwargs['race_id']
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        records = self.model.objects.filter(race = self.race_id).values()
        return records

class AllRacesPage(generic.ListView):
    template_name = "races.html"
    context_object_name = "all_races_list"
    
    def get_queryset(self):
        races = models.Race.objects.all().values()
        print(races)
        return races
    