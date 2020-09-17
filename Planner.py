import re, threading, time
from datetime import datetime, timedelta
from State import State
from StateMachine import StateMachine
from Bible import bible, getRandomVerse
from PlannerContext import PlannerContext


def checkYesMessage(message):
    if message[0] == 'y' or message.startswith('sur') or message.startswith('ok') or message.startswith('alright'):
        return True
    else:
        return False

class Welcome(State):
    def run(self, event):
        plannerContext = event[1]
        response = "Hi, I'm BibBot! Your personal bible reading assistant!\n" \
                   "I hope I can help you to read the bible every day :)\n\n"
        plannerContext.sendMessage(response)
        response = "To start, type 'menu' or 'help' to see the menu"
        plannerContext.sendMessage(response)

    def next(self, event):
        message = event[0]
        self.transitions = {
            message: Planner.menuTutorial
        }
        return State.next(self, message)

class MenuTutorial(State):
    def run(self, event):
        pass

    def next(self, event):
        message = event[0]
        plannerContext = event[1]
        returnCode = 0

        if message in ('help', 'menu'):
            plannerContext.printMenu()
            response = "Great job!\nIf you ever need to see the menu, just type 'menu' or 'help'"
            plannerContext.sendMessage(response)
            response = "Now, type in 1 to start a new reading plan"
            returnCode = 1
        else:
            response = "Please enter either 'menu' or 'help'"
        plannerContext.sendMessage(response)

        self.transitions = {
            0: Planner.menuTutorial,
            1: Planner.startPlanTutorial
        }
        return State.next(self, returnCode)

class StartPlanTutorial(State):
    def run(self, event):
        pass

    def next(self, event):
        message = event[0]
        plannerContext = event[1]
        returnCode = 0

        if message == '1':
            returnCode = 1
        else:
            response = "Please type in 1 to start a new reading plan"
            plannerContext.sendMessage(response)

        self.transitions = {
            0: Planner.startPlanTutorial,
            1: Planner.startPlan
        }
        return State.next(self, returnCode)

class Menu(State):
    def run(self, event):
        pass

    def next(self, event):
        message = event[0]
        plannerContext = event[1]
        returnCode = message

        if message in ('help', 'menu'):
            plannerContext.printMenu()
        elif re.match(r"^1\W?$", message) or message == 'one':
            returnCode = '1'
        elif re.match(r"^2\W?$", message) or message == 'two':
            returnCode = '2'
        elif re.match(r"^3\W?$", message) or message == 'three':
            returnCode = '3'
        elif re.match(r"^4\W?$", message) or message == 'four':
            returnCode = '4'
        elif re.match(r"^5\W?$", message) or message == 'five':
            returnCode = '5'
        elif re.match(r"^6\W?$", message) or message == 'six':
            returnCode = '6'
        elif re.match(r"^7\W?$", message) or message == 'seven':
            returnCode = '7'
        elif re.match(r"^8\W?$", message) or message == 'eight':
            returnCode = '8'

        self.transitions = {
            '1': Planner.startPlan,
            '2': Planner.todayReading,
            '3': Planner.tomorrowReading,
            '4': Planner.missedReading,
            '5': Planner.endDate,
            '6': Planner.setReminder,
            '7': Planner.deleteReminder,
            '8': Planner.getVerse,
            'menu': Planner.menu,
            'help': Planner.menu
        }
        if returnCode not in self.transitions:
            response = "Please select one of the menu options!"
            plannerContext.sendMessage(response)
            self.transitions = {
                returnCode: Planner.menu
            }
        return State.next(self, returnCode)

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
            0: Planner.menu,
            1: Planner.startPlan,
            2: Planner.getStartingChapter
        }
        return State.next(self, returnCode)

    def processResponse(self, plannerContext, book):
        if book not in bible:
            response = "Sorry, I couldn't find the name of the book you wanted. Did you misspell it?"
            plannerContext.sendMessage(response)
            return 1
        plannerContext.tempCurrentBook = book
        return 2

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
            0: Planner.startPlan,
            1: Planner.getStartingChapter,
            2: Planner.getReadingRate
        }
        return State.next(self, returnCode)

    def processResponse(self, plannerContext, chp):
        if chp > bible[plannerContext.tempCurrentBook]['chapters']:
            response = f"Sorry, your starting chapter is more than the number of chapters in {plannerContext.tempCurrentBook.title()}. Please enter a starting chapter less than {bible[plannerContext.tempCurrentBook]['chapters']}"
            plannerContext.sendMessage(response)
            return 1
        plannerContext.tempCurrentChp = chp
        return 2

