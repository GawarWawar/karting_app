from django.urls import path

from . import views

app_name = "recorder"
urlpatterns = [
    path("",views.index, name="index"),
    path("races", views.AllRacesPage.as_view(), name="races"),
    path("races/<race_id>/view", views.view_races_records, name="view"),
]