import re, threading, time
from datetime import datetime, timedelta
from State import State
from StateMachine import StateMachine
from Bible import bible, getRandomVerse
from PlannerContext import PlannerContext


class Welcome(State):
    def run(self, event):
        plannerContext = event[1]
        response = "Hi, I'm BibBot! Your personal bible reading assistant!\n" \
                   "I hope I can help you to read the bible every day :)\n\n" \
                   "First, let's start tracking a new reading plan. Type in 1 to select the first option"
        plannerContext.sendMessage(plannerContext.userId, response)

    def next(self, event):
        message = event[0]
        self.transitions = {
            message: Planner.menu
        }
        return State.next(self, message)

class Menu(State):
    def run(self, event):
        plannerContext = event[1]
        eight = '8' + u'\u2060' + ')'
        response = "(Enter the number of the option you want)\n"\
                   "1) Start new reading plan\n" \
                   "2) Get today's reading\n" \
                   "3) Get tomorrow's reading\n" \
                   "4) Missed today's reading?\n" \
                   "5) Get end date\n" \
                   "6) Set/Update a reminder\n" \
                   "7) Delete reminder\n" \
                   f"{eight} Tell me a random bible verse!\n"
        plannerContext.sendMessage(plannerContext.userId, response)

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

class StartPlan(State):
    def run(self, event):
        plannerContext = event[1]
        response = "What Book are you starting on?\n\n" \
                   "To go back, type back"
        plannerContext.sendMessage(plannerContext.userId, response)

    def next(self, event):
        message = event[0].lower()
        plannerContext = event[1]
        returnCode = 0
        messageValues = message.split(' ')

        if message == 'back':
            pass
        elif re.match(r"^[a-zA-Z]+$", message):
            book = messageValues[0]
            book = 'psalms' if book == 'psalm' else book
            returnCode = self.processResponse(plannerContext, book)
        elif re.match(r"^\d [a-zA-Z]+$", message):
            book = f"{messageValues[0]} {messageValues[1]}"
            returnCode = self.processResponse(plannerContext, book)
        elif re.match(r"^[a-zA-Z]+ [a-zA-Z]+ [a-zA-Z]+$", message):
            book = f"{messageValues[0]} {messageValues[1]} {messageValues[2]}"
            book = 'song of solomon' if book == 'song of songs' else book
            returnCode = self.processResponse(plannerContext, book)
        else:
            response = "Sorry, I couldn't find the book you wanted, Please enter a valid book in the bible!"
            plannerContext.sendMessage(plannerContext.userId, response)
            returnCode = 1

        self.transitions = {
            0: Planner.menu,
            1: Planner.startPlan,
            2: Planner.getStartingChapter
        }
        return State.next(self, returnCode)

    def processResponse(self, plannerContext, book):
        if book not in bible:
            response = "Sorry, I couldn't find the name of the book you wanted. Did you misspell it?"
            plannerContext.sendMessage(plannerContext.userId, response)
            return 1
        plannerContext.tempCurrentBook = book
        return 2

class GetStartingChapter(State):
    def run(self, event):
        plannerContext = event[1]
        response = "What Chapter are you starting on?\n\n" \
                   "To go back, type back"
        plannerContext.sendMessage(plannerContext.userId, response)

    def next(self, event):
        message = event[0].lower()
        plannerContext = event[1]
        returnCode = 0
        messageValues = message.split(' ')

        if message == 'back':
            pass
        elif re.match(r"^\d+$", message):
            chp = int(messageValues[0])
            returnCode = self.processResponse(plannerContext, chp)
        else:
            response = "Sorry, I couldn't understand your response. Please enter the starting chapter number!"
            plannerContext.sendMessage(plannerContext.userId, response)
            returnCode = 1

        self.transitions = {
            0: Planner.startPlan,
            1: Planner.getStartingChapter,
            2: Planner.getReadingRate
        }
        return State.next(self, returnCode)

    def processResponse(self, plannerContext, chp):
        if chp > bible[plannerContext.tempCurrentBook]['chapters']:
            response = f"Sorry, your starting chapter is more than the number of chapters in {plannerContext.tempCurrentBook.title()}. Please enter a starting chapter less than {bible[plannerContext.tempCurrentBook]['chapters']}"
            plannerContext.sendMessage(plannerContext.userId, response)
            return 1
        plannerContext.tempCurrentChp = chp
        return 2

