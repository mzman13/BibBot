import math
import datetime
from bible_manager import Bible
from UserReadingModel import UserReading


class PlannerContext:
    def __init__(self, messengerBot, userId, reminderEvent, logger):
        userData = UserReading.query.filter_by(userId=userId).first()
        if userData:
            self.readingRate = userData.readingRate
            self.currentBook = userData.currentBook
            self.currentChp = userData.currentChp
            self.nextBook = userData.nextBook
            self.nextChp = userData.nextChp
            self.today = userData.today
            self.offset = userData.offset
        else:
            self.readingRate = None
            self.currentBook = None
            self.currentChp = None
            self.nextBook = None
            self.nextChp = None
            self.today = None
            self.offset = None
        self.tempCurrentBook = None
        self.tempCurrentChp = None
        self.tempReadingRate = None
        self.bible = Bible(getChrono=False).bible

        self.userId = userId
        self.bot = messengerBot
        self.logger = logger

        self.reminderCreated = False
        self.reminderTime = None
        self.reminderEvent = reminderEvent

    def __str__(self):
        return f"{{reading rate: {self.readingRate}, " \
               f"currentBook: {self.currentBook}, " \
               f"currentChp: {self.currentChp}, " \
               f"nextBook: {self.nextBook}, " \
               f"nextChp: {self.nextChp}, " \
               f"today: {self.today}, " \
               f"userId: {self.userId}, " \
               f"reminderCreated: {self.reminderCreated}, " \
               f"reminderTime: {self.reminderTime}, " \
               f"offset: {self.offset}}}"

    def sendMessage(self, message):
        self.bot.send_text_message(self.userId, message)

    def updateToday(self):
        now = self.getOffSetTime(datetime.datetime.now()).date()
        if self.today and now > self.today:
            self.today = now
            self.setCurrentReading()

    def setCurrentReading(self):
        if self.nextBook and self.nextChp:  # update current book/chp to be previous nextBook/Chp
            self.currentBook = self.nextBook
            self.currentChp = self.nextChp
        self.nextBook, self.nextChp = self._calculateNext(self.currentBook, self.currentChp)
        self.updateDB()

    def getTodayReading(self):
        if self.nextBook == 'done':
            nextBook = 'revelation'
            nextChp = '22'
        else:
            nextBook = self.nextBook if (self.nextChp > 1) else self.currentBook
            if self.nextChp > 1:
                nextChp = self.nextChp - 1
            else:
                if self.nextBook == 'genesis':
                    nextChp = self.nextChp - 1
                else:
                    nextChp = self.bible[self.currentBook]['chapters']
        return f"Today's reading is from {self.currentBook.title()} {self.currentChp} to {nextBook.title()} {nextChp}"

    def getTomorrowReading(self):
        if self.nextBook == 'done':
            currentBook = self.currentBook
            currentChp = self.currentChp
            nextBook = self.nextBook
        else:
            currentBook = self.nextBook
            currentChp = self.nextChp
            nextBook, nextChp = self._calculateNext(currentBook, currentChp)
            nextBook = nextBook if (nextChp > 1) else currentBook
            nextChp = (nextChp - 1) if (nextChp > 1) else self.bible[currentBook]['chapters']

        if nextBook == 'done':
            nextBook = 'revelation'
            nextChp = '22'
        return f"Tomorrow's reading is from {currentBook.title()} {currentChp} to {nextBook.title()} {nextChp}"

    def _calculateNext(self, currentBook, currentChp):
        if currentChp + self.readingRate > self.bible[currentBook]['chapters']:
            total = (currentChp + self.readingRate) - self.bible[currentBook]['chapters']
            current = currentBook
            while True:
                next = self.bible[current]['next']
                if next == 'done' or self.bible[next]['chapters'] > total:
                    nextBook = next
                    nextChp = total
                    break
                else:
                    current = next
                    total -= self.bible[current]['chapters']
        else:
            nextBook = currentBook
            nextChp = currentChp + self.readingRate
        return nextBook, nextChp

    def missedReading(self, chpsRead):
        self.nextChp = self.currentChp + chpsRead
        self.nextBook = self.currentBook
        if self.nextChp > self.bible[self.currentBook]['chapters']:
            self.nextBook = self.bible[self.currentBook]['next']
            self.nextChp = self.nextChp % self.bible[self.currentBook]['chapters']
        self.updateDB()

    def getEndDateRemainingChps(self):
        # add remaining chapters in current book and remaining books until revelation

        remainingChps = 0
        foundNext = False
        for book, info in self.bible.items():
            if self.nextBook == 'done':
                break
            elif self.nextBook == book:
                remainingChps += (info['chapters'] - self.nextChp) + 1
                foundNext = True
            elif foundNext:
                remainingChps += info['chapters']
        remainingDays = math.ceil(remainingChps / self.readingRate)
        return remainingChps, remainingDays

    def setReminder(self, message):
        try:
            if 'am' in message:
                messageValues = message.split('a')
            elif 'pm' in message:
                messageValues = message.split('p')
            else:
                return False

            if ':' in message:
                formatter = "%I:%M"
            elif len(messageValues[0].rstrip()) <= 2:
                formatter = "%I"
            else:
                # special case if reminder time is 101, 111, 112 read as 10:01
                if len(messageValues[0].rstrip()) == 3 and messageValues[0].startswith('1'):
                    message = '0' + message
                formatter = "%I%M"

            if ' ' in message:
                formatter += ' %p'
            else:
                formatter += '%p'
            self.reminderTime = datetime.datetime.strptime(message, formatter).time()
            return True
        except:
            self.logger.exception("ERROR: could not parse time", exc_info=True)
            return False

    def deleteReminder(self):
        self.reminderCreated = False
        self.reminderTime = None
        self.reminderEvent.set()

    def setTempReminder(self, message):
        self.tempTime = message

    def setOffSet(self, timezone):
        if timezone == 'est':
            self.offset = 60 * 60 * -4
        elif timezone == 'cst':
            self.offset = 60 * 60 * -5
        elif timezone == 'mst':
            self.offset = 60 * 60 * -6
        elif timezone == 'pst':
            self.offset = 60 * 60 * -7
        else:
            return False
        self.updateDB()
        return True

    def getOffSetTime(self, currentDateTime):
        # if utc time ahead of local time, subtract offset from utc time
        if self.offset < 0:
            return currentDateTime - datetime.timedelta(seconds=abs(self.offset))
        # if local time ahead of utc time, add offset to utc time
        else:
            return currentDateTime + datetime.timedelta(seconds=self.offset)

    def printMenu(self):
        eight = '8' + u'\u2060' + ')'
        response = "(Enter the number of the option you want)\n" \
                   "1) Start new reading plan\n" \
                   "2) Get today's reading\n" \
                   "3) Get tomorrow's reading\n" \
                   "4) Missed today's reading?\n" \
                   "5) Get end date\n" \
                   f"{eight} Tell me a random bible verse!\n"
                   # "6) Set reminder\n" \
                   # "7) Delete reminder\n" \
        self.sendMessage(response)

    def updateDB(self):
        userData = UserReading.query.filter_by(userId=self.userId).first()
        userData.readingRate = self.readingRate
        userData.currentBook = self.currentBook
        userData.currentChp = self.currentChp
        userData.nextBook = self.nextBook
        userData.nextChp = self.nextChp
        userData.today = self.today
        userData.offset = self.offset
        from database import db
        db.session.commit()