class GetReadingRate(State):
    def run(self, event):
        plannerContext = event[1]
        response = "How many chapters will you read a day?\n\n" \
                   "To go back, type back"
        plannerContext.sendMessage(response)

    def next(self, event):
        message = event[0]
        plannerContext = event[1]
        returnCode = 0

        if re.match(r"^\d+$", message):
            message = int(message)
            if message > 1189 or message < 1:
                response = "Sorry, Please enter a number between 1 to 1189!"
                plannerContext.sendMessage(response)
                returnCode = 1
            else:
                plannerContext.tempReadingRate = message
                returnCode = 2
        elif message == 'back':
            pass
        elif message in ('help', 'menu'):
            plannerContext.printMenu()
            returnCode = 1
        else:
            response = "Sorry, I couldn't understand your response!\nPlease enter a positive number!"
            plannerContext.sendMessage(response)
            returnCode = 1

        self.transitions = {
            0: Planner.getStartingChapter,
            1: Planner.getReadingRate,
            2: Planner.planCreated
        }
        return State.next(self, returnCode)

class PlanCreated(State):
    def run(self, event):
        message = event[0]
        plannerContext = event[1]
        if message not in ('help', 'menu'):     # user might type menu after being asked to set reminder
            plannerContext.currentBook = plannerContext.tempCurrentBook
            plannerContext.currentChp = plannerContext.tempCurrentChp
            plannerContext.nextBook = None
            plannerContext.nextChp = None
            plannerContext.readingRate = plannerContext.tempReadingRate
            plannerContext.today = datetime.date(datetime.now())
            plannerContext.setCurrentReading()
            plannerContext.updateToday()
            response = f"Got it! The goal is to read {plannerContext.readingRate} chapters every day!\n\n{plannerContext.getTodayReading()}"
            plannerContext.sendMessage(response)
        response = "Do you also want to set a reminder?"
        plannerContext.sendMessage(response)

    def next(self, event):
        message = event[0]
        plannerContext = event[1]
        returnCode = 0

        if message in ('help', 'menu'):
            plannerContext.printMenu()
            returnCode = 1
        elif checkYesMessage(message):
            returnCode = 2
        else:
            response = "Finished creating plan"
            plannerContext.sendMessage(response)

        self.transitions = {
            0: Planner.menu,
            1: Planner.planCreated,
            2: Planner.setReminder
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
            if plannerContext.nextBook == 'done':
                plannerContext.sendMessage(response)
                celebrate = u'\U0001F389'
                smile = u'\U0001F601'
                highfive = u'\U0001F64C'
                clap = u'\U0001F44F'
                response = f"Congratulations!!! {celebrate}{celebrate}{celebrate}\nToday's the last day of your reading plan!{smile}{smile}{smile}\nGreat job on making it this far!{highfive}{highfive}{clap}"
        else:
            response = "No reading plan found!\nPlease start a new reading plan!"
        plannerContext.sendMessage(response)

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
        plannerContext.sendMessage(response)

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
        plannerContext.sendMessage(response)

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
                       "To cancel, type cancel"
        plannerContext.sendMessage(response)

    def next(self, event):
        message = event[0]
        plannerContext = event[1]
        returnCode = 0

        if re.match(r"^\d+$", message):
            message = int(message)
            if message >= plannerContext.readingRate:
                response = "You read all your chapters for today! Good Job! :)"
                plannerContext.sendMessage(response)
            elif message < plannerContext.readingRate:
                plannerContext.missedReading(message)
                response = f"You read {message}/{plannerContext.readingRate} chapters today. Keep up the discipline! You can do it!"
                plannerContext.sendMessage(response)
        elif message.lower() == 'cancel':
            plannerContext.sendMessage('cancelled')
        elif message in ('help', 'menu'):
            plannerContext.printMenu()
            returnCode = 1
        else:
            response = "Sorry, I couldn't understand your response!\nPlease enter a number!"
            plannerContext.sendMessage(response)
            returnCode = 1

        self.transitions = {
            0: Planner.menu,
            1: Planner.missedReading
        }
        return State.next(self, returnCode)

class GetVerse(State):
    def __init__(self):
        self.lastState = True

    def run(self, event):
        plannerContext = event[1]
        response = getRandomVerse()
        plannerContext.sendMessage(response)

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
                   "To cancel, type cancel"
        plannerContext.sendMessage(response)

    def next(self, event):
        message = event[0]
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
        elif message == 'cancel':
            plannerContext.sendMessage('cancelled')
        elif message in ('help', 'menu'):
            plannerContext.printMenu()
            returnCode = 1
        else:
            response = "Sorry, I couldn't understand your response! Please enter a valid time!"
            returnCode = 1
        plannerContext.sendMessage(response)

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
        plannerContext.sendMessage(response)

    def next(self, event):
        message = event[0]
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
        elif message in ('help', 'menu'):
            plannerContext.printMenu()
            returnCode = 1
        else:
            response = "Sorry, I couldn't understand your response! Please specify if 'AM' or 'PM'!"
            returnCode = 1
        plannerContext.sendMessage(response)

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
            response = "Are you sure you want to delete your reminder?"
        plannerContext.sendMessage(response)

    def next(self, event):
        message = event[0]
        plannerContext = event[1]
        returnCode = 0

        if message in ('help', 'menu'):
            plannerContext.printMenu()
            response = ''
            returnCode = 1
        elif checkYesMessage(message):
            plannerContext.deleteReminder()
            response = "Okay, I deleted your reminder!"
        else:
            response = "Okay, I won't delete your reminder"
        plannerContext.sendMessage(response)

        self.transitions = {
            0: Planner.menu,
            1: Planner.deleteReminder
        }
        return State.next(self, returnCode)

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
            1: Planner.processReminderResponse
        }
        return State.next(self, returnCode)

