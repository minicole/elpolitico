from django.core import serializers
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from elpolitico.settings import STATICFILES_DIRS
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect, HttpResponseNotFound, HttpResponseBadRequest
from MyState import *
import MyState
import threading
from observer import *
import json

myStates = None

TwitterThread = None

KeywordThread = None

Testy = "A"

def getMyStates():
    global myStates
    if myStates is None:
        myStates = MyStates()
    return myStates

def init_workers():
    global KeywordThread
    global TwitterThread

    time.sleep(60)

    if KeywordThread is None or not KeywordThread.isAlive():
        KeywordThread = threading.Thread(target=KeywordUpdateThread)
        KeywordThread.start()

    if TwitterThread is None or not TwitterThread.isAlive():
        TwitterThread = threading.Thread(target=TwitterUpdateThread())
        TwitterThread.start()
# end init_workers


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
            return HttpResponse(data)
    return HttpResponseRedirect('/')

def new_points_check(request):
    global myStates
    if myStates is None:
        myStates = MyStates()
    # return list of new points in the last second
    data = myStates.passStateToFrontEnd()
    data = json.dumps(data)
    return HttpResponse(data)