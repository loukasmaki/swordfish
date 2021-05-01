from flask import Flask, render_template, session, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectMultipleField, DateField, SelectField
from wtforms.validators import DataRequired, Email

from flask_sqlalchemy import SQLAlchemy
import os

#Forms

class JoinEventForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    tournament = SelectMultipleField('Tournaments (hold ctrl to choose more than one)', choices=[("ols", "Open Longsword"), 
    ("wls", "Women's Longsword"), ("sa", "Sabre"), ("wr", "Wrestling"), ("rad", "Rapier & Dagger"), ("sob", "Sword & Buckler")])
    dateOfBirth = DateField("Date of birth")
    country = SelectField('Country', choices=[("sv","Sweden"),("sf", "Finland"),("rus", "Russia")])
    nextOfKin = StringField("Next of Kin")
    nextOfKinPhoneEmail = StringField("Next of kin phone and/or email")
    submit = SubmitField('Submit')


#Initialisation

app = Flask(__name__)
app.config['SECRET_KEY'] = 'ssscccchhuperscheeecreeeet'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://dev:1234@127.0.0.1/sf'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

bootstrap = Bootstrap(app)
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
    pass

@app.route('/participants', methods=['GET'])
def participants(event):
    participants = Tournament.query.filter_by(event=event)

@app.route('/confirmation', methods=['GET'])
def confirmation():
    print(session.get('tournament'))
    return render_template('confirmation.html')


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

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name =db.Column(db.String(64), unique=True)
    user = db.relationship('User', backref='role')

    def __repr__(self):
        return '<Role %r>' % self.name

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    email = db.Column(db.String(64), unique=True)
    country = db.Column(db.String(64))
    nextofkin = db.Column(db.String(64), nullable=True)
    nextofkinphoneemail = db.Column(db.String(64), nullable=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    order = db.relationship('Order', backref='user')

        

    def __repr__(self):
        return '<User %r>' % self.username

class Tournament(db.Model):
    __tablename__ = 'tournaments'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    pools = db.Column(db.Integer)
    maxparticipants = db.Column(db.Integer)
    participants = db.Column(db.Integer)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'))
    

    def __repr__(self):
        return '<Tournament %r>' % self.name

class Event(db.Model):
    __tablename__ = 'events'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    maxparticipants = db.Column(db.Integer)
    participants = db.Column(db.Integer)
    sleepingonsite = db.Column(db.Boolean)
    #tournament = db.relationship('Tournament', backref='tournament')
    workshop = db.relationship('Workshops', backref='workshop')
    

    def __repr__(self):
        return '<Event %r>' % self.name

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


class Merch(db.Model):
    __tablename__ = 'merch'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    productinfo = db.Column(db.Text)
    price = db.Column(db.Float)
    stock = db.Column(db.Integer)


    def __repr__(self):
        return '<Merch %r>' % self.name    

class Orders(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    total = db.Column(db.Float)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Order %r>' % self.name

class Pools(db.Model):
    __tablename__ = 'pools'
    id = db.Column(db.Integer, primary_key=True)
    tournament = db.Column(db.Integer)
    tournament_id = db.Column(db.Integer, db.ForeignKey('tournament.id'))

class Ruleset(db.Model):
    __tablename__ = 'ruleset' 
    id = db.Column(db.Integer, primary_key=True)

