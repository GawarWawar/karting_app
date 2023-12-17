from django.contrib import admin
from django.urls import path
from django.shortcuts import redirect, render
from django.db.utils import IntegrityError
from django.core.exceptions import ObjectDoesNotExist

from django import forms

import pandas as pd

from . import models

class CsvImportForm(forms.Form):
    csv_file = forms.FileField()


class TempOfPilotsInBRInline(admin.TabularInline):
    model = models.TempOfPilotsInBR
    extra = 0

# Register your models here.
class BigRacesAdmin(admin.ModelAdmin):
    list_display= [
        "name_of_the_race",
        "id",
        "race_class",
        "date_of_race",
    ]
    
    inlines = [
        TempOfPilotsInBRInline
    ]
    
    change_list_template = "veliki_peregoni_changelist.html"    
    
    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('import-csv/', self.import_csv),
        ]
        return my_urls + urls
    
    def import_csv(self, request):
        if request.method == "POST":
            race_name = request.POST["race_name"]
            try:
                race = models.BigRace.objects.get(name_of_the_race = race_name)
            except (IntegrityError, ObjectDoesNotExist):
                race = models.BigRace(name_of_the_race = race_name)
            
            if request.POST["race_class_id"]:
                race_class = models.TypesOfBR.objects.get(pk = request.POST["race_class_id"])
                race.race_class = race_class
            race.save()
            
            csv_file = request.FILES["csv_file"]
            csv_content = pd.read_csv(csv_file)
            for pilot in list(csv_content.loc[:, "pilot_name"].index):
                pilot_name = csv_content.at[pilot, "pilot_name"]
                average_lap_time = csv_content.at[pilot, "average_lap_time"]
                pilot = models.TempOfPilotsInBR(
                    race = race,
                    pilot = pilot_name,
                    average_lap_time = average_lap_time
                )
                pilot.save()
            self.message_user(request, "Your csv file has been imported")
            return redirect("..")
        form = CsvImportForm()
        types_of_races = models.TypesOfBR.objects.all().values()
        payload = {
            "form": form,
            "types_of_races": types_of_races,
        }
        return render(
            request, "csv_form_veliki_peregoni.html", payload
        )
    
class TempOfPilotsInBRAdmin (admin.ModelAdmin):
    list_display = [
        "race",
        "pilot",
        "average_lap_time",
    ]
    
class TypeOfBRAdmin (admin.ModelAdmin):
    list_display = [
        "name_of_the_race_class",
        "id"
    ]
    
admin.site.register(models.BigRace, BigRacesAdmin)
admin.site.register(models.TempOfPilotsInBR, TempOfPilotsInBRAdmin)
admin.site.register(models.TypesOfBR, TypeOfBRAdmin)