class GetReadingRate(State):
    def run(self, event):
        plannerContext = event[1]
        response = "How many chapters will you read a day?\n\n" \
                   "To go back, type back"
        plannerContext.sendMessage(plannerContext.userId, response)

    def next(self, event):
        message = event[0]
        plannerContext = event[1]
        returnCode = 0

        if re.match(r"^\d+$", message.lower()):
            message = int(message)
            if message > 1189 or message < 1:
                response = "Sorry, Please enter a number between 1 to 1189!"
                plannerContext.sendMessage(plannerContext.userId, response)
                returnCode = 1
            else:
                plannerContext.tempReadingRate = message  # inclusive start, ex: [50, 52]
                returnCode = 2
        elif message.lower() == 'back':
            pass
        else:
            response = "Sorry, I couldn't understand your response! Please enter a positive number!"
            plannerContext.sendMessage(plannerContext.userId, response)
            returnCode = 1

        self.transitions = {
            0: Planner.getStartingChapter,
            1: Planner.getReadingRate,
            2: Planner.planCreated
        }
        return State.next(self, returnCode)

class PlanCreated(State):
    def run(self, event):
        plannerContext = event[1]
        plannerContext.currentBook = plannerContext.tempCurrentBook
        plannerContext.currentChp = plannerContext.tempCurrentChp
        plannerContext.nextBook = None
        plannerContext.nextChp = None
        plannerContext.readingRate = plannerContext.tempReadingRate
        plannerContext.today = datetime.date(datetime.now())
        plannerContext.setCurrentReading()
        plannerContext.updateToday()
        response = f"Got it! The goal is to read {plannerContext.readingRate} chapters every day!\n\n{plannerContext.getTodayReading()}"
        plannerContext.sendMessage(plannerContext.userId, response)
        response = "Do you also want to set a reminder?"
        plannerContext.sendMessage(plannerContext.userId, response)

    def next(self, event):
        message = event[0].lower()
        plannerContext = event[1]
        returnCode = 0

        if message[0] == 'y':
            returnCode = 1

        self.transitions = {
            0: Planner.menu,
            1: Planner.setReminder
        }
        return State.next(self, returnCode)

class TodayReading(State):
    def __init__(self):
        self.lastState = True

    def run(self, event):
        plannerContext = event[1]
        plannerContext.updateToday()
        if plannerContext.nextChp:
            response = plannerContext.getTodayReading()
            plannerContext.sendMessage(plannerContext.userId, response)
            if plannerContext.nextBook == 'done':
                celebrate = u'\U0001F389'
                smile = u'\U0001F601'
                highfive = u'\U0001F64C'
                clap = u'\U0001F44F'
                response = f"Congratulations!!! {celebrate}{celebrate}{celebrate}\nToday's the last day of your reading plan!{smile}{smile}{smile}\nGreat job on making it this far!{highfive}{highfive}{clap}"
        else:
            response = "No reading plan found!\nPlease start a new reading plan!"
        plannerContext.sendMessage(plannerContext.userId, response)

    def next(self, event):
        return None

class TomorrowReading(State):
    def __init__(self):
        self.lastState = True

    def run(self, event):
        plannerContext = event[1]
        plannerContext.updateToday()
        if plannerContext.nextChp:
            response = plannerContext.getTomorrowReading()
        else:
            response = "No reading plan found!\nPlease start a new reading plan!"
        plannerContext.sendMessage(plannerContext.userId, response)

    def next(self, event):
        return None

class EndDate(State):
    def __init__(self):
        self.lastState = True

    def run(self, event):
        plannerContext = event[1]
        plannerContext.updateToday()
        if plannerContext.nextChp:
            remainingChps, remainingDays = plannerContext.getEndDateRemainingChps()
            response = f"{remainingChps} chapters left!\nYou will finish reading the bible in {remainingDays} days on {plannerContext.today + timedelta(days=remainingDays)}"
        else:
            response = "No reading plan found!\nPlease start a new reading plan!"
        plannerContext.sendMessage(plannerContext.userId, response)

    def next(self, event):
        return None

class MissedReading(State):
    def run(self, event):
        self.lastState = False
        plannerContext = event[1]
        if not plannerContext.nextChp:
            response = "No reading plan found!\nPlease start a new reading plan"
            self.lastState = True
        else:
            response = "How many chapters did you read today?\n\n" \
                       "To go back, type back"
        plannerContext.sendMessage(plannerContext.userId, response)

    def next(self, event):
        message = event[0]
        plannerContext = event[1]
        returnCode = 1
        if re.match(r"^\d+$", message.lower()):
            message = int(message)
            if message >= plannerContext.readingRate:
                response = "You read all your chapters for today! Good Job! :)"
                plannerContext.sendMessage(plannerContext.userId, response)
            elif message < plannerContext.readingRate:
                plannerContext.missedReading(message)
                response = f"You read {message}/{plannerContext.readingRate} chapters today. Keep up the discipline! You can do it!"
                plannerContext.sendMessage(plannerContext.userId, response)
        elif message.lower() == 'back':
            pass
        else:
            response = "Sorry, I couldn't understand your response! Please enter a number!"
            plannerContext.sendMessage(plannerContext.userId, response)
            returnCode = 0

        self.transitions = {
            0: Planner.missedReading,
            1: Planner.menu
        }
        return State.next(self, returnCode)

