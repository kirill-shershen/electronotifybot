# -*- coding: utf-8 -*-
from app import db


class UserNotify(db.Model):
    __tablename__ = 'UserNotify'
    ID = db.Column(db.Integer, primary_key=True)
    User_ID = db.Column(db.Integer, index = True, nullable = False)
    City = db.Column(db.Text, index = True, nullable = False)
    Street = db.Column(db.Text, index = True, nullable = False)
    Notify = db.Column(db.Integer, index = True, nullable = False, default = 3)
    outages = db.relationship('ElectroOutage', backref = 'owner', lazy='dynamic')

    def __init__(self, User_ID, City, Street, Notify):
        self.User_ID = User_ID
        self.City = City
        self.Street = Street
        self.Notify = Notify

    def __repr__(self):
        return '<UserNotify %d(%s,%s,%d)>' % (self.User_ID, self.City.encode('utf8'), self.Street.encode('utf8'), self.Notify)

class ElectroOutage(db.Model):
    __tablename__ = 'ElectroOutage'
    ID = db.Column(db.Integer, primary_key=True)
    UserNotify_ID = db.Column(db.Integer, db.ForeignKey('UserNotify.ID'))
    City = db.Column(db.Text, nullable = False)
    Street = db.Column(db.Text, nullable = False)
    Date = db.Column(db.DateTime, nullable = False)
    StrDate = db.Column(db.String(100), nullable = False)
    Reason = db.Column(db.Text, default = '-', nullable = False)

    def __init__(self, UserNotify_ID, City, Street, Date, StrDate, Reason):
        self.UserNotify_ID = UserNotify_ID
        self.City = City
        self.Street = Street
        self.Date = Date
        self.StrDate = StrDate
        self.Reason = Reason

    def __repr__(self):
        return '<ElectroOutage %r>' % (self.UserNotify_ID)

