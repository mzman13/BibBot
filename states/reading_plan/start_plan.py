import re
from State import State
import planner


class StartPlan(State):
    def run(self, event):
        plannerContext = event[1]
        response = "What Book are you starting on?\n\n" \
                   "To cancel, type cancel"
        plannerContext.sendMessage(response)

    def next(self, event):
        message = event[0]
        plannerContext = event[1]
        returnCode = 0
        messageValues = message.split(' ')

        if message == 'cancel':
            plannerContext.sendMessage('cancelled')
        elif message in ('help', 'menu'):
            plannerContext.printMenu()
            returnCode = 1
        # match books with no numbers
        elif re.match(r"^[a-zA-Z]+$", message):
            book = messageValues[0]
            book = 'psalms' if book == 'psalm' else book
            returnCode = self.processResponse(plannerContext, book)
        # match books starting with a number
        elif re.match(r"^\d [a-zA-Z]+$", message):
            book = f"{messageValues[0]} {messageValues[1]}"
            returnCode = self.processResponse(plannerContext, book)
        # match 3 worded books
        elif re.match(r"^[a-zA-Z]+ [a-zA-Z]+ [a-zA-Z]+$", message):
            book = f"{messageValues[0]} {messageValues[1]} {messageValues[2]}"
            book = 'song of solomon' if book == 'song of songs' else book
            returnCode = self.processResponse(plannerContext, book)
        else:
            response = "Sorry, I couldn't find the book you wanted, Please enter a valid book in the bible!"
            plannerContext.sendMessage(response)
            returnCode = 1

        self.transitions = {
            0: planner.menu,
            1: planner.startPlan,
            2: planner.getStartingChapter
        }
        return State.next(self, returnCode)

    def processResponse(self, plannerContext, book):
        if book not in plannerContext.bible:
            response = "Sorry, I couldn't find the name of the book you wanted. Did you misspell it?"
            plannerContext.sendMessage(response)
            return 1
        plannerContext.tempCurrentBook = book
        return 2
