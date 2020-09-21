from State import State
import planner


class DeleteReminder(State):
    def run(self, event):
        self.lastState = False
        plannerContext = event[1]
        if not plannerContext.reminderCreated:
            response = "No reminder to delete!"
            self.lastState = True
        else:
            response = "Are you sure you want to delete your reminder?"
        plannerContext.sendMessage(response)

    def next(self, event):
        message = event[0]
        plannerContext = event[1]
        returnCode = 0

        if message in ('help', 'menu'):
            plannerContext.printMenu()
            response = ''
            returnCode = 1
        elif planner.checkYesMessage(message):
            plannerContext.deleteReminder()
            response = "Okay, I deleted your reminder!"
        else:
            response = "Okay, I won't delete your reminder"
        plannerContext.sendMessage(response)

        self.transitions = {
            0: planner.Planner.menu,
            1: planner.Planner.deleteReminder
        }
        return State.next(self, returnCode)
