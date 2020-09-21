import re
from State import State
import planner


class GetTimeZoneTutorial(State):
    def run(self, event):
        message = event[0]
        plannerContext = event[1]
        if message == 'back':
            plannerContext.sendMessage("tell me what timezone you're in (abbreviated)")

    def next(self, event):
        message = event[0]
        plannerContext = event[1]
        returnCode = 0

        if re.match(r"^[a-zA-z]{3}$", message):
            if not plannerContext.setOffSet(message):
                plannerContext.sendMessage("Sorry, I couldn't find your timezone!\nPlease try again")
            else:
                plannerContext.sendMessage("Thanks!")
                plannerContext.sendMessage("Next, type 'menu' or 'help' to see the menu\n\nTo go back, type back")
                returnCode = 1
        else:
            plannerContext.sendMessage("Sorry, I couldn't find your timezone!\nPlease try again")

        self.transitions = {
            0: planner.Planner.getTimeZoneTutorial,
            1: planner.Planner.menuTutorial,
        }
        return State.next(self, returnCode)
