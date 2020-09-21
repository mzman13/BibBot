import re
from State import State
import planner


class GetStartingChapter(State):
    def run(self, event):
        plannerContext = event[1]
        response = "What Chapter are you starting on?\n\n" \
                   "To go back, type back"
        plannerContext.sendMessage(response)

    def next(self, event):
        message = event[0]
        plannerContext = event[1]
        returnCode = 0
        messageValues = message.split(' ')

        if message == 'back':
            pass
        elif message in ('help', 'menu'):
            plannerContext.printMenu()
            returnCode = 1
        elif re.match(r"^\d+$", message):
            chp = int(messageValues[0])
            returnCode = self.processResponse(plannerContext, chp)
        else:
            response = "Sorry, I couldn't understand your response. Please enter the starting chapter number!"
            plannerContext.sendMessage(response)
            returnCode = 1

        self.transitions = {
            0: planner.startPlan,
            1: planner.getStartingChapter,
            2: planner.getReadingRate
        }
        return State.next(self, returnCode)

    def processResponse(self, plannerContext, chp):
        if chp > plannerContext.bible[plannerContext.tempCurrentBook]['chapters']:
            response = f"Sorry, your starting chapter is more than the number of chapters in {plannerContext.tempCurrentBook.title()}. Please enter a starting chapter less than {plannerContext.bible[plannerContext.tempCurrentBook]['chapters']}"
            plannerContext.sendMessage(response)
            return 1
        plannerContext.tempCurrentChp = chp
        return 2
