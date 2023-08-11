# karting_app

# Instalation and start process
Project has web application instance and worker for asynchronous tasks, that are needed to be started separetely
Home directory for all actions should be karting_app/karting_site

To begin working on a project, install all needed packages from requirements.txt:
$ python3 -m pip install requirements.txt 

This project is written on Django, so first step is to run needed commands to build db and collect statics:
$ python3 manage.py migrate
$ python3 manage.py collectstatics
After that out of the way, next step is creation of admin superuser:
$ python3 manage.py createsuperuser 
Our wsgi server ready to start. Project uses gunicorn to do that:
$ gunicorn karting_site.wsgi
As all Django servers, web app could be started directly from the manage.py:
$ python3 manage.py runserver 
To access it from outside network too, use 0.0.0.0:8000 specificator:
$ python3 manage.py runserver 0.0.0.0:8000

We are ready to start Celery worker.
This project uses Reddis server to communicate between web app and worker. To start Celery Redis server should be working
There is 2 ways to start Celery:
1. Run Celery on the separate console: 
$ celery -A karting_site worker --loglevel=INFO -O fair --pool solo
2. To launch both Celery and server: 
$ gunicorn karting_site.wsgi & celery -A karting_site worker --loglevel=INFO -O fair