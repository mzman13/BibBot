import re
from State import State
import planner


class GetAmPm(State):
    def run(self, event):
        plannerContext = event[1]
        response = "Is that 'AM' or 'PM'?\n\n" \
                   "To go back, type back"
        plannerContext.sendMessage(response)

    def next(self, event):
        message = event[0]
        plannerContext = event[1]
        returnCode = 0
        response = ''

        if re.match(r"^(?:am|pm)", message):
            if 'am' in message:
                plannerContext.tempTime += 'am'
            elif 'pm' in message:
                plannerContext.tempTime += 'pm'
            if not plannerContext.setReminder(plannerContext.tempTime):
                response = "Sorry, I couldn't understand your response! Please enter a valid time!"
                returnCode = 2
            else:
                response = f"Okay, I will remind you to read at {plannerContext.reminderTime.strftime('%I:%M %p')} every day!"
        elif message == 'back':
            returnCode = 2
        elif message in ('help', 'menu'):
            plannerContext.printMenu()
            returnCode = 1
        else:
            response = "Sorry, I couldn't understand your response! Please specify if 'AM' or 'PM'!"
            returnCode = 1
        plannerContext.sendMessage(response)

        self.transitions = {
            0: planner.Planner.menu,
            1: planner.Planner.getAmPm,
            2: planner.Planner.setReminder
        }
        return State.next(self, returnCode)
