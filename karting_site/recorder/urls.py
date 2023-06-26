from django.urls import path

from . import views

app_name = "recorder"
urlpatterns = [
    #path("",views.index, name="index"),
    #path("<celery_id>", views.view, name="view"),
    path("races", views.RacesView.as_view(), name="races"),
    path("races/<race_id>/view", views.view, name="view"),
]