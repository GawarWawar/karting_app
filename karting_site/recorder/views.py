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
    context ={}
    try:
        last_race = models.Race.objects.last()
    except ObjectDoesNotExist:
        pass
    else:
        context["last_race"] = last_race
    records_of_the_last_race = models.RaceRecords.objects.filter(race = last_race.pk).values()
    context["records_of_the_last_race"] = records_of_the_last_race
    return render(request, "index.html", context) 

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
    