class GetVerse(State):
    def __init__(self):
        self.lastState = True

    def run(self, event):
        plannerContext = event[1]
        response = getRandomVerse()
        plannerContext.sendMessage(plannerContext.userId, response)

    def next(self, event):
        return None

class SetReminder(State):
    def run(self, event):
        self.lastState = False
        plannerContext = event[1]
        if plannerContext.reminderCreated:
            response = f"You already have a reminder set at {plannerContext.reminderTime.strftime('%I:%M %p')}!"
            self.lastState = True
        elif not plannerContext.nextChp:
            response = "No reading plan found!\nPlease start a new reading plan"
            self.lastState = True
        else:
            response = "What time should I remind you to read?\n\n" \
                   "To go back, type back"
        plannerContext.sendMessage(plannerContext.userId, response)

    def next(self, event):
        message = event[0].lower()
        plannerContext = event[1]
        returnCode = 0
        response = ''

        if re.match(r"^\d{1,2}:?\d{0,2}\s?((?:AM|PM|am|pm)$|$)", message):
            if 'am' in message or 'pm' in message:
                if not plannerContext.setReminder(message):
                    response = "Sorry, I couldn't understand your response! Please enter a valid time!"
                    returnCode = 1
                else:
                    response = f"Okay, I will remind you to read at {plannerContext.reminderTime.strftime('%I:%M %p')} every day!"
            else:
                plannerContext.setTempReminder(message)
                returnCode = 2
        elif message == 'back':
            pass
        else:
            response = "Sorry, I couldn't understand your response! Please enter a valid time!"
            returnCode = 1
        plannerContext.sendMessage(plannerContext.userId, response)

        self.transitions = {
            0: Planner.menu,
            1: Planner.setReminder,
            2: Planner.getAmPm
        }
        return State.next(self, returnCode)

class GetAmPm(State):
    def run(self, event):
        plannerContext = event[1]
        response = "Is that 'AM' or 'PM'?\n\n" \
                   "To go back, type back"
        plannerContext.sendMessage(plannerContext.userId, response)

    def next(self, event):
        message = event[0].lower()
        plannerContext = event[1]
        returnCode = 0
        response = ''

        if re.match(r"^(?:am|pm)", message):
            if 'am' in message:
                plannerContext.tempTime += 'am'
            elif 'pm' in message:
                plannerContext.tempTime += 'pm'
            if not plannerContext.setReminder(plannerContext.tempTime):
                response = "Sorry, I couldn't understand your response! Please enter a valid time!"
                returnCode = 2
            else:
                response = f"Okay, I will remind you to read at {plannerContext.reminderTime.strftime('%I:%M %p')} every day!"
        elif message == 'back':
            returnCode = 2
        else:
            response = "Sorry, I couldn't understand your response! Please specify if 'AM' or 'PM'!"
            returnCode = 1
        plannerContext.sendMessage(plannerContext.userId, response)

        self.transitions = {
            0: Planner.menu,
            1: Planner.getAmPm,
            2: Planner.setReminder
        }
        return State.next(self, returnCode)

class DeleteReminder(State):
    def run(self, event):
        self.lastState = False
        plannerContext = event[1]
        if not plannerContext.reminderCreated:
            response = "No reminder to delete!"
            self.lastState = True
        else:
            response = "Are you sure you want to delete your reminder?\n\n" \
                        "To go back, type back"
        plannerContext.sendMessage(plannerContext.userId, response)

    def next(self, event):
        message = event[0].lower()
        plannerContext = event[1]

        if message[0] == 'y':
            plannerContext.deleteReminder()
            response = "Okay, I deleted your reminder!"
        else:
            response = "Okay, I won't delete your reminder"
        plannerContext.sendMessage(plannerContext.userId, response)

        self.transitions = {
            message: Planner.menu
        }
        return State.next(self, message)

