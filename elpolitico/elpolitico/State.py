__author__ = 'Nicole'

import json

GREEN = 'green'
CONSERVATIVE = 'conservative'
LIBERAL = 'liberal'
LIBERTARIAN = 'libertarian'

STATES = [GREEN, CONSERVATIVE, LIBERAL, LIBERTARIAN]


class States:

    def __init__(self):
        self.states = {GREEN: CurrentStateOfParty(GREEN), CONSERVATIVE: CurrentStateOfParty(CONSERVATIVE), LIBERAL: CurrentStateOfParty(LIBERAL), LIBERTARIAN: CurrentStateOfParty(LIBERTARIAN)}
        self.newPoints = list()
        self.existingPoints = list()
        self.totalOldPoints = 0

    def getState(self, party):
        for state in self.states:
            if state.party is party:
                return state

    def passStateToFrontEnd(self):
        pointsToPass = list()
        for point in self.newPoints:
            self.totalOldPoints += 1
            self.existingPoints.append(point)
            # serialize points:
            pointsToPass.append(json.dumps(point))
        # empty the old new points:
        self.newPoints = list()
        return pointsToPass

    def addNewPoint(self, point):
        self.newPoints.append(point)
        state = self.getState(point.party)
        state.percentTotal = state.totalPoints / self.totalOldPoints


class CurrentStateOfParty:
    def __init__(self, party):
        self.party = party
        self.percentTotal = 0
        self.certainty = 0
        self.positivity = 0
        self.totalPoints = 0

    def addNewPoint(self, point):
        self.certainty = (self.certainty * self.totalPoints + point.certainty) / (self.totalPoints + 1)
        self.positivity = (self.positivity * self.totalPoints + point.positivity) / (self.totalPoints + 1)
        self.totalPoints += 1


class StateOfPoint:
    def __init__(self):
        self.newPoint = None
        self.positivity = 0


class NewPoint:
    def __init__(self):
        self.certainty = 0
        self.lat = 0
        self.long = 0
        self.party = None