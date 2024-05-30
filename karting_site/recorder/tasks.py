from celery import current_app, Celery, shared_task
from celery.signals import after_task_publish, task_postrun, task_success, after_setup_logger, after_setup_task_logger
from celery.contrib.abortable import AbortableTask
from celery.utils.log import get_task_logger

from django_celery_results.models import TaskResult
from celery.result import AsyncResult

import logging
import time
import datetime
import os

from . import models
from . import recorder

#Tasks

# Signals
#TODO: REWORK OR DELETE
@after_task_publish.connect(sender= recorder.record_race.name)
def task_sent_handler(sender=None, headers=None, body=None, **kwargs):
    # information about task are located in headers for task messages
    # using the task protocol version 2.
    # print(f"Recording started successfully at {datetime.datetime.now()}")
    ...

#TODO: make it prettier
@task_postrun.connect()
def task_success_handler(
    sender=None, task_id = None, **kwargs
):
   if sender.name == recorder.record_race.name:
        race_obj = models.Race.objects.get(
           pk = sender.race_id, 
        )
        race_obj.date_record_finished = datetime.datetime.now()
        race_obj.celery_recorder_id = "0"
        race_obj.save()
        
        if race_obj.was_recorded_complete:
            new_race = models.Race.objects.create(
                    name_of_the_race = datetime.datetime.now()
                )
            new_race.is_recorded = True
            new_race.date_record_started = datetime.datetime.now()

            recording_by_celery = recorder.record_race.delay(new_race.id)
            new_race.celery_recorder_id = recording_by_celery.id

            new_race.save()
