"""
URL configuration for karting_site project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include,path
from django.conf import settings
from django.conf.urls.static import static

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path('admin/', admin.site.urls, name="admin"),
    path("recorder/", include("recorder.urls", namespace="recorder")),
    path("analyzer/", include("analyzer.urls", namespace="analyzer")),
    path("api", views.api, name="api"),
    path("api/recorder/", include("recorder.urls_api", namespace="api_recorder")),
    path("api/analyzer/", include("analyzer.urls_api", namespace="api_analyzer")),
    path("loaderio-7bc48c07cd88559cb85ae4f5ec0ebd7f/", views.loade_io, name="loader")
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

admin.site.site_header = "Karting App Admin"
admin.site.site_title = "Karting App Admin Page"
admin.site.index_title = "Welcome to Karting App admin"