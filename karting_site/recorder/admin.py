from collections.abc import Iterator
from typing import Any
from django.contrib import admin
from django.http import HttpResponse, HttpResponseRedirect
from django.utils.datastructures import MultiValueDictKeyError

from django_celery_results.models import TaskResult
from . import models
from . import tasks
from .utils import tools as u_tools
from . import recorder
    
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
    ]
    
    list_display = [
        "name_of_the_race", 
        "publish_date", 
        "is_recorded"
    ]
    
    change_form_template = "change_form.html"
    
    def response_change(self, request, obj):
        if "_start_recording" in request.POST:
            obj = self.get_queryset(request).get(pk=obj.id)
            obj.is_recorded = True
            task_to_do_name = tasks.start_recorder.name
            try:
                celery_object_that_started_recording = TaskResult.objects.get(task_id = obj.celery_recorder_id, status = "STARTED", task_name = task_to_do_name)
            except TaskResult.DoesNotExist:
                recording_by_celery = tasks.start_recorder.delay(obj.id)
                obj.celery_recorder_id = recording_by_celery.id
                message = f"Recording started. Process id is {recording_by_celery.id}"
            else:
                message = f"Recording for this race has already started. Celery working on it {celery_object_that_started_recording.task_id} id"

            self.message_user(request, message)
            obj.save()
            return HttpResponseRedirect(".")
        return super().response_change(request, obj)

admin.site.register(models.Race, RaceAdmin)
admin.site.register(models.RaceRecords, RaceRecordsAdmin)

