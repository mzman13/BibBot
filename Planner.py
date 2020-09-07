import re
from datetime import datetime, timedelta
from State import State
from StateMachine import StateMachine
from Bible import bible, getRandomVerse
from PlannerContext import PlannerContext


class Welcome(State):
    def run(self, event):
        plannerContext = event[2]
        response = "Hi, I'm BibBot! Your personal bible reading assistant!\n" \
                   "I hope I can help you to read the bible every day :)\n\n" \
                   "First, let's start tracking a new reading plan. Type in 1 to select the first option"
        plannerContext.sendMessage(event[1], response)

    def next(self, event):
        message = event[0]
        self.transitions = {
            message: Planner.menu
        }
        return State.next(self, message)

class Menu(State):
    def run(self, event):
        plannerContext = event[2]
        eight = '8' + u'\u2060' + ')'
        response = "How can I help you?\n(Please enter the number for the option you want)\n"\
                   "1) Start New Reading Plan\n" \
                   "2) Get Today's Reading\n" \
                   "3) Get Tomorrow's Reading\n" \
                   "4) Missed Today's Reading?\n" \
                   "5) Get End Date\n" \
                   "6) Set/Update a Reminder\n" \
                   "7) Delete Reminder\n" \
                   f"{eight} Tell me a random bible verse!\n"
        plannerContext.sendMessage(event[1], response)
        return response

    def next(self, event):
        self.transitions = {
            '1': Planner.startPlan,
            '2': Planner.todayReading,
            '3': Planner.tomorrowReading,
            '4': Planner.missedReading,
            '5': Planner.endDate,
            '6': Planner.setReminder,
            '7': Planner.deleteReminder,
            '8': Planner.getVerse
        }
        message = event[0]
        if message not in self.transitions:
            self.transitions = {
                message: Planner.menu
            }
        return State.next(self, message)

class startPlan(State):
    def run(self, event):
        plannerContext = event[2]
        response = "What Book and Chapter are you starting on?\n(Format should be BookName Chp#)\n" \
                   "To go back, type back"
        plannerContext.sendMessage(event[1], response)
        return response

    def next(self, event):
        message = event[0].lower()
        plannerContext = event[2]
        returnCode = 'back'
        messageValues = message.split(' ')
        if message == 'back':
            pass
        elif re.match(r"^\w+ \d+$", message):
            book = messageValues[0]
            chp = int(messageValues[1])
            book = 'psalms' if book == 'psalm' else book
            returnCode = self.processResponse(plannerContext, book, chp, event[1])
        elif re.match(r"^\d \w+ \d+$", message):
            book = f"{messageValues[0]} {messageValues[1]}"
            chp = int(messageValues[2])
            returnCode = self.processResponse(plannerContext, book, chp, event[1])
        elif re.match(r"^[a-zA-Z]+ [a-zA-Z]+ [a-zA-Z]+ \d+$", message):
            book = f"{messageValues[0]} {messageValues[1]} {messageValues[2]}"
            chp = int(messageValues[3])
            book = 'song of solomon' if book == 'song of songs' else book
            returnCode = self.processResponse(plannerContext, book, chp, event[1])
        else:
            response = "Sorry, I couldn't find the book/chapter you wanted, Please make sure your response follows the format of BookName Chapter#"
            plannerContext.sendMessage(event[1], response)
            returnCode = 0

        self.transitions = {
            0: Planner.startPlan,
            1: Planner.getReadingRate,
            'back': Planner.menu
        }
        return State.next(self, returnCode)

    def processResponse(self, plannerContext, book, chp, userId):
        if book not in bible:
            response = "Sorry, I couldn't find the name of the book you wanted. Did you misspell it?"
            plannerContext.sendMessage(userId, response)
            return 0
        elif chp > bible[book]['chapters']:
            response = f"Sorry, your starting chapter is more than the number of chapters in {book.title()}. Please enter a starting chapter less than {bible[book]['chapters']}"
            plannerContext.sendMessage(userId, response)
            return 0
        # check if book name in bible or if starting chp is <= book's # of chapters
        elif book in bible and chp <= bible[book]['chapters']:
            plannerContext.currentBook = book
            plannerContext.currentChp = chp
            plannerContext.nextBook = None
            plannerContext.nextChp = None
            return 1

