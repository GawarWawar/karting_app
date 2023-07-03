from django.contrib import admin
from django.urls import path
from django.shortcuts import redirect, render

from django import forms

import pandas as pd

from . import models
# Register your models here.
class VelikiPeregoniAdmin(admin.ModelAdmin):
    list_display= [
        "name_of_the_race",
        "id",
        "race_class",
        "date_of_race",
    ]
    
class CsvImportForm(forms.Form):
    csv_file = forms.FileField()
    
class PilotsInVPAdmin (admin.ModelAdmin):
    change_list_template = "pilots_changelist.html"
    
    list_display = [
        "race",
        "pilot",
        "avarage_lap_time",
    ]
    
    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('import-csv/', self.import_csv),
        ]
        return my_urls + urls

    def import_csv(self, request):
        if request.method == "POST":
            race_id = request.POST["race_id"]
            print(race_id)
            csv_file = request.FILES["csv_file"]
            csv_content = pd.read_csv(csv_file)
            print(csv_content)
            for pilot in csv_content.loc[:, "pilot"].index:
                race = models.VelikiPeregoni.objects.get(pk=race_id)
                pilot = models.PilotsInVP(
                    race = race,
                    pilot = csv_content.at[pilot, "pilot"],
                    avarage_lap_time = csv_content.at[pilot, "avarage_lap_time"]
                )
                pilot.save()
            self.message_user(request, "Your csv file has been imported")
            return redirect("..")
        form = CsvImportForm()
        payload = {"form": form}
        return render(
            request, "csv_form.html", payload
        )
    
class TypeOfVPAdmin (admin.ModelAdmin):
    list_display = [
        "name_of_the_race_class"
    ]
    
admin.site.register(models.VelikiPeregoni, VelikiPeregoniAdmin)
admin.site.register(models.PilotsInVP, PilotsInVPAdmin)
admin.site.register(models.TypesOfVP, TypeOfVPAdmin)
