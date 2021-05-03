from flask import Flask, render_template, session, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectMultipleField, DateField, SelectField
from wtforms.validators import DataRequired, Email
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from threading import Thread

import os

#Forms

class JoinEventForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    tournament = SelectMultipleField('Tournaments (hold ctrl to choose more than one)', choices=[
                                     ("ols", "Open Longsword"), 
                                     ("wls", "Women's Longsword"), 
                                     ("sa", "Sabre"), 
                                     ("wr", "Wrestling"), 
                                     ("rad", "Rapier & Dagger"), 
                                     ("sob", "Sword & Buckler")])
    dateOfBirth = DateField("Date of birth")
    country = SelectField('Country', choices=[("sv","Sweden"),
                                              ("sf", "Finland"),
                                              ("rus", "Russia")])
    nextOfKin = StringField("Next of Kin")
    nextOfKinPhoneEmail = StringField("Next of kin phone and/or email")
    submit = SubmitField('Submit')


#Initialisation

app = Flask(__name__)
app.config['SECRET_KEY'] = 'ssscccchhuperscheeecreeeet'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://dev:1234@127.0.0.1/sf'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')

app.config['EVENT_MAIL_SUBJECT_PREFIX'] = "[Swordfish]"
app.config['EVENT_MAIL_SENDER'] = 'Event Admin <devporco@gmail.com>'

db = SQLAlchemy(app)

bootstrap = Bootstrap(app)
mail = Mail(app)
moment = Moment(app)


#Routes

@app.route('/')
def index():
    return render_template('index.html', current_time=datetime.utcnow())

@app.route('/user/<name>')
def user(name):
    return render_template('user.html', name=name)

@app.route('/registration', methods=['GET', 'POST'])
def registration():
    form = JoinEventForm()
    if form.validate_on_submit():
        session['name'] = form.name.data
        session['email'] = form.email.data
        session['tournament'] = form.tournament.data
        session['dateOfBirth'] = form.dateOfBirth.data
        session['country'] = form.country.data        
        session['nextOfKin'] = form.nextOfKin.data
        session['nextOfKinPhoneEmail'] = form.nextOfKinPhoneEmail.data

        user = User=(name=form.name.data,
                     email=form.name.data, 
                     tournament=form.tournament.data, 
                     dateofbirth=form.dateOfBirth.data, 
                     country=form.country.data, 
                     nextofkin=form.nextOfKin.form, 
                     nextofkinphoneemail=form.nextOfKinPhoneEmail.data)
        return redirect(url_for('confirmation'))

    return render_template('registration.html', form=form, 
                            name=session.get('name'), 
                            email=session.get('email'), 
                            tournament=session.get('tournament'), 
                            country=session.get('country'), 
                            nextOfKin=session.get('nextOfKin'), 
                            nextOfKinPhoneEmail=session.get('nextOfKinPhoneEmail'), 
                            dateOfBirth=session.get('dateOfBirth'))

@app.route('/fights', methods=['GET'])
def fights():
    return render_template('fights.html')

@app.route('/participants', methods=['GET'])
def participants(event):
    participants = Tournament.query.filter_by(event=event)
    return render_template('participants.html', participants=participants)

@app.route('/confirmation', methods=['GET'])
def confirmation():
    print(session.get('tournament'))
    return render_template('confirmation.html')

@app.route('/information', methods=['GET'])
def information():
    return render_template('information.html')


@app.route('/shop')
def shop():
    return render_template('shop.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


#Database

orders_items = db.Table('orders_items', 
    db.Column('order_id', db.Integer, db.ForeignKey('order.id'), primary_key=True),
    db.Column('item_id', db.Integer, db.ForeignKey('item.id'), primary_key=True)
)


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name =db.Column(db.String(64), unique=True)
    user = db.relationship('User', backref='role')

    def __repr__(self):
        return '<Role %r>' % self.name

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    email = db.Column(db.String(64), unique=True)
    country = db.Column(db.String(64))
    dateofbirth = db.Column(db.Date)
    nextofkin = db.Column(db.String(64), nullable=True)
    nextofkinphoneemail = db.Column(db.String(64), nullable=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    
    order = db.relationship('Order', backref='user')


        

    def __repr__(self):
        return '<User %r>' % self.username

class Event(db.Model):
    __tablename__ = 'event'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    maxparticipants = db.Column(db.Integer)
    participants = db.Column(db.Integer)
    sleepingonsite = db.Column(db.Boolean)
    tournament = db.relationship('Tournament', backref='event')
    workshop = db.relationship('Workshops', backref='event')
    

    def __repr__(self):
        return '<Event %r>' % self.name

class Tournament(db.Model):
    __tablename__ = 'tournament'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    pools = db.Column(db.Integer)
    maxparticipants = db.Column(db.Integer)
    participants = db.Column(db.Integer)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'))
    

    def __repr__(self):
        return '<Tournament %r>' % self.name



class Workshops(db.Model):
    __tablename__ = 'workshops'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    year = db.Column(db.Date)
    description = db.Column(db.Text)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'))
    

    def __repr__(self):
        return '<Event %r>' % self.name

class Instructors(db.Model):
    __tablename__ = 'instructors'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    bio = db.Column(db.Text)

    def __repr__(self):
        return '<Instructor %r>' % self.name


class Item(db.Model):
    __tablename__ = 'item'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    productinfo = db.Column(db.Text)
    price = db.Column(db.Float)
    stock = db.Column(db.Integer)


    def __repr__(self):
        return '<Merch %r>' % self.name    

class Orders(db.Model):
    __tablename__ = 'order'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    items = db.relationship('Item', secondary=orders_items, lazy='subquery', backref=db.backref('orders', lazy=True))
    total = db.Column(db.Float)
    registration_order = db.Column(db.Boolean, default=False)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


    def __repr__(self):
        return '<Order %r>' % self.name

class Pools(db.Model):
    __tablename__ = 'pools'
    id = db.Column(db.Integer, primary_key=True)
    tournament = db.Column(db.Integer)
    tournament_id = db.Column(db.Integer, db.ForeignKey('tournament.id'))
    
    def __repr__(self):
        return '<Pools %r>' % self.name

class Ruleset(db.Model):
    __tablename__ = 'ruleset' 
    id = db.Column(db.Integer, primary_key=True)

    def __repr__(self):
        return '<Ruleset %r>' % self.name

#Functions
## Mail

def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)

def send_email(to, subject, template, **kwargs):
    msg = Message(app.config['EVENT_MAI_SUBJECT_PREFIX'] + subject,
            sender=app.config['EVENT_MAIL_SENDER'], recipients=[to])
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)
    thr = Thread(tartget=send_async_email, args=[app, msg])
    thr.start()
    return thr

# 