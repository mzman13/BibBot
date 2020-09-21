from State import State
from bible_manager import getRandomVerse


class GetVerse(State):
    def __init__(self):
        self.lastState = True

    def run(self, event):
        plannerContext = event[1]
        response = getRandomVerse()
        plannerContext.sendMessage(response)

    def next(self, event):
        return None
