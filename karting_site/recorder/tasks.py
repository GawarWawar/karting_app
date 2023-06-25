from celery import Celery,shared_task

import time

@shared_task
def wait(delay):
    time.sleep(delay)
    return "Done"

@shared_task
def hello():
    hello = "Hello!"
    return hello