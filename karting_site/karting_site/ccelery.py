from __future__ import absolute_import, unicode_literals
from celery import Celery
import os
from decouple import config

# To turn on Celery: celery -A karting_site worker --loglevel=INFO -O fair
# To use Celery, Reddis server should be used for this app. to start Reddis server use: redis-server
# To launch both Celery and server: python3 manage.py runserver 0.0.0.0:8000 & celery -A karting_site worker --loglevel=INFO -O fair
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'karting_site.settings')

app = Celery(
    'karting_site', 
    backend='rpc://', 
)

app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

if __name__ == '__main__':
    app.start()