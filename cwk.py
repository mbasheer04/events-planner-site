# import SQLAlchemy
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from werkzeug import security
from flask_login import LoginManager, login_user, logout_user, current_user, login_required
from flask import Flask, render_template, request, session, redirect, url_for 
from db_schema import db, User, Event, UserEvent, dbinit, add_userevent
from flask_mail import Message, Mail
import datetime, random, barcode
from markupsafe import Markup


app = Flask(__name__)
app.secret_key = "test"

#SQLAlchemy and Flask-Mail configurations
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///giginator.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'bmusraf3@gmail.com'
app.config['MAIL_PASSWORD'] = 'altkqanwtglwgoyr'
app.config['MAIL_DEFAULT_SENDER'] = 'bmusraf3@gmail.com'

#Initialise mail to connect with app
mail = Mail(app)
#Initialise database to connect with app
db.init_app(app)

#LoginManager initialisation
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login" #Sets default view to "login" when user is not authenticated

# change this to False to avoid resetting the database every time this app is restarted
resetdb = False
if resetdb:
    with app.app_context():
        # drop everything, create all the tables, then put some data into the tables
        db.drop_all()
        db.create_all()
        dbinit()

#Used to generate the 6-digit random verification code
def generateCode():
    return str(random.randint(100000,999999))

#callback for login manager
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/') #route to the index
def index():
    return render_template('layout.html')

@app.route('/loginform') #route to login page
def loginform():
    return render_template('loginform.html')

@app.route('/register') #route to registration page
def register():
    return render_template('register.html')

@app.route('/mytickets') #route to myTickets page
@login_required
def mytickets():
    tickets = Event.query.join(UserEvent).filter(current_user.id==UserEvent.user_id).\
                    order_by(Event.date,Event.time,Event.eventname) #Retrieve all events that the current user has a ticket of.
    return render_template('mytickets.html',tickets=tickets)

@app.route('/myevents')
@login_required
def myevents():
    events = Event.query.join(UserEvent).filter(current_user.id==UserEvent.user_id,UserEvent.isTicket==False).\
                    order_by(Event.date,Event.time,Event.eventname) #Retrieve all events that are not Tickets
    return render_template('myevents.html',events=events)

@app.route('/browse')
def allevents():
    if current_user.is_authenticated: 
        #Subquery to find all tickets that the user owns
        ownedtickets = UserEvent.query.filter(UserEvent.user_id == current_user.id).with_entities(UserEvent.event_id).subquery()
        #Retrieve all events that the user does not already have a ticket of
        available_events = Event.query.filter(Event.id.notin_(ownedtickets),calcTickets(Event) < Event.capacity).\
                                order_by(Event.date,Event.time,Event.eventname)
        #Retrieve all events that the user already has a ticket of
        booked_events = Event.query.filter(Event.id.in_(ownedtickets),calcTickets(Event) < Event.capacity).\
                                order_by(Event.date,Event.time,Event.eventname)
    else:
        #Retrieve all events that are not sold out
        available_events = Event.query.filter(calcTickets(Event) < Event.capacity).\
                                order_by(Event.date,Event.time,Event.eventname)
        booked_events = [] #Guests cannot have owned tickets so list is empty
    sold_events = Event.query.filter(calcTickets(Event) >= Event.capacity).\
                                order_by(Event.date,Event.time,Event.eventname) #Retrieves all sold out tickets
    return render_template('browse.html',available_events=available_events,
                           booked_events=booked_events,sold_events=sold_events)

def calcTickets(event):
    noTickets = Event.query.join(UserEvent).filter(UserEvent.isTicket==True,UserEvent.event_id==event.id).count()
    return noTickets

#Calculates if an event is nearing capacity
def nearingCapacity(event):
    noTickets = calcTickets(event)
    if noTickets >= (0.95 * event.capacity):
        return True
    return False

#AJAX route for checking availability of an event
@app.route('/check_availability', methods=['GET'])
def check_availability():
    eventname = request.args.get('name')
    event = Event.query.filter(Event.eventname==eventname).first()
    if nearingCapacity(event):
        spaces = event.capacity - calcTickets(event)
        message = f"Only {spaces} tickets remaining"
        return message
    return ""

#AJAX route for generating a barcode
@app.route('/generate_barcode', methods=['GET'])
def generate_barcode():
    eventname = request.args.get('name')
    ticket = UserEvent.query.join(Event).filter(UserEvent.user_id==current_user.id,Event.eventname==eventname).first()
    barcode_class = barcode.get_barcode_class('code128') #Barcode class (code128)
    barcode_data = barcode_class(ticket.serial_number).render() #Renders barcode
    return Markup(barcode_data) #Returns barcode data as markup

@app.route('/addticket', methods=['GET']) #Route for buying a ticket 
def addticket():
    if current_user.is_authenticated:
        eventname = request.args.get('name')
        event = Event.query.filter(Event.eventname == eventname).first()
        if (calcTickets(event) < event.capacity): #Prevents users from buying tickets by URL manipulation when tickets are sold out
            add_userevent(current_user,event,True)
            db.session.commit()
            if nearingCapacity(event): #Sends email to organisers when event is nearing capacity
                organisers = User.query.join(UserEvent).filter(UserEvent.event_id==event.id,UserEvent.isTicket==False)
                with mail.connect() as conn:
                    for organiser in organisers:
                        msg = Message(f"The {eventname} event is nearing capacity.",recipients=[organiser])
                        conn.send(msg)
        return redirect('/mytickets')
    else:
        return redirect('/loginform')

