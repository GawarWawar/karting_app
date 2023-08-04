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

from . import models
from .utils import pilot_rating
from . import analyzer

def analyze_race_api(request, race_id):
    content = analyzer.analyze_race(race_id)
    try:
        content.update(
            {
                "race_id": race_id
            }
        )
    except AttributeError:
        content = {
                "race_id": race_id
            }
    return HttpResponse(json.dumps(content))