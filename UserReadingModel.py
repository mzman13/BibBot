from database import db


class UserReading(db.Model):
    __tablename__ = 'UserReading'
    id = db.Column(db.Integer, primary_key=True)
    userId = db.Column(db.String())
    readingRate = db.Column(db.Integer)
    currentBook = db.Column(db.String())
    currentChp = db.Column(db.Integer)
    nextBook = db.Column(db.String())
    nextChp = db.Column(db.Integer)
    today = db.Column(db.Date())
    offset = db.Column(db.Integer)

    def __init__(self, userId):
        self.userId = userId
        self.readingRate = None
        self.currentBook = None
        self.currentChp = None
        self.nextBook = None
        self.nextChp = None
        self.today = None
        self.offset = None

    def __repr__(self):
        return '<id {}>'.format(self.id)
