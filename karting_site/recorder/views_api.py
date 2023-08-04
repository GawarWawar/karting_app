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
    try:
        last_race = models.Race.objects.last()
    except ObjectDoesNotExist:
        context.update(
            {
                "message" : "There is no race created"
            }
        )
    else:
        context["last_race"] = last_race.to_dict()
        records_of_the_last_race = models.RaceRecords.objects.filter(race = last_race.pk).values()
        context["records_of_the_last_race"] = list(records_of_the_last_race)
    return HttpResponse(json.dumps(context)) 