from django.apps import AppConfig

# Config to add recorder into django apps
class RecorderConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'recorder'
