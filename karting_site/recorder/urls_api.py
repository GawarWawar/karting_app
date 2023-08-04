from django.urls import path

from . import views_api

app_name = "recorder"
urlpatterns = [
    path("last_race", views_api.last_race_records_api, name="index"),
]