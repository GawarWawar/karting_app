from celery import current_app, Celery, shared_task
from celery.signals import after_task_publish, task_postrun, task_success

from celery.result import AsyncResult

import time

from . import models



@shared_task
def wait(delay):
    time.sleep(delay)
    return "Done"

@shared_task(name = "recorder.hello", bind = True)
def hello(self):
    time.sleep(15)
    hello = "Hello!"
    return hello

@after_task_publish.connect(sender=hello.name)
def task_sent_handler(sender=None, headers=None, body=None, **kwargs):
    # information about task are located in headers for task messages
    # using the task protocol version 2.
    print("Hi!")
    info = headers if 'task' in headers else body
    
@task_success.connect(sender=hello.name)
def task_success_handler(sender=None, headers=None, body=None, **kwargs):
    # information about task are located in headers for task messages
    # using the task protocol version 2.
    print("Good Bye!")
    info = headers if 'task' in headers else body
