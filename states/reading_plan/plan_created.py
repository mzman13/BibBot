from datetime import datetime
from State import State
import planner


class PlanCreated(State):
    def run(self, event):
        message = event[0]
        plannerContext = event[1]
        if message not in ('help', 'menu'):     # user might type menu after being asked to set reminder
            plannerContext.currentBook = plannerContext.tempCurrentBook
            plannerContext.currentChp = plannerContext.tempCurrentChp
            plannerContext.nextBook = None
            plannerContext.nextChp = None
            plannerContext.readingRate = plannerContext.tempReadingRate
            plannerContext.today = plannerContext.getOffSetTime(datetime.now()).date()
            plannerContext.setCurrentReading(1)
            plannerContext.updateToday()
            response = f"Got it! The goal is to read {plannerContext.readingRate} chapters every day!\n\n{plannerContext.getTodayReading()}"
            plannerContext.sendMessage(response)
        self.lastState = True
        # response = "Do you also want to set a reminder?"
        # plannerContext.sendMessage(response)

    def next(self, event):
        message = event[0]
        plannerContext = event[1]
        returnCode = 0

        if message in ('help', 'menu'):
            plannerContext.printMenu()
            # returnCode = 1
        # elif planner.checkYesMessage(message):
        #     returnCode = 2
        else:
            response = "Finished creating plan"
            plannerContext.sendMessage(response)

        self.transitions = {
            0: planner.Planner.menu,
            1: planner.Planner.planCreated
            # 2: planner.Planner.setReminder
        }
        return State.next(self, returnCode)
