from django.core import serializers
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from elpolitico.settings import STATICFILES_DIRS
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect, HttpResponseNotFound, HttpResponseBadRequest
from MyState import *
import MyState
import json

myStates = None

def home(request):
    print(STATICFILES_DIRS)
    return render(
        request,
        'index.html'
    )

def party_check(request, party=None):
    global myStates
    if myStates is None:
        myStates = MyStates()
    for mystate in myStates.currentStates:
        if mystate.party == party:
            data = mystate.exportToFrontEnd()
            data = json.dumps(data)
            print(data)
            return HttpResponse(data)

def new_points_check(request):
    global myStates
    if myStates is None:
        myStates = MyStates()
    # return list of new points in the last second
    data = myStates.passStateToFrontEnd()
    data = json.dumps(data)
    return HttpResponse(data)