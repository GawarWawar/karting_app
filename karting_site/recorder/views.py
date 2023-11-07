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
# List of all records of the last Race, acts like a starting page for the recorder
def recorder_starting_page (request):
    context ={}
    last_race = models.Race.objects.last()
    context["last_race"] = last_race
    try:
        records_of_the_last_race = models.RaceRecords.objects.filter(race = last_race.pk).values()
    except AttributeError:
        # Dont need to do anything here
        # Template will display all needed info with NoneType object given
        # This will occure in the situations when no Races are created ->
        # So dont need logs about it
        pass
    else:
        context["records_of_the_last_race"] = records_of_the_last_race
    return render(request, "recorder_index.html", context) 

# List of all Records of given Race
def view_race_records_by_id (request, race_id):
    context = {}
    try:
        race = models.Race.objects.get(pk = race_id)
    except ObjectDoesNotExist:
        # Same as AttributeError in recorder_starting_page () ->
        pass
    else:
        context["race"] = race
        records = models.RaceRecords.objects.filter(race = race_id).order_by("-pk").values()
        context["all_races_records"] = records 
    return render(request, "races_records.html", context)

# List of all races
class AllRacesPage(generic.ListView):
    template_name = "races.html"
    context_object_name = "all_races_list"
    
    def get_queryset(self):
        races = models.Race.objects.all().values()
        return races
    