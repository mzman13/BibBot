import re
from State import State
import planner


class Menu(State):
    def run(self, event):
        pass

    def next(self, event):
        message = event[0]
        plannerContext = event[1]
        returnCode = message

        if message in ('help', 'menu'):
            plannerContext.printMenu()
        elif re.match(r"^1\W?$", message) or message == 'one':
            returnCode = '1'
        elif re.match(r"^2\W?$", message) or message == 'two':
            returnCode = '2'
        elif re.match(r"^3\W?$", message) or message == 'three':
            returnCode = '3'
        elif re.match(r"^4\W?$", message) or message == 'four':
            returnCode = '4'
        elif re.match(r"^5\W?$", message) or message == 'five':
            returnCode = '5'
        elif re.match(r"^6\W?$", message) or message == 'six':
            returnCode = '6'
        elif re.match(r"^7\W?$", message) or message == 'seven':
            returnCode = '7'
        elif re.match(r"^8\W?$", message) or message == 'eight':
            returnCode = '8'

        self.transitions = {
            '1': planner.startPlan,
            '2': planner.todayReading,
            '3': planner.tomorrowReading,
            '4': planner.missedReading,
            '5': planner.endDate,
            '6': planner.setReminder,
            '7': planner.deleteReminder,
            '8': planner.getVerse,
            'menu': planner.menu,
            'help': planner.menu
        }
        if returnCode not in self.transitions:
            response = "Please select one of the menu options!"
            plannerContext.sendMessage(response)
            self.transitions = {
                returnCode: planner.menu
            }
        return State.next(self, returnCode)