@app.route('/sellticket', methods=['GET']) #Route for selling tickets
@login_required
def sellticket():
    eventname = request.args.get('name')
    event = Event.query.filter(Event.eventname == eventname).first()
    UserEvent.query.filter(UserEvent.event_id==event.id,UserEvent.user_id==current_user.id,UserEvent.isTicket==True).delete()
    db.session.commit()
    return redirect('/mytickets')

@app.route('/create-event', methods=['POST']) #Route for creating an event
@login_required
def create_event():
    eventname = request.form['eventname'] #Form value requests
    date = request.form['date']
    time = request.form['time']
    duration = request.form['duration']
    capacity = request.form['capacity']

    time = str(time) + ":00" #HTML time input tags do not include seconds, so seconds are manually added
    duration = str(duration) + ":00"
    formatted_date = datetime.datetime.strptime(date,"%Y-%m-%d") #Format Date
    time_list = time.split(":") #Separates time String into a list
    formatted_time = datetime.time(int(time_list[0]),int(time_list[1]),int(time_list[2])) #Uses the time constructor by passing in list values
    duration_list = duration.split(":")
    formatted_duration = datetime.time(int(duration_list[0]),int(duration_list[1]),int(duration_list[2]))
    event = Event(eventname,formatted_date,formatted_time,formatted_duration,capacity) #Creates new event
    db.session.add(event)
    db.session.commit() #Required to prevent add_userevent from throwing an error

    add_userevent(current_user,event,False) #Creates a relationship between the organiser and the event 
    db.session.commit()
    return redirect('/myevents')
    
@app.route('/delete-event', methods=['GET']) #Route for deleting events
@login_required
def delete_event():
    eventname = request.args.get('name')
    event = Event.query.filter(Event.eventname == eventname)
    users = User.query.join(UserEvent).filter(UserEvent.event_id==event.first().id)
    with mail.connect() as conn: #Sends email when an event is deleted
        for user in users:
            msg = Message(f"The {eventname} event has been cancelled.", recipients=[user.email])
            conn.send(msg)
    UserEvent.query.filter(UserEvent.event_id==event.first().id).delete()
    event.delete()
    db.session.commit()
    return redirect('/myevents')

@app.route('/class-promotion', methods=['POST']) #Route for promoting an attendee to a Website Organiser
@login_required
def class_promotion():
    username = request.form['username']
    user = User.query.filter(User.username == username).first()
    user.isOrganiser = True #Sets the users status to Organiser
    db.session.commit()
    return redirect('/myevents')

@app.route('/event-promotion', methods=['POST']) #Route for promoting a user to an Organiser for an Event
@login_required
def event_promotion():
    username = request.form['username']
    eventname = request.form['eventname']
    user = User.query.filter(User.username == username).first()
    event = Event.query.filter(Event.eventname == eventname).first()
    add_userevent(user,event,False)
    db.session.commit()
    return redirect('/myevents')

@app.route('/registration', methods=["POST"]) #Route for registration
def registration():
    if request.method=="POST":
        fullname = request.form['fullname']
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        organiserkey = request.form['organiserkey']

    #Checks if username or email already exists
    if (User.query.filter(User.username==username).first() is None) and (User.query.filter(User.email==email).first() is None):
        isOrganiser = False
        if organiserkey == "Dc5_G1gz":
            isOrganiser = True
        hashed = security.generate_password_hash(password) #Hashes password
        verification_code = generateCode() 
        #Dictionary containing the form values
        user = {'fullname':fullname, 
                'username':username,
                'email':email,
                'password':hashed,
                'isOrganiser':isOrganiser
                }
        session['verification_code'] = verification_code
        session['unverified_user'] = user
        session['email'] = email
        
        #Verification email
        msg = Message("To verify your account, use the verification code: " + verification_code,recipients=[email])
        mail.send(msg)

        return render_template('verify_email.html') #Sends user to verification page
    else:
        return redirect('register')
    
@app.route('/verify_email', methods=["POST"]) #Route for submitting email verification form
def verify_email():
    code = request.form['code']
    verification_code = session.get('verification_code')
    if code == verification_code:
        #Create new User
        user = session.get('unverified_user')
        newuser = User(user["fullname"],user["username"],user["password"],user["email"],user["isOrganiser"])
        db.session.add(newuser)
        db.session.commit()
        login_user(User.query.filter_by(username=newuser.username).first()) #Login User
        return redirect('/')
    else:
        return render_template('verify_email.html')

@app.route('/login', methods=["POST","GET"]) #Route for logging in a user
def login():
    if request.method=="POST":
        username = request.form['username']
        password = request.form['password']
    else:
        username = request.args.get('username')
        password = request.args.get('password')
    
    user = User.query.filter_by(username=username).first()
    if(user is not None): #If user exists, check password
        hashed_password = user.password
        verified = security.check_password_hash(hashed_password, password)

        if(verified): #If password is verified, login user
            session['userid'] = user.id
            login_user(user)
            return redirect('/')
        else:
            return redirect('loginform')
    else:
        return redirect('register')

@app.route('/logout') #Route for logging out
def logout():
    session.pop('userid', None)
    logout_user()
    return redirect('/')