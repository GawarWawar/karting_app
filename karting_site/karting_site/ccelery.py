from __future__ import absolute_import, unicode_literals
from celery import Celery
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'karting_site.settings')

app = Celery(
    'karting_site', 
    backend='rpc://', 
    broker='pyamqp://', 
)

app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

if __name__ == '__main__':
    app.start()