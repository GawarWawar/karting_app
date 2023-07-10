from django.urls import path

from . import views

app_name = "analyzer"
urlpatterns = [
    path("<race_id>", views.race_analyze, name="analyze_race"),
    #path("json", views.index_json, name="index"),
]