class Planner(StateMachine):
    def __init__(self, messengerBot, userId, logger):
        """
        reminderEvent: threading event to signal when to stop the reminder thread
        reminderLock: threading lock to make sure user finishes whatever state they're in before getting reminded
        """
        StateMachine.__init__(self, Planner.welcome)
        self.reminderEvent = threading.Event()
        self.reminderLock = threading.Lock()
        self.plannerContext = PlannerContext(messengerBot, userId, self.reminderEvent, logger)

    def process(self, event):
        if self.currentState != Planner.setReminder:
            self.reminderLock.acquire()


        event = (self.getLowerMessage(event[0]), self.plannerContext,)
        # self.plannerContext.logger.info(f"Planner Before: message - {event[0]}, {self.plannerContext} in {threading.current_thread().name}")
        # self.plannerContext.logger.info(f"current state 1 - {self.currentState}")
        self.checkWelcomeState(event)
        self.currentState = self.currentState.next(event)
        # self.plannerContext.logger.info(f"next state 2 - {self.currentState}")
        self.currentState.run(event)
        self.checkLastState()
        # self.plannerContext.logger.info(f"Planner After: message - {event[0]}, lastState - {self.currentState.lastState}, {self.plannerContext}")
        self.checkSetReminderState()

        if self.reminderLock.locked():
            self.reminderLock.release()

    def getLowerMessage(self, m):
        try:
            message = m.lower()
        except:
            message = m
            if message is None:
                message = ''
        return message

    def checkWelcomeState(self, event):
        if self.currentState == Planner.welcome:
            self.currentState.run(event)

    def checkSetReminderState(self):
        # check if user wants to create reminder and start reminder process
        # self.plannerContext.logger.info(f" {self.plannerContext.reminderCreated}, {self.plannerContext.reminderTime}, {self.reminderEvent.is_set()}")
        if not self.plannerContext.reminderCreated and self.plannerContext.reminderTime:
            self.plannerContext.reminderCreated = True
            self.startReminderThread()

    def checkLastState(self):
        # if no transition states for current state, reset state to menu
        if self.currentState.lastState:
            # self.plannerContext.logger.info(f"resetting current state to {self.currentState}")
            self.currentState = Planner.menu

    def startReminderThread(self):
        t = threading.Thread(target=self.remindUser, name='ThreadReminder', args=[self.plannerContext.reminderTime, self.reminderLock, self.reminderEvent])
        t.start()

    def remindUser(self, reminderTime, reminderLock, reminderEvent):
        """
        wait/sleep for n sec, then remind user and sleep until reminder time
        when user deletes reminder, reminderEvent is set and .wait() will return True and exit loop. Then, unset the event for the next reminder thread
        +60 seconds because will remind user twice if current time still == reminder time
        """
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
Planner.menuTutorial = MenuTutorial()
Planner.startPlanTutorial = StartPlanTutorial()
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
