from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
import datetime
import random

# create the database interface
db = SQLAlchemy()

# a model of a user for the database
class User(UserMixin,db.Model):
    __tablename__='users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    fullname = db.Column(db.String(50))
    username = db.Column(db.String(20), unique=True)
    password = db.Column(db.String(200))
    email = db.Column(db.String(50), unique=True)
    isOrganiser = db.Column(db.Boolean)
    events = db.relationship("UserEvent")

    def __init__(self, fullname, username, password, email, isOrganiser):  
        self.fullname=fullname
        self.username=username
        self.password=password
        self.email=email
        self.isOrganiser=isOrganiser

class Event(db.Model):
    __tablename__='events'
    id = db.Column(db.Integer, primary_key=True)
    eventname = db.Column(db.String(50))
    date = db.Column(db.Date)
    time = db.Column(db.Time)
    duration = db.Column(db.Time)
    capacity = db.Column(db.Integer)
    users = db.relationship('UserEvent')
    
    def __init__(self,eventname,date,time,duration,capacity):  
        self.eventname=eventname
        self.date=date
        self.time=time
        self.duration=duration
        self.capacity=capacity

# Association table between Users and Events 
class UserEvent(db.Model): 
    __tablename__='user_events'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), primary_key=True)
    isTicket = db.Column(db.Boolean)
    serial_number = db.Column(db.String(9),unique=True)

    def __init__(self, user_id, event_id, isTicket):
        self.user_id = user_id
        self.event_id = event_id
        self.isTicket = isTicket
        self.serial_number = str(random.randint(0,999999999))

def add_userevent(user,event,isTicket):
    new_userevent = UserEvent(user.id,event.id,isTicket)
    user.events.append(new_userevent)
    event.users.append(new_userevent)
    db.session.add(new_userevent)

# put some data into the tables
def dbinit():
    users = [User("user","user1","123","user1@",True),
    User("user","user2","123","user2@",True),
    User("user","user3","123","user3@",False),
    User("user","user4","123","user4@",False),
    User("user","user5","123","user5@",False),
    User("user","user6","123","user6@",False),
    User("user","user7","123","user7@",False),
    User("user","user8","123","user8@",False),
    User("user","user9","123","user9@",False),
    User("user","user10","123","user10@",False),
    User("user","user11","123","user11@",False),
    User("user","user12","123","user12@",False),
    User("user","user13","123","user13@",False),
    User("user","user14","123","user14@",False),
    User("user","user15","123","user15@",False),
    User("user","user16","123","user16@",False),
    User("user","user17","123","user17@",False),
    User("user","user18","123","user18@",False),
    User("user","user19","123","user19@",False),
    User("user","user20","123","user20@",False),
    User("user","user21","123","user21@",False),
    User("user","user22","123","user22@",False),
    User("user","user23","123","user23@",False)]

    db.session.add_all(users)

    event1 = Event("DCS Annual General Meeting",datetime.date.today(),datetime.time(3,2,2),datetime.time(3,2,2),25)
    event2 = Event("CS118 Revision",datetime.date.today(),datetime.time(3,4,5),datetime.time(1,2,3),12000)
    event3 = Event("CS126 Revision",datetime.date.today(),datetime.time(3,2,2),datetime.time(3,2,2),12000)
    event4 = Event("CS130 Revision",datetime.date.today(),datetime.time(3,4,5),datetime.time(1,2,3),12000)
    event5 = Event("CS131 Revision",datetime.date.today(),datetime.time(3,2,2),datetime.time(3,2,2),12000)
    event6 = Event("CS132 Revision",datetime.date.today(),datetime.time(3,4,5),datetime.time(1,2,3),12000)
    event6 = Event("CS133 Revision",datetime.date.today(),datetime.time(3,4,5),datetime.time(1,2,3),12000)
    event6 = Event("CS139 Revision",datetime.date.today(),datetime.time(3,4,5),datetime.time(1,2,3),12000)

    db.session.add_all([event1,event2,event3,event3,event4,event5,event6])
    db.session.commit()
    
    for user in users:
        add_userevent(user,event1,True)

    # commit all the changes to the database file
    db.session.commit()
