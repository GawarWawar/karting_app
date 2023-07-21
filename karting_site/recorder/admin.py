from collections.abc import Iterator
from typing import Any
from django.contrib import admin
from django.http import HttpResponse, HttpResponseRedirect
from django.utils.datastructures import MultiValueDictKeyError
from django.db.utils import IntegrityError
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import redirect, render
from django.urls import path
from django import forms

import pandas as pd

import datetime

from django_celery_results.models import TaskResult
from celery.result import AsyncResult

from . import models
from . import tasks
from . import recorder
   
class CsvImportForm(forms.Form):
    csv_file = forms.FileField()
   
 
class NamesInRaceFilter(admin.SimpleListFilter):
    title = 'Names in the race'
    parameter_name = 'name_of_a_pilot'

    def lookups(self, request, model_admin):
        try:
            query = model_admin.get_queryset(request).filter(race = request.GET.__getitem__("race__id__exact"))
        except MultiValueDictKeyError: 
            return None
        else:
            query = query.values("pilot_name").distinct()
            list_to_return = []
            for value in query:
                list_to_return.append([f"{value['pilot_name']}",value['pilot_name']])
        
            return tuple(list_to_return)

    def queryset(self, request, queryset):
        try:
            queryset = queryset.filter(pilot_name = request.GET.__getitem__("name_of_a_pilot"))
        except MultiValueDictKeyError: 
            pass
        return queryset    

# Register your models here.    
class RaceRecordsAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "race",
        "team_number",
        "name_of_a_pilot",
        "kart",
        "lap_count",
        "lap_time",
        "s1_time",
        "s2_time",
        "team_segment",
        "true_name",
        "true_kart",
    ]
    
    list_filter = ( 
        "race", 
        NamesInRaceFilter
    )
    
    def name_of_a_pilot(self, obj):
        return obj.pilot_name
        
class RaceAdmin(admin.ModelAdmin):
    fields = [
        "name_of_the_race",
        "is_recorded"
    ]
    
    readonly_fields = [
        "is_recorded"
    ]
    
    list_display = [
        "name_of_the_race", 
        "id",
        "publish_date", 
        "is_recorded"
    ]
    
    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('import-csv/', self.import_csv),
        ]
        return my_urls + urls
    
    change_form_template = "race_admin_add_button_changeform.html"
    
    def response_change(self, request, obj):
        if "_start_recording" in request.POST:
            obj = self.get_queryset(request).get(pk=obj.id)
            obj.is_recorded = True
            obj.date_record_started = datetime.datetime.now()
            task_to_do_name = recorder.record_race.name
            try:
                celery_object_that_started_recording = TaskResult.objects.get(task_id = obj.celery_recorder_id, status = "STARTED", task_name = task_to_do_name)
            except TaskResult.DoesNotExist:
                recording_by_celery = recorder.record_race.delay(obj.id)
                obj.celery_recorder_id = recording_by_celery.id
                obj.save()
                message = f"Recording started. Process id is {recording_by_celery.id}"
            else:
                obj.save()
                message = f"Recording for this race has already started. Celery working on it {celery_object_that_started_recording.task_id} id"
            self.message_user(request, message)
            return HttpResponseRedirect(".")
        elif "_abort_recording" in request.POST:
            obj = self.get_queryset(request).get(pk=obj.id)
            task_to_abort_name = recorder.record_race.name
            try:
                celery_object_that_started_recording = TaskResult.objects.get(task_id = obj.celery_recorder_id, status = "STARTED", task_name = task_to_abort_name)
            except TaskResult.DoesNotExist:
                obj.save()
                message = f"Recording for the race with {obj.id} id is not in progress!"
            else:
                #task_in_progress = AsyncResult(id = obj.celery_recorder_id, task_name=task_to_abort_name)
                task_in_progress = recorder.record_race.AsyncResult(obj.celery_recorder_id)
                task_in_progress.abort()
                obj.celery_recorder_id = 0
                obj.save()
                message = f"Recording aborted, process id was {task_in_progress.id}"
            self.message_user(request, message)
            return HttpResponseRedirect(".")
            
        return super().response_change(request, obj)

    change_list_template = "race_admin_changelist.html"    
    def import_csv(self, request):
        if request.method == "POST":
            race_name = request.POST["race_name"]
            try:
                race = models.Race.objects.get(name_of_the_race = race_name)
            except (IntegrityError, ObjectDoesNotExist):
                race = models.Race(name_of_the_race = race_name)
            
            race.is_recorded = True
            
            if request.POST["was_recorded_complete"]:
                race.was_recorded_complete = request.POST["was_recorded_complete"]
            race.save()
                
            csv_file = request.FILES["csv_file"]
            csv_content = pd.read_csv(csv_file)
            for row in list(csv_content.loc[:, "team"].index):
                team_number = csv_content.at[row, "team"]
                pilot_name = csv_content.at[row, "pilot"]
                kart = csv_content.at[row, "kart"]
                lap_count = csv_content.at[row, "lap"]
                lap_time = csv_content.at[row, "lap_time"]
                s1_time = csv_content.at[row, "s1"]
                s2_time = csv_content.at[row, "s2"]
                team_segment = csv_content.at[row, "segment"]
                true_name = csv_content.at[row, "true_name"]
                true_kart = csv_content.at[row, "true_kart"]
                
                pilot = models.RaceRecords(
                    race = race,
                    team_number = team_number,
                    pilot_name = pilot_name,
                    kart = kart,
                    lap_count = lap_count,
                    lap_time = lap_time,
                    s1_time = s1_time,
                    s2_time = s2_time,
                    team_segment = team_segment,
                    true_name = true_name,
                    true_kart = true_kart,
                )
                pilot.save()
            self.message_user(request, "Your csv file has been imported")
            return redirect("..")
        form = CsvImportForm()
        payload = {
            "form": form,
            "true_false": [True, False],
        }
        return render(
            request, "csv_form_race_admin.html", payload
        )
    

admin.site.register(models.Race, RaceAdmin)
admin.site.register(models.RaceRecords, RaceRecordsAdmin)

