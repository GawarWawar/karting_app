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
    last_race_with_records_pk = last_race.pk
    
    while True:
        last_race_with_records = models.Race.objects.filter(pk = last_race_with_records_pk).values()
        # Check if race with this pk exists
        if last_race_with_records: 
            last_race_with_records = last_race_with_records[0]
            try:
                records_of_the_race = models.RaceRecords.objects.filter(race = last_race_with_records_pk).order_by("-pk").values()
            except AttributeError:
                # Dont need to do anything here
                # Template will display all needed info with NoneType object given
                # !!! NOTE This will occure in the situations when no Races are created
                ...   
            else:
                # Check if race has records
                if not records_of_the_race and last_race_with_records_pk - 1 >= 0:
                    last_race_with_records_pk -= 1
                else:
                    # Rerurn race and its` records information
                    context["race"] = last_race_with_records
                    context["records_of_the_race"] = records_of_the_race
                    break
        else:
            # Go to previous race
            if last_race_with_records_pk - 1 >= 0:
                last_race_with_records_pk -= 1
            else:
                context["race"] = last_race
                break

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
        records_of_the_race = models.RaceRecords.objects.filter(race = race_id).order_by("-pk").values()
        context["records_of_the_race"] = records_of_the_race 
    return render(request, "individual_race_page.html", context)

# List of all races
class AllRacesPage(generic.ListView):
    template_name = "list_of_all_races.html"
    context_object_name = "all_races_list"
    
    def get_queryset(self):
        races = models.Race.objects.all().order_by("-pk").values()
        return races
    