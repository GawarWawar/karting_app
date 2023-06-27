from celery import current_app, Celery, shared_task
from celery.signals import after_task_publish, task_postrun, task_success

from celery.result import AsyncResult

import time

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
def start_recorder(self, race_id):
    recorder.record_race(race_id)

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
