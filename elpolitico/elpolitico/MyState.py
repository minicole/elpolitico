__author__ = 'Nicole'

import json
import random

GREEN = 'green'
CONSERVATIVE = 'conservative'
LIBERAL = 'liberal'
LIBERTARIAN = 'libertarian'
MAX_CACHED_POINTS = 400

STATES = [GREEN, CONSERVATIVE, LIBERAL, LIBERTARIAN]


class MyStates:
    def __init__(self):
        self.currentStates = [CurrentStateOfParty(GREEN), CurrentStateOfParty(CONSERVATIVE), CurrentStateOfParty(LIBERAL), CurrentStateOfParty(LIBERTARIAN)]
        self.newPoints = list()
        self.existingPoints = list()
        self.totalPoints = 0

    def passStateToFrontEnd(self):
        pointsToPass = list()
        for point in self.newPoints:
            self.existingPoints.append(point)
            # serialize points:
            pointsToPass.append(json.dumps(point.newPoint.exportToFrontEnd()))
        # empty the old new points:
        self.newPoints = list()
        return {'newPoints': pointsToPass}

    def addNewPoint(self, point):
        self.newPoints.append(point)
        state = self.getState(point.party)
        self.totalPoints += 1
        state.percentTotal = state.totalPoints / self.totalPoints
        if self.totalPoints >= MAX_CACHED_POINTS:
            self.existingPoints.pop(1)
            self.totalPoints -= 1


class CurrentStateOfParty:
    def __init__(self, party):
        self.party = party
        self.percentTotal = 0
        self.certainty = 0
        self.positivity = 0
        self.totalPoints = 0

    def addNewPoint(self, point):
        self.certainty = (self.certainty * self.totalPoints + point.newPoint.tendency) / (self.totalPoints + 1)
        self.positivity = (self.positivity * self.totalPoints + point.positivity) / (self.totalPoints + 1)
        self.totalPoints += 1

    def exportToFrontEnd(self):
        return {'party': self.party, 'percentTotal': self.percentTotal, 'certainty': self.certainty, 'positivity': self.positivity}

    def exportRandomness(self):
        return {'party': "conservative", 'percentTotal': random.randint(-60,60), 'certainty': random.randint(-60,60), 'positivity': random.randint(-60,60)}


class StateOfPoint:
    def __init__(self):
        self.newPoint = NewPoint()
        self.positivity = 0


class NewPoint:
    def __init__(self):
        self.tendency = 0
        self.lat = 0
        self.long = 0
        self.party = None

    def exportToFrontEnd(self):
        return {"lat": self.lat, "long": self.long, "tendency": self.tendency, "party": self.party}

    def exportRandomness(self):
        return {"lat": random.randint(-60,60), "long": random.randint(-60,60), "tendency": random.randint(-60,60), "party": random.randint(-60,60)}