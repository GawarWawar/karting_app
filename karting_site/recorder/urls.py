from django.urls import path

from . import views

app_name = "recorder"
urlpatterns = [
    # Link to page, that will display last race
    path("",views.recorder_starting_page, name="index"),
    # Link to page, that displays List of all races
    path("races", views.AllRacesPage.as_view(), name="races"),
    # Link to page, that displays info and all records about particular race
    path("races/<race_id>/view", views.view_race_records_by_id, name="view"),
]