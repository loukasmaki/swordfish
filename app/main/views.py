from datetime import datetime
from flask import render_template, session, redirect, url_for
from . import main
#from .forms import JoinEventForm
from .. import db
from ..models import User


@main.route('/', methods=['GET'])
def index():
    return render_template('index.html', current_time=datetime.utcnow())


@main.route('/registration', methods=['GET', 'POST'])
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

        user = User(name=form.name.data,
                     email=form.name.data, 
                     tournament=form.tournament.data, 
                     dateofbirth=form.dateOfBirth.data, 
                     country=form.country.data, 
                     nextofkin=form.nextOfKin.form, 
                     nextofkinphoneemail=form.nextOfKinPhoneEmail.data)
        return redirect(url_for('confirmation'))

    return render_template('main/registration.html', form=form, 
                            name=session.get('name'), 
                            email=session.get('email'), 
                            tournament=session.get('tournament'), 
                            country=session.get('country'), 
                            nextOfKin=session.get('nextOfKin'), 
                            nextOfKinPhoneEmail=session.get('nextOfKinPhoneEmail'), 
                            dateOfBirth=session.get('dateOfBirth'))


@main.route('/fights', methods=['GET'])
def fights():
    return render_template('main/fights.html')

@main.route('/participants', methods=['GET'])
def participants(event):
    participants = Tournament.query.filter_by(event=event)
    return render_template('main/participants.html', participants=participants)

@main.route('/confirmation', methods=['GET'])
def confirmation():
    print(session.get('tournament'))
    return render_template('main/confirmation.html')

@main.route('/information', methods=['GET'])
def information():
    return render_template('main/information.html')


@main.route('/shop')
def shop():
    return render_template('main/shop.html')

