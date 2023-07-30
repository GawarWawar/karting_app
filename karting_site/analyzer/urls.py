from django.urls import path

from . import views

app_name = "analyzer"
urlpatterns = [
    path("json", views.index_json, name="index"),
    path("<race_id>", views.race_analyze, name="analyze_race"),
    path("statistic/<race_id>", views.race_kart_statistic, name="statistic"),
]