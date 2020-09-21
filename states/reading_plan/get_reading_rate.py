import re
from State import State
import planner


class GetReadingRate(State):
    def run(self, event):
        plannerContext = event[1]
        response = "How many chapters will you read a day?\n\n" \
                   "To go back, type back"
        plannerContext.sendMessage(response)

    def next(self, event):
        message = event[0]
        plannerContext = event[1]
        returnCode = 0

        if re.match(r"^\d+$", message):
            message = int(message)
            if message > 1189 or message < 1:
                response = "Sorry, Please enter a number between 1 to 1189!"
                plannerContext.sendMessage(response)
                returnCode = 1
            else:
                plannerContext.tempReadingRate = message
                returnCode = 2
        elif message == 'back':
            pass
        elif message in ('help', 'menu'):
            plannerContext.printMenu()
            returnCode = 1
        else:
            response = "Sorry, I couldn't understand your response!\nPlease enter a positive number!"
            plannerContext.sendMessage(response)
            returnCode = 1

        self.transitions = {
            0: planner.Planner.getStartingChapter,
            1: planner.Planner.getReadingRate,
            2: planner.Planner.planCreated
        }
        return State.next(self, returnCode)
