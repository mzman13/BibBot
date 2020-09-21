from State import State
import planner


class ProcessReminderResponse(State):
    def run(self, event):
        plannerContext = event[1]
        response = "******REMINDER TIME!******\n" \
                   "Did you do today's reading? [Yes/No]"
        plannerContext.sendMessage(response)
        self.previousState = event[2]

    def next(self, event):
        message = event[0]
        plannerContext = event[1]
        returnCode = 0

        if message in ('help', 'menu'):
            plannerContext.printMenu()
            response = ''
            returnCode = 1
        elif message[0] != 'y':
            response = "It's ok! Keep up the discipline! You can do it!"
            plannerContext.missedReading(0)
        else:
            response = "Great Job! :D"
        plannerContext.sendMessage(response)

        self.transitions = {
            0: self.previousState,
            1: planner.processReminderResponse
        }
        return State.next(self, returnCode)
