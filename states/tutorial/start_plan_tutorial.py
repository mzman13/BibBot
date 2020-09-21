from State import State
import planner


class StartPlanTutorial(State):
    def run(self, event):
        pass

    def next(self, event):
        message = event[0]
        plannerContext = event[1]
        returnCode = 0

        if message == '1':
            returnCode = 1
        else:
            response = "Please type in 1 to start a new reading plan"
            plannerContext.sendMessage(response)

        self.transitions = {
            0: planner.startPlanTutorial,
            1: planner.startPlan
        }
        return State.next(self, returnCode)