class ProcessReminderResponse(State):
    def run(self, event):
        plannerContext = event[1]
        response = "******REMINDER TIME!******\n" \
                   "Did you do today's reading? [Yes/No]"
        plannerContext.sendMessage(plannerContext.userId, response)
        self.previousState = event[2]

    def next(self, event):
        message = event[0].lower()
        plannerContext = event[1]
        if message[0] != 'y':
            response = "It's Ok! Keep up the discipline! You can do it!"
            plannerContext.missedReading(0)
        else:
            response = "Great Job! :D"
        plannerContext.sendMessage(plannerContext.userId, response)
        return self.previousState

class Planner(StateMachine):
    def __init__(self, messengerBot, userId, logger):
        StateMachine.__init__(self, Planner.welcome)
        self.reminderEvent = threading.Event()
        self.reminderLock = threading.Lock()
        self.plannerContext = PlannerContext(messengerBot, userId, self.reminderEvent, logger)

    def process(self, event):
        if self.currentState != Planner.setReminder:
            self.reminderLock.acquire()

        event = (event[0], self.plannerContext,)
        # self.plannerContext.logger.info(f"Planner Before: message - {event[0]}, {self.plannerContext} in {threading.current_thread().name}")
        # self.plannerContext.logger.info(f"current state 1 - {self.currentState}")
        self.checkWelcomeState(event)
        self.currentState = self.currentState.next(event)
        # self.plannerContext.logger.info(f"next state 2 - {self.currentState}")
        self.currentState.run(event)
        self.checkLastState(event)
        # self.plannerContext.logger.info(f"Planner After: message - {event[0]}, lastState - {self.currentState.lastState}, {self.plannerContext}")
        self.checkSetReminderState()

        if self.reminderLock.locked():
            self.reminderLock.release()

    def checkWelcomeState(self, event):
        if self.currentState == Planner.welcome:
            self.currentState.run(event)

    def checkSetReminderState(self):
        # check if user wants to create reminder and start reminder process
        # self.plannerContext.logger.info(f" {self.plannerContext.reminderCreated}, {self.plannerContext.reminderTime}, {self.reminderEvent.is_set()}")
        if not self.plannerContext.reminderCreated and self.plannerContext.reminderTime:
            self.plannerContext.reminderCreated = True
            self.startReminderThread()

    def checkLastState(self, event):
        # if no transition states for current state, reset state to menu
        if self.currentState.lastState:
            # self.plannerContext.logger.info(f"resetting current state to {self.currentState}")
            self.currentState = Planner.menu
            self.currentState.run(event)

    def startReminderThread(self):
        t = threading.Thread(target=self.remindUser, name='ThreadReminder', args=[self.plannerContext.reminderTime, self.reminderLock, self.reminderEvent])
        t.start()

    def remindUser(self, reminderTime, reminderLock, reminderEvent):
        """+60 seconds because will remind user twice if current time still == reminder time"""
        try:

            current = datetime.now().time()
            sleepTime = abs((timedelta(hours=self.plannerContext.reminderTime.hour, minutes=self.plannerContext.reminderTime.minute)
                             - timedelta(hours=current.hour, minutes=current.minute)).seconds) + 60
            # self.plannerContext.logger.info(f'sleeping for {sleepTime} in {threading.current_thread().name}')
            while not reminderEvent.wait(sleepTime):
                previousState = self.currentState
                event = ('', self.plannerContext, previousState,)
                with reminderLock:
                    self.currentState = Planner.processReminderResponse
                    self.currentState.run(event)

                current = datetime.now().time()
                sleepTime = abs((timedelta(hours=reminderTime.hour, minutes=reminderTime.minute)
                                 - timedelta(hours=current.hour, minutes=current.minute)).seconds) + 60
                # self.plannerContext.logger.info(f"sleeping for {sleepTime} seconds")
        except:
            self.plannerContext.logger.exception("ERROR: could not remind user!", exc_info=True)
        finally:
            reminderEvent.clear()
            # self.plannerContext.logger.info(f"event cleared, killed thread {reminderEvent.is_set()}")

Planner.welcome = Welcome()
Planner.menu = Menu()
Planner.startPlan = StartPlan()
Planner.getStartingChapter = GetStartingChapter()
Planner.getReadingRate = GetReadingRate()
Planner.planCreated = PlanCreated()
Planner.todayReading = TodayReading()
Planner.tomorrowReading = TomorrowReading()
Planner.endDate = EndDate()
Planner.missedReading = MissedReading()
Planner.getVerse = GetVerse()
Planner.setReminder = SetReminder()
Planner.deleteReminder = DeleteReminder()
Planner.processReminderResponse = ProcessReminderResponse()
Planner.getAmPm = GetAmPm()
