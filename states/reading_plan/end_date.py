from State import State
from datetime import timedelta


class EndDate(State):
    def __init__(self):
        self.lastState = True

    def run(self, event):
        plannerContext = event[1]
        plannerContext.updateToday()
        if plannerContext.nextChp:
            remainingChps, remainingDays = plannerContext.getEndDateRemainingChps()
            response = f"{remainingChps} chapters left!\nYou will finish reading the bible in {remainingDays} days on {plannerContext.today + timedelta(days=remainingDays)}"
        else:
            response = "No reading plan found!\nPlease start a new reading plan!"
        plannerContext.sendMessage(response)

    def next(self, event):
        return None
