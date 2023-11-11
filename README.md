# karting_app
This project was created to set up tool, that could help in Go-kart competition in the Zhaha Shvydkosti Karting Centre.  
First part of the project, Recorder gets info of laps done in the race and writes them into the Django model.  
Second part of the project, Analyzer uses recorded info and gives new/additional info about what is happaning in the race.  
As a web application, this project has:
- Admin set up which is used to create Races and start their record
- Part with pages which has basic functionality to look on recorded info
- Api with provided information about the project

# Instalation and start process
Project is being deployed on [karting-app-gawarsprojects.koyeb.app](https://karting-app-gawarsprojects.koyeb.app/)
However, if there is a need to create separate entity of the project, here is information about it`s setup:
This project has web application instance and worker for asynchronous tasks, that are needed to be started separetely.  
Home directory for all actions should be /karting_site

To begin working on a project, install all needed packages from requirements.txt:
```bash
$ python3 -m pip install requirements.txt
```

This project is written on Django, so first step is to run needed commands to build db and collect statics:
However, before building DB, configure setting to use propper engine and connect to existing db.  
Project uses PostgreSQL and to configure it add .env file with: DATABASE_NAME, DATABASE_USER, DATABASE_PASSWORD and DATABASE_HOST variables.
After that we can continue with typical Django setup: 
```bash
$ python3 manage.py migrate
```
```bash
$ python3 manage.py collectstatics
```
After that out of the way, next step is creation of admin superuser:
```bash
$ python3 manage.py createsuperuser 
```
Our wsgi server ready to start. Project uses gunicorn to do that:
```bash
$ gunicorn karting_site.wsgi
```
As all Django servers, web app could be started directly from the manage.py:
```bash
$ python3 manage.py runserver 
```
To access it from outside network too, use 0.0.0.0:8000 specificator:
```bash
$ python3 manage.py runserver 0.0.0.0:8000
```

The next step is to start Celery worker.  
This project uses Reddis server to communicate between web app and worker.  
After configuration of Redis server, add to .env file next varialbes to connect Celery to Redis: REDIS_USER, REDIS_PASSWORD, REDIS_URL, REDIS_PORT
There is 2 ways to start Celery:
1. Run Celery on the separate console: 
```bash
$ celery -A karting_site worker --loglevel=INFO -O fair --pool solo
```
2. To launch both Celery and server: 
```bash
$ gunicorn karting_site.wsgi & celery -A karting_site worker --loglevel=INFO -O fair
```

# Instructions of how to use
If u decide to use deployed version:
- Go to the [karting-app-gawarsprojects.koyeb.app](https://karting-app-gawarsprojects.koyeb.app/)
- It will has all needed instruction of how to use various parts of the project. Contact admin to create and record races

If u decide to deploy this project yourself:  
Recorder section:
- To create race - head to /admin/recorder/race/add/ and fill the form and Save the Race
- To record created race - head to /admin/recored/race and get to the created race (can choose from the list of Races presented on the page) and press "Start Recording" button. Recording process can be aborted with "Abort Recording" button
- In the Race records category recorded laps will be shown

Analyzer section:  
To use analyzation process:
- go to the main page of the site
- select a race
- click "Analyze this race"
Next steps could be done to improve resaults of analyzation process: 
- create "Types of BRs". In the Karting Centre there are 2, 4, 7 and 10 hours BigRaces
- import CSVs in the "BigRaces" category with races of the season or other desired period. In the CSV upload form will be stated colums, that are neede to be present in the file. Already created CSV files, that are ready to import, could be found in data/temp_by_races folder. This allow analyzer to process the race and compare pilots temp in this race and previous their appiarence
