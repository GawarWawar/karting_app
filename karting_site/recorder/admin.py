from django.contrib import admin

from . import models

# Register your models here.
class RaceAdmin(admin.ModelAdmin):
    fields = ["name_of_the_race", "publish_date", "is_recorded"]
    list_display = ["name_of_the_race", "publish_date", "is_recorded"]
    
admin.site.register(models.Race, RaceAdmin)