import math
from datetime import datetime, timedelta
from Bible import bible


class PlannerContext:
    def __init__(self, messengerBot, logger):
        self.readingRate = None
        self.currentBook = None
        self.currentChp = None
        self.nextBook = None
        self.nextChp = None
        self.today = None
        self.bot = messengerBot
        self.logger = logger

    def __str__(self):
        return f"{self.readingRate} {self.currentBook} {self.currentChp} {self.nextBook} {self.nextChp} {self.today}"

    def updateToday(self):
        if self.today and datetime.date(datetime.now()) > self.today:
            self.today = datetime.date(datetime.now())
            self.setCurrentReading()

    def setCurrentReading(self):
        if self.nextBook and self.nextChp:  # update current book/chp to be previous nextBook/Chp
            self.currentBook = self.nextBook
            self.currentChp = self.nextChp
        self.nextBook, self.nextChp = self._calculateNext(self.currentBook, self.currentChp)

    def getTodayReading(self):
        nextBook = self.nextBook if (self.nextChp > 1) else self.currentBook
        nextChp = (self.nextChp - 1) if (self.nextChp > 1) else bible[self.currentBook]['chapters']
        return f"Today's reading is from {self.currentBook.title()} {self.currentChp} to {nextBook.title()} {nextChp}"

    def getTomorrowReading(self):
        currentBook = self.nextBook
        currentChp = self.nextChp
        nextBook, nextChp = self._calculateNext(currentBook, currentChp)
        nextBook = nextBook if (nextChp > 1) else currentBook
        nextChp = (nextChp - 1) if (nextChp > 1) else bible[currentBook]['chapters']
        return f"Tomorrow's reading is from {currentBook.title()} {currentChp} to {nextBook.title()} {nextChp}"

    def _calculateNext(self, currentBook, currentChp):
        if currentChp + self.readingRate > bible[currentBook]['chapters']:
            total = (currentChp + self.readingRate) - bible[currentBook]['chapters']
            current = currentBook
            while True:
                next = bible[current]['next']
                if bible[next]['chapters'] > total:
                    nextBook = next
                    nextChp = total
                    break
                else:
                    current = next
                    total -= bible[current]['chapters']
        else:
            nextBook = currentBook
            nextChp = currentChp + self.readingRate
        return nextBook, nextChp

    def getEndDateRemainingChps(self):
        remainingChps = 0
        for book, info in bible.items():
            if book == self.nextBook:
                remainingChps += (info['chapters'] - self.nextChp) + 1
            elif remainingChps > 0:
                remainingChps += info['chapters']
        remainingDays = math.ceil(remainingChps / self.readingRate)
        return f"{remainingChps} chapters left!\nYou will finish reading the bible in {remainingDays} days on {self.today + timedelta(days=remainingDays)}"

    def reset(self):
        self.readingRate = None
        self.currentBook = None
        self.currentChp = None
        self.nextBook = None
        self.nextChp = None
        self.today = None