class getReadingRate(State):
    def run(self, event):
        plannerContext = event[2]
        response = "How many chapters will you read a day?\n" \
                   "To go back, type back"
        plannerContext.sendMessage(event[1], response)
        return response

    def next(self, event):
        message = event[0]
        plannerContext = event[2]
        returnCode = 0
        if re.match(r"^\d+$", message.lower()):
            message = int(message)
            if message > 1189 or message < 1:
                response = "Sorry, Please enter a number between 1 to 1189!"
                plannerContext.sendMessage(event[1], response)
            else:
                plannerContext.readingRate = message  # inclusive start, ex: [50, 52]
                plannerContext.setCurrentReading()
                plannerContext.today = datetime.date(datetime.now())
                returnCode = 1
        elif message.lower() == 'back':
            returnCode = 'back'
            plannerContext.currentBook = None
            plannerContext.currentChp = None
        else:
            response = "Sorry, I couldn't understand your response! Please enter a positive number!"
            plannerContext.sendMessage(event[1], response)

        self.transitions = {
            0: Planner.getReadingRate,
            1: Planner.planCreated,
            'back': Planner.startPlan
        }
        return State.next(self, returnCode)

class planCreated(State):
    def __init__(self):
        self.lastState = True

    def run(self, event):
        plannerContext = event[2]
        response = f"Got it! Starting from {plannerContext.currentBook.title()} {plannerContext.currentChp}, the goal is to read {plannerContext.readingRate} chapters every day!\n\n{plannerContext.getTodayReading()}"
        plannerContext.updateToday()
        plannerContext.sendMessage(event[1], response)
        return response

    def next(self, event):
        return None

class todayReading(State):
    def __init__(self):
        self.lastState = True

    def run(self, event):
        plannerContext = event[2]
        plannerContext.updateToday()
        if plannerContext.nextChp:
            response = plannerContext.getTodayReading()
            if plannerContext.nextBook == 'done':
                celebrate = u'\U0001F389'
                smile = u'\U0001F601'
                highfive = u'\U0001F64C'
                clap = u'\U0001F44F'
                response = f"Congratulations!!! {celebrate}{celebrate}{celebrate}\nToday is the last day of your reading plan!{smile}{smile}{smile}\nGreat job on making it this far!{highfive}{highfive}{clap}"
        else:
            response = "No reading plan found!\nPlease start a new reading plan!"
        plannerContext.sendMessage(event[1], response)
        return response

    def next(self, event):
        return None

class tomorrowReading(State):
    def __init__(self):
        self.lastState = True

    def run(self, event):
        plannerContext = event[2]
        plannerContext.updateToday()
        if plannerContext.nextChp:
            response = plannerContext.getTomorrowReading()
        else:
            response = "No reading plan found!\nPlease start a new reading plan!"
        plannerContext.sendMessage(event[1], response)
        return response

    def next(self, event):
        return None

class endDate(State):
    def __init__(self):
        self.lastState = True

    def run(self, event):
        plannerContext = event[2]
        plannerContext.updateToday()
        if plannerContext.nextChp:
            remainingChps, remainingDays = plannerContext.getEndDateRemainingChps()
            response = f"{remainingChps} chapters left!\nYou will finish reading the bible in {remainingDays} days on {plannerContext.today + timedelta(days=remainingDays)}"
        else:
            response = "No reading plan found!\nPlease start a new reading plan!"
        plannerContext.sendMessage(event[1], response)
        return response

    def next(self, event):
        return None

