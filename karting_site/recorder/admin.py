from django.contrib import admin
from django.http import HttpResponse, HttpResponseRedirect

from django_celery_results.models import TaskResult

from . import models
from . import tasks

# Register your models here.
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
            task_to_do_name = tasks.hello.name
            try:
                celery_object_that_started_recording = TaskResult.objects.get(task_id = obj.celery_recorder_id, status = "STARTED", task_name = task_to_do_name)
            except TaskResult.DoesNotExist:
                recording_by_celery = tasks.hello.delay()
                obj.celery_recorder_id = recording_by_celery.id
                message = f"Recording started. Process id is {recording_by_celery.id}"
            else:
                message = f"Recording for this race has already started. Celery working on it {celery_object_that_started_recording.task_id} id"

            self.message_user(request, message)
            obj.save()
            return HttpResponseRedirect(".")
        return super().response_change(request, obj)

admin.site.register(models.Race, RaceAdmin)