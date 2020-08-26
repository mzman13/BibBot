import re
from datetime import datetime
from State import State
from StateMachine import StateMachine
from Bible import bible


class Welcome(State):
    def run(self, event):
        response = "Hi, Welcome to BibBot! I hope I can help you to read the bible every day!"
        return response

    def next(self, event):
        message = event[0]
        self.transitions = {
            message: Planner.menu
        }
        return State.next(self, message)

class Menu(State):
    def run(self, event):
        response = "Please enter the number for the option you want.\n"\
           "1) Start New Reading Plan\n"\
           "2) Get Today's Reading\n"\
           "3) Get Yesterday's Reading\n"\
           "4) Get Tomorrow's Reading"
        return response

    def next(self, event):
        self.transitions = {
            '1': Planner.startPlan,
            '2': Planner.todayReading,
            '3': Planner.yesterdayReading,
            '4': Planner.tomorrowReading
        }
        message = event[0]
        if message not in self.transitions:
            self.transitions = {
                message: Planner.menu
            }
        return State.next(self, message)

class Invalid(State):
    def run(self, event):
        response = "Sorry, I could not process your message. Please try again"
        return response

    def next(self, event):
        return None

class startPlan(State):
    def run(self, event):
        response = "What Book and Chapter are you starting on? (Format should be Book Chp#)"
        return response

    def next(self, event):
        message = event[0].lower()
        plannerContext = event[2]
        if re.match(r"^\w+ \d+$", message):
            plannerContext.currentBook = message.split(' ')[0]
            plannerContext.currentChp = int(message.split(' ')[1])
            message = 1
        else:
            message = 0

        self.transitions = {
            0: Planner.invalid,
            1: Planner.getReadingRate
        }
        return State.next(self, message)

class getReadingRate(State):
    def run(self, event):
        response = "How many chapters will you read a day?"
        return response

    def next(self, event):
        message = event[0]
        plannerContext = event[2]
        if re.match(r"^\d+$", message.lower()):
            message = int(message)
            plannerContext.readingRate = message - 1  # inclusive start, ex: [50, 52]
            plannerContext.setCurrentReading()
            plannerContext.today = datetime.date(datetime.now())
            message = 1
        else:
            message = 0

        self.transitions = {
            0: Planner.invalid,
            1: Planner.planCreated
        }
        return State.next(self, message)

class planCreated(State):
    def run(self, event):
        plannerContext = event[2]
        response = f"Got it! Starting from {plannerContext.currentBook} {plannerContext.currentChp}, the goal is to read {plannerContext.readingRate + 1} chapters every day!"
        return response

    def next(self, event):
        return None

class todayReading(State):
    def run(self, event):
        plannerContext = event[2]
        plannerContext.updateToday()
        response = f"{plannerContext.currentBook} {plannerContext.currentChp} to {plannerContext.nextBook} {plannerContext.nextChp}"
        return response

    def next(self, event):
        return None

class yesterdayReading(State):
    def run(self, event):
        response = "2nd Chronicles 26 - 34"
        return response

    def next(self, event):
        return None

class tomorrowReading(State):
    def run(self, event):
        response = "Ezra 5 -10"
        return response

    def next(self, event):
        return None

class PlannerContext:
    def __init__(self):
        self.readingRate = None
        self.currentBook = None
        self.currentChp = None
        self.nextBook = None
        self.nextChp = None
        self.today = None
        self.yesterday = None
        self.tomorrow = None

    def updateToday(self):
        if datetime.date(datetime.now()) > self.today:
            self.today = datetime.date(datetime.now())
            self.setCurrentReading()

    def setCurrentReading(self):
        if self.currentChp + self.readingRate > bible[self.currentBook]['chapters']:
            self.nextBook = bible[self.currentBook]['next']
            self.nextChp = (self.currentChp + self.readingRate) % bible[self.currentBook]['chapters']
        else:
            self.nextBook = self.currentBook
            self.nextChp = self.currentChp + self.readingRate

class Planner(StateMachine):
    def __init__(self, messengerBot):
        StateMachine.__init__(self, Planner.welcome)
        self.plannerContext = PlannerContext()
        self.bot = messengerBot

    def process(self, event):
        event = (event[0], event[1], self.plannerContext,)
        if self.currentState == Planner.welcome:
            response = self.currentState.run(event)
            self.bot.send_text_message(event[1], response)
        self.currentState = self.currentState.next(event)
        response = self.currentState.run(event)
        self.bot.send_text_message(event[1], response)

        # if no transition states for current state, reset state to menu
        if not self.currentState.next(event):
            self.currentState = Planner.menu
            response = self.currentState.run(event)
            self.bot.send_text_message(event[1], response)


Planner.welcome = Welcome()
Planner.menu = Menu()
Planner.invalid = Invalid()
Planner.startPlan = startPlan()
Planner.getReadingRate = getReadingRate()
Planner.planCreated = planCreated()
Planner.todayReading = todayReading()
Planner.yesterdayReading = yesterdayReading()
Planner.tomorrowReading = tomorrowReading()

