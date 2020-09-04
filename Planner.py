import re
from datetime import datetime
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
        plannerContext.bot.send_text_message(event[1], response)

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
                   f"{eight} Tell me a random bible verse!\n"
                    # "6) (TBD) Set/Update a Reminder\n" \
                    # "7) (TBD) Delete Reminder\n" \
        plannerContext.bot.send_text_message(event[1], response)
        return response

    def next(self, event):
        self.transitions = {
            '1': Planner.startPlan,
            '2': Planner.todayReading,
            '3': Planner.tomorrowReading,
            '4': Planner.missedReading,
            '5': Planner.endDate,
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
        plannerContext.logger.info("startPlan run()")
        response = "What Book and Chapter are you starting on?\n(Format should be BookName Chp#)\n" \
                   "To go back, type back"
        plannerContext.bot.send_text_message(event[1], response)
        return response

    def next(self, event):
        message = event[0].lower()
        plannerContext = event[2]
        plannerContext.logger.info("startPlan next()")
        returnCode = 0
        if re.match(r"^\w+ \d+$", message):
            messageValues = message.split(' ')
            # check if book name in bible or if starting chp is <= book's # of chapters
            if messageValues[0] in bible and int(messageValues[1]) <= bible[messageValues[0]]['chapters']:
                plannerContext.currentBook = messageValues[0]
                plannerContext.currentChp = int(messageValues[1])
                plannerContext.nextBook = None
                plannerContext.nextChp = None
                returnCode = 1
            elif messageValues[0] not in bible:
                response = "Sorry, I couldn't find the name of the book you wanted. Did you misspell it?"
                plannerContext.bot.send_text_message(event[1], response)
            elif int(messageValues[1]) > bible[messageValues[0]]['chapters']:
                response = f"Sorry, your starting chapter is more than the number of chapters in {messageValues[0].title()}. Please enter a starting chapter less than {bible[messageValues[0]]['chapters']}"
                plannerContext.bot.send_text_message(event[1], response)
        elif message == 'back':
            pass
        else:
            response = "Sorry, I couldn't understand your response, Please make sure your response follows the format of BookName Chapter#"
            plannerContext.bot.send_text_message(event[1], response)

        self.transitions = {
            0: Planner.menu,
            1: Planner.getReadingRate
        }
        return State.next(self, returnCode)

class getReadingRate(State):
    def run(self, event):
        plannerContext = event[2]
        plannerContext.logger.info("getReadingRate run()")
        response = "How many chapters will you read a day?"
        plannerContext.bot.send_text_message(event[1], response)
        return response

    def next(self, event):
        message = event[0]
        plannerContext = event[2]
        plannerContext.logger.info("getReadingRate next()")
        returnCode = 0
        if re.match(r"^\d+$", message.lower()):
            message = int(message)
            if message > 1189 or message < 1:
                response = "Sorry, Please enter a number between 1 to 1189!"
                plannerContext.bot.send_text_message(event[1], response)
                plannerContext.reset()
            else:
                plannerContext.readingRate = message  # inclusive start, ex: [50, 52]
                plannerContext.setCurrentReading()
                plannerContext.today = datetime.date(datetime.now())
                returnCode = 1
        else:
            response = "Sorry, I couldn't understand your response! Please enter a number!"
            plannerContext.bot.send_text_message(event[1], response)
            plannerContext.reset()

        self.transitions = {
            0: Planner.menu,
            1: Planner.planCreated
        }
        return State.next(self, returnCode)

class planCreated(State):
    def __init__(self):
        self.lastState = True

    def run(self, event):
        plannerContext = event[2]
        response = f"Got it! Starting from {plannerContext.currentBook.title()} {plannerContext.currentChp}, the goal is to read {plannerContext.readingRate} chapters every day!\n\n{plannerContext.getTodayReading()}"
        plannerContext.updateToday()
        plannerContext.bot.send_text_message(event[1], response)
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
        else:
            response = "No reading plan found!\nPlease start a new reading plan!"
        plannerContext.bot.send_text_message(event[1], response)
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
        plannerContext.bot.send_text_message(event[1], response)
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
            response = plannerContext.getEndDateRemainingChps()
        else:
            response = "No reading plan found!\nPlease start a new reading plan!"
        plannerContext.bot.send_text_message(event[1], response)
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
        plannerContext.bot.send_text_message(event[1], response)
        return response

    def next(self, event):
        message = event[0]
        plannerContext = event[2]
        if re.match(r"^\d+$", message.lower()):
            message = int(message)
            if message >= plannerContext.readingRate:
                response = "You read all your chapters for today! Good Job! :)"
                plannerContext.bot.send_text_message(event[1], response)
            elif message < plannerContext.readingRate:
                plannerContext.nextChp = plannerContext.currentChp + message
                plannerContext.nextBook = plannerContext.currentBook
                if plannerContext.nextChp > bible[plannerContext.currentBook]['chapters']:
                    plannerContext.nextBook = bible[plannerContext.currentBook]['next']
                    plannerContext.nextChp = plannerContext.nextChp % bible[plannerContext.currentBook]['chapters']
                response = f"You read {message}/{plannerContext.readingRate} chapters today. Keep up the discipline! You can do it!"
                plannerContext.bot.send_text_message(event[1], response)
        elif message.lower() == 'back':
            pass
        else:
            response = "Sorry, I couldn't understand your response! Please enter a number!"
            plannerContext.bot.send_text_message(event[1], response)

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
        plannerContext.bot.send_text_message(event[1], response)
        return response

    def next(self, event):
        return None

class Planner(StateMachine):
    def __init__(self, messengerBot, logger):
        StateMachine.__init__(self, Planner.welcome)
        self.plannerContext = PlannerContext(messengerBot, logger)

    def process(self, event):
        event = (event[0], event[1], self.plannerContext,)
        self.plannerContext.logger.info(f"Planner {event[0]}- {self.plannerContext}")
        self.plannerContext.logger.info(f"current state - {self.currentState}")
        if self.currentState == Planner.welcome:
            self.currentState.run(event)
        self.currentState = self.currentState.next(event)
        self.plannerContext.logger.info(f"next state - {self.currentState}")
        self.plannerContext.logger.info(f"Planner After {event[0]}, {self.currentState.lastState}- {self.plannerContext}")
        self.currentState.run(event)

        # if no transition states for current state, reset state to menu
        if self.currentState.lastState:
            self.plannerContext.logger.info(f"resetting current state to menu")
            self.currentState = Planner.menu
            self.currentState.run(event)


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
