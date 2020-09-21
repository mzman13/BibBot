import threading
from datetime import timedelta
from StateMachine import StateMachine
from planner_context import PlannerContext
from states import *


def checkYesMessage(message):
    if message[0] == 'y' or message.startswith('sur') or message.startswith('ok') or message.startswith('alright'):
        return True
    else:
        return False

class Planner(StateMachine):
    welcome = Welcome()
    menuTutorial = MenuTutorial()
    startPlanTutorial = StartPlanTutorial()
    getTimeZoneTutorial = GetTimeZoneTutorial()
    menu = Menu()
    startPlan = StartPlan()
    getStartingChapter = GetStartingChapter()
    getReadingRate = GetReadingRate()
    planCreated = PlanCreated()
    todayReading = TodayReading()
    tomorrowReading = TomorrowReading()
    endDate = EndDate()
    missedReading = MissedReading()
    getVerse = GetVerse()
    setReminder = SetReminder()
    deleteReminder = DeleteReminder()
    processReminderResponse = ProcessReminderResponse()
    getAmPm = GetAmPm()

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
        # self.plannerContext.logger.info(f"current state - {self.currentState}")
        self.checkWelcomeState(event)
        self.currentState = self.currentState.next(event)
        # self.plannerContext.logger.info(f"next state - {self.currentState}")
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
        def calculateSleepTime(plannerContext, reminder, current):
            offSetCurrent = plannerContext.getOffSetTime(current)
            return abs((timedelta(hours=reminder.hour, minutes=reminder.minute)
                        - timedelta(hours=offSetCurrent.hour, minutes=offSetCurrent.minute)).seconds) \
                        + 60

        try:
            sleepTime = calculateSleepTime(self.plannerContext, reminderTime, datetime.now())
            # self.plannerContext.logger.info(f'sleeping for {sleepTime} in {threading.current_thread().name}')

            while not reminderEvent.wait(sleepTime):
                previousState = self.currentState
                event = ('', self.plannerContext, previousState,)
                with reminderLock:
                    # self.plannerContext.logger.info("reminding user now!")
                    self.currentState = Planner.processReminderResponse
                    self.currentState.run(event)

                sleepTime = calculateSleepTime(self.plannerContext, reminderTime, datetime.now())
                # self.plannerContext.logger.info(f"sleeping for {sleepTime} seconds")
        except:
            self.plannerContext.logger.exception("ERROR: could not remind user!", exc_info=True)
        finally:
            reminderEvent.clear()
            # self.plannerContext.logger.info(f"event cleared, killed thread {reminderEvent.is_set()}")
