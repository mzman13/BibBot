import re
from State import State
import planner


class SetReminder(State):
    def run(self, event):
        self.lastState = False
        plannerContext = event[1]
        if plannerContext.reminderCreated:
            response = f"You already have a reminder set at {plannerContext.reminderTime.strftime('%I:%M %p')}!"
            self.lastState = True
        elif not plannerContext.nextChp:
            response = "No reading plan found!\nPlease start a new reading plan"
            self.lastState = True
        else:
            response = "What time should I remind you to read?\n\n" \
                   "To cancel, type cancel"
        plannerContext.sendMessage(response)

    def next(self, event):
        message = event[0]
        plannerContext = event[1]
        returnCode = 0
        response = ''

        if re.match(r"^\d{1,2}:?\d{0,2}\s?((?:AM|PM|am|pm)$|$)", message):
            if 'am' in message or 'pm' in message:
                if not plannerContext.setReminder(message):
                    response = "Sorry, I couldn't understand your response! Please enter a valid time!"
                    returnCode = 1
                else:
                    response = f"Okay, I will remind you to read at {plannerContext.reminderTime.strftime('%I:%M %p')} every day!"
            else:
                plannerContext.setTempReminder(message)
                returnCode = 2
        elif message == 'cancel':
            plannerContext.sendMessage('cancelled')
        elif message in ('help', 'menu'):
            plannerContext.printMenu()
            returnCode = 1
        else:
            response = "Sorry, I couldn't understand your response! Please enter a valid time!"
            returnCode = 1
        plannerContext.sendMessage(response)

        self.transitions = {
            0: planner.Planner.menu,
            1: planner.Planner.setReminder,
            2: planner.Planner.getAmPm
        }
        return State.next(self, returnCode)
