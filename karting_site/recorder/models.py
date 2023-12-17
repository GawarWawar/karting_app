from django.db import models
from django.utils import timezone

import datetime

# Model for the races that contain RaceRecords
class Race(models.Model):
    name_of_the_race = models.CharField(max_length=200)
    publish_date = models.DateTimeField("publish_date", default=timezone.now)
    date_record_started = models.DateTimeField("date_record_started", default=timezone.now)
    date_record_finished = models.DateTimeField("date_record_finished", default=timezone.now)
    was_recorded_complete = models.BooleanField("was_recorded_complete", default=False)
    is_recorded = models.BooleanField("is_recorded", default=False)
    celery_recorder_id = models.CharField(max_length=64, default=0)
    
    def __str__(self):
        return self.name_of_the_race
    
    def to_dict (self):
        race_dict = {
            "id" : self.pk,
            "name_of_the_race" : self.name_of_the_race,
            "publish_date" : self.publish_date.strftime("%m/%d/%Y, %H:%M:%S"),
            "date_record_started" : self.date_record_started.strftime("%m/%d/%Y, %H:%M:%S"),
            "date_record_finished" : self.date_record_finished.strftime("%m/%d/%Y, %H:%M:%S"),
            "was_recorded_complete" : self.was_recorded_complete,
            "is_recorded" : self.is_recorded,
            "celery_recorder_id" : self.celery_recorder_id,
        }
        return(race_dict)

# Each of the RaceRecords contains info about 1 lap of 1 team into particular Race
class RaceRecords(models.Model):
    race = models.ForeignKey(Race, on_delete=models.CASCADE)
    team_number = models.CharField("team_number", max_length=10)
    pilot_name = models.CharField("pilot_name", max_length=200)
    kart = models.IntegerField("kart", default=0)
    lap_count = models.IntegerField("lap_count")
    lap_time = models.FloatField("lap_time")
    s1_time = models.FloatField("s1_time")
    s2_time = models.FloatField("s2_time")
    team_segment = models.IntegerField("team_segment")
    true_name = models.BooleanField("true_name")
    true_kart = models.BooleanField("true_kart")

    def only_race_data_to_dict (self):
        race_record_dict = {
            "team_number" : self.team_number,
            "pilot_name" : self.pilot_name,
            "kart" : self.kart,
            "lap_count" : self.lap_count,
            "lap_time" : self.lap_time,
            "s1_time" : self.s1_time,
            "s2_time" : self.s2_time,
            "team_segment" : self.team_segment,
            "true_name": self.true_name,
            "true_kart": self.true_kart,
        }
        return race_record_dict
    