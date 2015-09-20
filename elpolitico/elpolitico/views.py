from django.core import serializers
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from elpolitico.settings import STATICFILES_DIRS
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect, HttpResponseNotFound, HttpResponseBadRequest
from State import States
import State
import json

def home(request):
    print(STATICFILES_DIRS)
    return render(
        request,
        'index.html'
    )

def party_check(request, party=None):
    if request.method == "POST":
        for state in State.STATES:
            data = States.getState(state)
            data = json.dumps(data)
            return HttpResponse(data)
    return HttpResponseRedirect('/')

def new_points_check(request):
    # return list of new points in the last second
    if request.method == "POST":
        data = States.passStateToFrontEnd()
        data = json.dumps(data)
        return HttpResponse(data)
    return HttpResponseRedirect('/')