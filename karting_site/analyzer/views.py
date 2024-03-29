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
from . import analyzer

# Create your views here.
def race_analyze(request, race_id):
    content = analyzer.analyze_race(race_id)
    
    return render(request, "analyzer.html", content)

def race_kart_statistic (request, race_id):
    content = analyzer.compute_kart_statistic(race_id)

    return render(request, "race_statistic.html", content)
