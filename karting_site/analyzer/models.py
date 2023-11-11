from django.db import models
from django.utils import timezone

import datetime
# Create your models here.
class TypesOfBR (models.Model):
    name_of_the_race_class = models.CharField(("Class of the race"), max_length=50, default=None, unique=True)
    
    def __str__(self):
        return self.name_of_the_race_class

class BigRace (models.Model):
    name_of_the_race = models.CharField(("Race name"), max_length=50, default=None, null=True)
    race_class = models.ForeignKey(TypesOfBR, to_field="name_of_the_race_class", on_delete=models.CASCADE)
    date_of_race = models.DateField(("Date of race"), auto_now=False, auto_now_add=False, default=timezone.now)
    
    def __str__(self):
        return self.name_of_the_race    
    
class TempOfPilotsInBR (models.Model):  
    race = models.ForeignKey(BigRace, on_delete=models.CASCADE)
    pilot = models.CharField(("Pilot"), max_length=100)
    average_lap_time = models.FloatField(("Average Lap Time"), default=0)
    
class PilotsRating (models.Model):
    pilot = models.CharField(("Pilot Name"), max_length=50)
    rating = models.FloatField(("Pilot Rating"), default=0)