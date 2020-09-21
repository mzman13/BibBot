import re
from State import State
import planner


class MissedReading(State):
    def run(self, event):
        self.lastState = False
        plannerContext = event[1]
        if not plannerContext.nextChp:
            response = "No reading plan found!\nPlease start a new reading plan"
            self.lastState = True
        else:
            response = "How many chapters did you read today?\n\n" \
                       "To cancel, type cancel"
        plannerContext.sendMessage(response)

    def next(self, event):
        message = event[0]
        plannerContext = event[1]
        returnCode = 0

        if re.match(r"^\d+$", message):
            message = int(message)
            if message >= plannerContext.readingRate:
                response = "You read all your chapters for today! Good Job! :)"
                plannerContext.sendMessage(response)
            elif message < plannerContext.readingRate:
                plannerContext.missedReading(message)
                response = f"You read {message}/{plannerContext.readingRate} chapters today.\nKeep up the discipline! You can do it!"
                plannerContext.sendMessage(response)
        elif message.lower() == 'cancel':
            plannerContext.sendMessage('cancelled')
        elif message in ('help', 'menu'):
            plannerContext.printMenu()
            returnCode = 1
        else:
            response = "Sorry, I couldn't understand your response!\nPlease enter a number!"
            plannerContext.sendMessage(response)
            returnCode = 1

        self.transitions = {
            0: planner.Planner.menu,
            1: planner.Planner.missedReading
        }
        return State.next(self, returnCode)
