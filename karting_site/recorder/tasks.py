from celery import current_app, Celery, shared_task
from celery.signals import after_task_publish, task_postrun, task_success, after_setup_logger, after_setup_task_logger
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
def hello(self):
    time.sleep(1)
    hello = "Hello!"
    return hello

@shared_task(name = "recorder.start_recorder", bind = True)
def start_recorder(
    self, 
    race_id,
    ):
    logger_name_and_file_name = f"race_id_{race_id}_{datetime.datetime.now()}"
    logger = logging.getLogger(logger_name_and_file_name)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # FileHandler
    fh = logging.FileHandler(f'recorder/data/logs/{logger_name_and_file_name}.log')
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    recorder.record_race(race_id, logger)

@after_task_publish.connect(sender= start_recorder.name)
def task_sent_handler(sender=None, headers=None, body=None, **kwargs):
    # information about task are located in headers for task messages
    # using the task protocol version 2.
    print("Hi!")
    info = headers if 'task' in headers else body
    
@task_success.connect(sender= start_recorder.name)
def task_success_handler(sender=None, headers=None, body=None, **kwargs):
    # information about task are located in headers for task messages
    # using the task protocol version 2.
    print("Good Bye!")
    info = headers if 'task' in headers else body
