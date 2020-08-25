import re
from State import State
from StateMachine import StateMachine
from Bible import bible


class Menu(State):
    def run(self):
        response = "Hi, Welcome to BibleBot! Please enter the number for the option you want.\n"\
           "1) Start New Reading Plan\n"\
           "2) Get Today's Reading\n"\
           "3) Get Yesterday's Reading\n"\
           "4) Get Tomorrow's Reading"
        return response

    def next(self, message):
        self.transitions = {
            '2': Planner.todayReading,
            '3': Planner.yesterdayReading,
            '4': Planner.tomorrowReading
        }
        if message not in self.transitions:
            self.transitions = {
                message: Planner.menu
            }
        return State.next(self, message)

class startPlan(State):
    def run(self):
        response = "What Book and Chapter are you starting on? (Format should be Book Chp#)"
        return response

    def next(self, message):
        if re.match(r"^\w+ \d+$", message.lower()):
            message = 1
            self.startBook, self.startChp = message.split(' ')
        else:
            message = 0

        self.transitions = {
            0: Planner.invalid,
            1: Planner.getReadingRate
        }
        return State.next(self, message)

class getReadingRate(State):
    def run(self):
        response = "How many chapters will you read a day?"
        return response

    def next(self, message):
        if re.match(r"^\d+$", message.lower()):
            message = 1
            self.readingRate = message - 1 # inclusive start, ex: [50, 52]
            if self.startChp + self.readingRate > bible[self.startBook]:
                currentBook = bible['nextBook']
                currentChp = (self.startChp + self.readingRate) % bible[self.startBook]
            else:
                currentBook = self.startBook
                currentChp = self.startChp + self.readingRate
            self.today = f"{self.startBook} {self.startChp} to {currentBook} {currentChp}"
        else:
            message = 0

        self.transitions = {
            0: Planner.invalid,
            1: Planner.initializePlan
        }
        return State.next(self, message)

class initializePlan(State):
    def run(self):
        # today = bible[startingBook], startChp: (startChp + readingRate)
        yesterday = ''
        tomorrow = ''

    def next(self, message):
        return None

class todayReading(State):
    def run(self):
        response = "2nd Chronicles 35 - 36, Ezra 1 - 4"
        return response

    def next(self, message):
        return None

class yesterdayReading(State):
    def run(self):
        response = "2nd Chronicles 26 - 34"
        return response

    def next(self, message):
        return None

class tomorrowReading(State):
    def run(self):
        response = "Ezra 5 -10"
        return response

    def next(self, message):
        return None

class Planner(StateMachine):
    def __init__(self, messengerBot):
        StateMachine.__init__(self, Planner.menu)
        self.bot = messengerBot
        self.startBook = None
        self.startChp = None
        self.readingRate = None
        self.today = None
        self.yesterday = None
        self.tomorrow = None

    def process(self, message):
        self.currentState = self.currentState.next(message[0])
        # if
        response = self.currentState.run()
        self.bot.send_text_message(message[1], response)

        # if no transition states for current state, reset state to menu
        if not self.currentState.next(message[0]):
            self.currentState = Planner.menu

Planner.menu = Menu()
Planner.startPlan = startPlan()
Planner.getReadingRate = getReadingRate()
Planner.initializePlan = initializePlan()
Planner.todayReading = todayReading()
Planner.yesterdayReading = yesterdayReading()
Planner.tomorrowReading = tomorrowReading()
