from django.core import serializers
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from elpolitico.settings import STATICFILES_DIRS
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect, HttpResponseNotFound, HttpResponseBadRequest

def home(request):
    print(STATICFILES_DIRS)
    return render(
        request,
        'index.html'
    )