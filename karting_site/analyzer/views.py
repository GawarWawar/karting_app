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

# Create your views here.
def index(request):
    return HttpResponse("Hello!")