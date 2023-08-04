from django.urls import path

from . import views_api

app_name = "analyzer"
urlpatterns = [
    path("analyze_race/<race_id>", views_api.analyze_race_api, name=""),
]