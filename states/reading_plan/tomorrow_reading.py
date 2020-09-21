from State import State


class TomorrowReading(State):
    def __init__(self):
        self.lastState = True

    def run(self, event):
        plannerContext = event[1]
        plannerContext.updateToday()
        if plannerContext.nextChp:
            response = plannerContext.getTomorrowReading()
        else:
            response = "No reading plan found!\nPlease start a new reading plan!"
        plannerContext.sendMessage(response)

    def next(self, event):
        return None
