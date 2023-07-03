from django.contrib import admin

from . import models
# Register your models here.
class VelikiPeregoniAdmin(admin.ModelAdmin):
    list_display= [
        "name_of_the_race",
        "race_class",
        "date_of_race",
    ]
    
    
class PilotsInVPAdmin (admin.ModelAdmin):
    list_display = [
       
    ]
    
class TypeOfVPAdmin (admin.ModelAdmin):
    list_display = [
        "name_of_the_race_class"
    ]
    
admin.site.register(models.VelikiPeregoni, VelikiPeregoniAdmin)
admin.site.register(models.PilotsInVP, PilotsInVPAdmin)
admin.site.register(models.TypesOfVP, TypeOfVPAdmin)
