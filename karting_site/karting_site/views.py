from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect

def index(request):
    return render(request, "index.html")

def api (request):
    return render(request, "api.html")