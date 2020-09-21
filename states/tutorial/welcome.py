from State import State
import planner


class Welcome(State):
    def run(self, event):
        plannerContext = event[1]
        response = "Hi, I'm BibBot! Your personal bible reading assistant!\n" \
                   "I hope I can help you to read the bible every day :)\n\n"
        plannerContext.sendMessage(response)
        response = "To start, tell me what timezone you're in (abbreviated)"
        plannerContext.sendMessage(response)

    def next(self, event):
        message = event[0]
        self.transitions = {
            message: planner.Planner.getTimeZoneTutorial
        }
        return State.next(self, message)