class missedReading(State):
    def run(self, event):
        self.lastState = False
        plannerContext = event[2]
        if not plannerContext.nextChp:
            response = "No reading plan found!\nPlease start a new reading plan"
            self.lastState = True
        else:
            response = "How many chapters did you read today?\n" \
                       "To go back, type back"
        plannerContext.sendMessage(event[1], response)
        return response

    def next(self, event):
        message = event[0]
        plannerContext = event[2]
        if re.match(r"^\d+$", message.lower()):
            message = int(message)
            if message >= plannerContext.readingRate:
                response = "You read all your chapters for today! Good Job! :)"
                plannerContext.sendMessage(event[1], response)
            elif message < plannerContext.readingRate:
                plannerContext.nextChp = plannerContext.currentChp + message
                plannerContext.nextBook = plannerContext.currentBook
                if plannerContext.nextChp > bible[plannerContext.currentBook]['chapters']:
                    plannerContext.nextBook = bible[plannerContext.currentBook]['next']
                    plannerContext.nextChp = plannerContext.nextChp % bible[plannerContext.currentBook]['chapters']
                response = f"You read {message}/{plannerContext.readingRate} chapters today. Keep up the discipline! You can do it!"
                plannerContext.sendMessage(event[1], response)
        elif message.lower() == 'back':
            pass
        else:
            response = "Sorry, I couldn't understand your response! Please enter a number!"
            plannerContext.sendMessage(event[1], response)

        self.transitions = {
            message: Planner.menu
        }
        return State.next(self, message)

class getVerse(State):
    def __init__(self):
        self.lastState = True

    def run(self, event):
        plannerContext = event[2]
        response = getRandomVerse()
        plannerContext.sendMessage(event[1], response)
        return response

    def next(self, event):
        return None

class setReminder(State):
    def run(self, event):
        plannerContext = event[2]
        response = "What time would you like to be reminded to read every day?\n" \
                   "(Please specify am/pm next to the time!)\n " \
                   "To go back, type back"
        plannerContext.sendMessage(event[1], response)

    def next(self, event):
        message = event[0]
        plannerContext = event[2]

        if re.match(r"^\d+$", message.lower()):
            # plannerContext.createReminder(message)
            response = "Okay, I will remind you to read at this time every day!"
            plannerContext.sendMessage(event[1], response)
        else:
            response = "Sorry, I couldn't understand your response! Please enter a number!"
            plannerContext.sendMessage(event[1], response)

        self.transitions = {
            message: Planner.menu
        }
        return State.next(self, message)

class deleteReminder(State):
    def run(self, event):
        plannerContext = event[2]
        response = "Are you sure you want to delete your reminder?\n" \
                   "To go back, type back"
        plannerContext.sendMessage(event[1], response)

    def next(self, event):
        message = event[0].lower()
        plannerContext = event[2]

        if message[0] == 'y':
            # plannerContext.deleteReminder()
            response = "Okay, I deleted your reminder!"
        else:
            response = "Okay, I won't delete your reminder"
        plannerContext.sendMessage(event[1], response)

        self.transitions = {
            message: Planner.menu
        }
        return State.next(self, message)

class Planner(StateMachine):
    def __init__(self, messengerBot, logger):
        StateMachine.__init__(self, Planner.welcome)
        self.plannerContext = PlannerContext(messengerBot, logger)

    def process(self, event):
        event = (event[0], event[1], self.plannerContext,)
        # self.plannerContext.logger.info(f"Planner {event[0]}- {self.plannerContext}")
        # self.plannerContext.logger.info(f"current state - {self.currentState}")
        if self.currentState == Planner.welcome:
            self.currentState.run(event)
        self.currentState = self.currentState.next(event)
        # self.plannerContext.logger.info(f"next state - {self.currentState}")
        self.currentState.run(event)

        # if no transition states for current state, reset state to menu
        if self.currentState.lastState:
            # self.plannerContext.logger.info(f"resetting current state to {self.currentState}")
            self.currentState = Planner.menu
            self.currentState.run(event)
        # self.plannerContext.logger.info(f"Planner After {event[0]}, {self.currentState.lastState}- {self.plannerContext}")


Planner.welcome = Welcome()
Planner.menu = Menu()
Planner.startPlan = startPlan()
Planner.getReadingRate = getReadingRate()
Planner.planCreated = planCreated()
Planner.todayReading = todayReading()
Planner.tomorrowReading = tomorrowReading()
Planner.endDate = endDate()
Planner.missedReading = missedReading()
Planner.getVerse = getVerse()
Planner.setReminder = setReminder()
Planner.deleteReminder = deleteReminder()
