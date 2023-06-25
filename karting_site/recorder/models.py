from django.db import models

# Create your models here.

class Race(models.Model):
    name_of_the_race = models.CharField(max_length=200)
    publish_time = models.DateTimeField("publish_time")

class RaceRecords(models.Model):
    race = models.ForeignKey(Race, on_delete=models.CASCADE)
    team_number = models.CharField("team", max_length=10)
    pilot_name = models.CharField("pilot_name", max_length=200)
    kart = models.IntegerField("kart", default=0),
    lap_count = models.IntegerField("lap_count")
    lap_time = models.FloatField("lap_time")
    s1_time = models.FloatField("s1_time")
    s2_time = models.FloatField("s2_time")
    team_segment = models.IntegerField("team_segment")
    true_name = models.BooleanField("true_name")
    true_kart = models.BooleanField("true_kart")
    