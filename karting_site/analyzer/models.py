from django.db import models
from django.utils import timezone

import datetime
# Create your models here.
class TypesOfVP (models.Model):
    name_of_the_race_class = models.CharField(("Class of the race"), max_length=50, default=None, unique=True)
    
    def __str__(self):
        return self.name_of_the_race_class

class VelikiPeregoni (models.Model):
    name_of_the_race = models.CharField(("Race name"), max_length=50, default=None, null=True)
    race_class = models.ForeignKey(TypesOfVP, to_field="name_of_the_race_class", on_delete=models.CASCADE)
    date_of_race = models.DateField(("Date of race"), auto_now=False, auto_now_add=False, default=timezone.now)
    
    def __str__(self):
        return self.name_of_the_race    
    
class PilotsInVP (models.Model):  
    race = models.ForeignKey(VelikiPeregoni, on_delete=models.CASCADE)
    pilot = models.CharField(("Pilot"), max_length=100)
    average_lap_time = models.FloatField(("Average Lap Time"), default=0)
    
class PilotsRating (models.Model):
    pilot = models.CharField(("Pilot Name"), max_length=50)
    rating = models.FloatField(("Pilot Rating"), default=0)