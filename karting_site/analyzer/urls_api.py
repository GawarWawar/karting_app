from django.urls import path

from . import views_api

app_name = "analyzer"
urlpatterns = [
    path("analyze_race/<race_id>", views_api.analyze_race_api, name="analyze_race"),
    path("race_statistic/<race_id>", views_api.race_kart_statistic, name="race_statistic"),
]