
from collections.abc import Iterator
import csv

import datetime

from celery.result import AsyncResult

from django import forms
from django.contrib import admin, messages
from django.core.exceptions import ObjectDoesNotExist
from django.db.utils import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import path
from django.utils.datastructures import MultiValueDictKeyError

from django_celery_results.models import TaskResult

from kombu.exceptions import OperationalError

import pandas as pd
from typing import Any
import zipfile

from . import models
from . import tasks
from . import recorder
from analyzer.utils.analyzation_process.models_transmissions import collect_model_records_into_DataFrame

   
class ExportCsvMixin:
    def export_info_of_each_instance_as_one_csv__action(self, request, queryset):

        meta = self.model._meta
        field_names = [field.name for field in meta.fields]

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename={}.csv'.format(meta)
        writer = csv.writer(response)

        writer.writerow(field_names)
        for obj in queryset:
            row = writer.writerow([getattr(obj, field) for field in field_names])

        return response
    
    export_info_of_each_instance_as_one_csv__action.short_description = "Export info of selected into csv "
   
class CsvImportForm(forms.Form):
    csv_file = forms.FileField()
   
# Filter for the names in the race. It selects names only present in the selected race
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

# Admin models creation
class RaceRecordsAdmin(admin.ModelAdmin, ExportCsvMixin):
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
    
    actions = [
        "export_info_of_each_instance_as_one_csv__action"
        ]
    
    def name_of_a_pilot(self, obj):
        return obj.pilot_name
        
class RaceAdmin(admin.ModelAdmin, ExportCsvMixin):
    fields = [
        "name_of_the_race",
        "id",
        "is_recorded",
        "was_recorded_complete"
    ]
    
    readonly_fields = [
        "id",
        "is_recorded",
        "was_recorded_complete"
    ]
    
    list_display = [
        "name_of_the_race", 
        "id",
        "publish_date", 
        "is_recorded",
        "was_recorded_complete"
    ]
    
    # Add import-csv to list of urls
    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('import-csv/', self.import_csv),
        ]
        return my_urls + urls
    
    
    # Action to export all races as CSVs in one archive
    def export_as_csvs__action(self, request, queryset):
        response = HttpResponse(content_type='application/zip')
        archive_name = "races_archive"
        response['Content-Disposition'] = 'attachment; filename="{}".zip'.format(archive_name)
        
        with zipfile.ZipFile(response, 'w', zipfile.ZIP_DEFLATED) as archive:
            for race_object in queryset:
                race_records = collect_model_records_into_DataFrame(
                    model = models.RaceRecords,
                    inheritance_id = race_object.id,
                    column_of_inheritance_id = "race"
                )
                race_name_as_file_name = race_object.name_of_the_race
                archive.writestr(
                    race_name_as_file_name,
                    race_records.to_csv(
                        None, 
                        index=False, 
                        index_label=False
                    )
                )
               
        return response
    
    # Add new actions to list of actions in the admin
    actions = [
        "export_as_csvs__action",
        "export_info_of_each_instance_as_one_csv__action"
        ]
    export_as_csvs__action.short_description = "Export selected races` records into csv"
    
    # Adding 2 buttons into the Race editing process
    # Template to add buttons to the page
    change_form_template = "race_admin_add_button_changeform.html"
    def response_change(self, request, obj):
        # Button to start race recording
        if "_start_recording" in request.POST:
            obj :models.Race = self.get_queryset(request).get(pk=obj.id)
            obj.date_record_started = datetime.datetime.now()
        
            # Check if the Celery already assigned task if to the race
            if obj.celery_recorder_id == "0":
                # Check for broker connecton b4 sending task
                try:
                    recording_by_celery = recorder.record_race.delay(obj.id)
                except OperationalError:
                    messages.add_message(
                        request, messages.ERROR, 
                        "Recording was not started. Couldn't establish connection with Redis."
                    )
                # Update Race instance in database after successful task sending
                else:
                    obj.is_recorded = True
                    obj.celery_recorder_id = recording_by_celery.id
                    obj.save()
                    messages.add_message(
                        request, messages.INFO, 
                        f"Recording started. Process id is {recording_by_celery.id}"
                    ) 
            else:
                obj.save()
                
                task_to_do_name = recorder.record_race.name
                # Search if Celery has already startdet the task id given 
                celery_object_that_started_recording = TaskResult.objects.filter(
                    task_id = obj.celery_recorder_id, task_name = task_to_do_name
                ).values()
                
                # Send message according to the result of the search
                if len(celery_object_that_started_recording) == 0:
                    messages.add_message(
                        request, messages.INFO, 
                        f"Task to record this race has been given to broker. Celery task id is {obj.celery_recorder_id}."
                    ) 
                else:
                    messages.add_message(
                        request, messages.WARNING, 
                        f"Recording for this race has already started. Celery task id is {obj.celery_recorder_id}."
                    ) 
            return HttpResponseRedirect(".")
        
        # Button to abort race recording
        elif "_abort_recording" in request.POST:
            obj = self.get_queryset(request).get(pk=obj.id)

            # Look if recording started at all
            if obj.celery_recorder_id == "0" or obj.celery_recorder_id == 0:
                obj.celery_recorder_id = "0"
                obj.save()
                messages.add_message(
                    request, messages.INFO, 
                    f"Recording for this race isn't assigned to Celery."
                ) 
            else:
                # Abort task by id written into the race obj
                task_in_progress = recorder.record_race.AsyncResult(
                    obj.celery_recorder_id
                )
                task_in_progress.abort()
                
                # Update Race instance in database after successful task aborting
                obj.celery_recorder_id = "0"
                obj.save()
                messages.add_message(
                    request, messages.INFO, 
                    f"Recording with task id {task_in_progress.id} was aborted."
                )
            return HttpResponseRedirect(".")
            
        return super().response_change(request, obj)

    # Add button to the main Race admin page, that convert csv to RaceRecords
    # Template to add button to the page
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
            for row_index in list(csv_content.iloc[:, 0].index):
                race_record = models.RaceRecords(
                    race = race,
                    team_number = csv_content.at[row_index, "team_number"],
                    pilot_name = csv_content.at[row_index, "pilot_name"],
                    kart = csv_content.at[row_index, "kart"],
                    lap_count = csv_content.at[row_index, "lap_count"],
                    lap_time = csv_content.at[row_index, "lap_time"],
                    s1_time = csv_content.at[row_index, "s1_time"],
                    s2_time = csv_content.at[row_index, "s2_time"],
                    team_segment = csv_content.at[row_index, "team_segment"],
                    true_name = csv_content.at[row_index, "true_name"],
                    true_kart = csv_content.at[row_index, "true_kart"],
                )
                race_record.save()
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
    
# Registration of models 
admin.site.register(models.Race, RaceAdmin)
admin.site.register(models.RaceRecords, RaceRecordsAdmin)

