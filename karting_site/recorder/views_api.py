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
# List of all records of the last Race, acts lice a starting page for the recorder
def last_race_records_api (request):
    context = {
        "last_race" : {},
        "records_of_the_last_race" : []
    }
    last_race = models.Race.objects.last()
    try:
        context["last_race"] = last_race.to_dict()
    except AttributeError:
        context.update(
            {
                "message" : "There is no race created"
            }
        )
    else:
        records_of_the_last_race = models.RaceRecords.objects.filter(race = last_race.pk).values()
        context["records_of_the_last_race"] = list(records_of_the_last_race)
    return HttpResponse(json.dumps(context)) 

def list_of_all_races_page_api (request):
    races = [race.to_dict() for race in models.Race.objects.all()]
    return_dict = {
        "data": {
            "races":races
        }
            
    }
    return HttpResponse(json.dumps(return_dict))

# List of all Records of given Race
def view_race_records_by_id_api (request, race_id):
    context = {
        "data": {}
    }
    try:
        race = models.Race.objects.get(pk = race_id).to_dict()
    except ObjectDoesNotExist:
        context.update(
            {
                "message": "There is no Race under that id."
            }
        )
    else:
        context["data"].update(
            {
                "race" : race
            }
            )
    records = [record.only_race_data_to_dict() for record in models.RaceRecords.objects.filter(race = race_id).order_by("-pk")]
    context["data"].update(
        {
            "race_records" : records
        }
    )
    return HttpResponse (json.dumps(context))