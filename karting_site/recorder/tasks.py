from celery import current_app, Celery, shared_task
from celery.signals import after_task_publish

import time

@after_task_publish.connect
def update_sent_state(sender=None, headers=None, **kwargs):
    # the task may not exist if sent using `send_task` which
    # sends tasks by name, so fall back to the default result backend
    # if that is the case.
    task = current_app.tasks.get(sender)
    backend = task.backend if task else current_app.backend
 
    backend.store_result(headers['id'], None, "SENT")

@shared_task
def wait(delay):
    time.sleep(delay)
    return "Done"

@shared_task(task_track_started=True)
def hello():
    time.sleep(15)
    hello = "Hello!"
    return hello

