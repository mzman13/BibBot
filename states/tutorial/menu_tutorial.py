from State import State
import planner


class MenuTutorial(State):
    def run(self, event):
        pass

    def next(self, event):
        message = event[0]
        plannerContext = event[1]
        returnCode = 0

        if message in ('help', 'menu'):
            plannerContext.printMenu()
            plannerContext.sendMessage("Great job!\nIf you ever need to see the menu, just type 'menu' or 'help'")
            plannerContext.sendMessage("Now, type in 1 to start a new reading plan")
            returnCode = 2
        elif message == 'back':
            returnCode = 1
        else:
            plannerContext.sendMessage("Please enter either 'menu' or 'help'")

        self.transitions = {
            0: planner.Planner.menuTutorial,
            1: planner.Planner.getTimeZoneTutorial,
            2: planner.Planner.startPlanTutorial
        }
        return State.next(self, returnCode)
