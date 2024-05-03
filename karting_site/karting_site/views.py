from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect

def index(request):
    return render(request, "index.html")

def api (request):
    return render(request, "api.html")

def loade_io (request):
    return render(request, "loaderio-7bc48c07cd88559cb85ae4f5ec0ebd7f.html")