from django.urls import path

from . import views_api

app_name = "recorder"
urlpatterns = [
    path("last_race", views_api.last_race_records_api, name="last_race_records_api"),
    path("list_of_all_races", views_api.list_of_all_races_page_api, name="list_of_all_races_page_api")
]