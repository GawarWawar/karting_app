from django.urls import path

from . import views

app_name = "analyzer"
urlpatterns = [
    path("<race_id>", views.race_analyze, name="analyze_race"),
    path("statistic/<race_id>", views.race_kart_statistic, name="statistic"),
]