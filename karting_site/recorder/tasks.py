from celery import current_app, Celery, shared_task
from celery.signals import after_task_publish, task_postrun, task_success, after_setup_logger, after_setup_task_logger
from celery.contrib.abortable import AbortableTask
from celery.utils.log import get_task_logger

from celery.result import AsyncResult

import logging
import time
import datetime
import os

from . import models
from . import recorder


@shared_task
def wait(delay):
    time.sleep(delay)
    return "Done"

@shared_task(name = "recorder.hello", bind = True)
def hello(self, obj):
    time.sleep(1)
    hello = "Hello!"
    self.obj = obj
    return hello

@after_task_publish.connect(sender= recorder.record_race.name)
def task_sent_handler(sender=None, headers=None, body=None, **kwargs):
    # information about task are located in headers for task messages
    # using the task protocol version 2.
    print(f"Recording started successfully at {datetime.datetime.now()}")
    
@task_postrun.connect()
def task_success_handler(
    sender=None, task_id = None, **kwargs
):
   if sender.name == recorder.record_race.name:
        queryset = models.Race.objects.get(
           pk = sender.race_id, 
        )
        queryset.date_record_finished = datetime.datetime.now()
        queryset.was_recorded_complete = True       
        queryset.save()
