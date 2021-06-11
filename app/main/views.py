from types import MethodDescriptorType
from flask import render_template, session, redirect, url_for, flash, current_app, request, abort
from flask_login import login_required, current_user
from . import main
from .forms import EditProfileAdminForm, EditProfileForm, JoinEventForm, PostForm
from .. import db
from ..models import Permission, Tournament, User, Role, Post, Orgpart, EventRegistration
from app.decorators import admin_required
import stripe 

from datetime import datetime


@main.route('/', methods=['GET'])
def index():
    posts = Post.query.order_by(Post.timestamp.desc()).all()
    return render_template('index.html', current_time=datetime.utcnow(), posts=posts)


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

@main.route('/workshops', methods=['GET'])
def workshops():
    workshops = Post.query.filter_by(type_id=2)
    return render_template('main/workshops.html') 

@main.route('/fights', methods=['GET'])
def fights():
    return render_template('main/fights.html')

@main.route('/participants', methods=['GET'])
def participants():
    participants = []
    return render_template('main/participants.html', participants=participants)

@main.route('/confirmation', methods=['GET'])
def confirmation():
    print(session.get('tournament'))
    return render_template('main/confirmation.html')

@main.route('/information', methods=['GET'])
def information():
    return render_template('main/information.html')

@main.route('/user/<int:id>')
@login_required
def user(id):
    user = User.query.filter_by(id=id).first_or_404()
    return render_template('main/user.html', user=user)

@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.country = form.country.data
        current_user.club = form.club.data
        db.session.add(current_user._get_current_object())
        db.session.commit()
        flash('Your profile has been updated.')
        return redirect(url_for('.user', id=current_user.id,))
    form.name.data = current_user.name
    form.country.data = current_user.country
    form.club.data = current_user.club
    return render_template('main/edit_profile.html', form=form)

@main.route('/edit-profile/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user=user)
    if form.validate_on_submit():
        user.email = form.email.data
        user.name = form.name.data
        user.confirmed = form.confirmed.data
        user.role = Role.query.get(form.role.data)
        user.country = form.country.data
        user.club = form.club.data
        db.session.add(user)
        db.session.commit()
        flash('The profile has been updated')
        return redirect(url_for('.user', id=user.id))
    form.email.data = user.email
    form.name.data = user.name
    print(user.role.id)
    form.role.data = user.role_id
    form.confirmed.data = user.confirmed
    form.country.data = user.country
    form.club.data = user.club
    return render_template('main/edit_profile.html', form=form, user=user)

@main.route('/posts', methods=['GET', 'POST'])
@login_required
@admin_required
def posts():
    form = PostForm()
    
    if current_user.can(Permission.WRITE) and form.validate_on_submit():
        post = Post(body=form.body.data, 
                    author=current_user._get_current_object(),
                    title=form.title.data,
                    type_id=form.orgpart.data.id)
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('.posts'))
    posts = Post.query.order_by(Post.timestamp.desc()).all()
    
    return render_template('main/admin_post.html', form=form, posts=posts)

@main.route('/join-event', methods=['GET', 'POST'])
def join_event():
    form = JoinEventForm()

    if form.validate_on_submit():
        eventRegistration = EventRegistration(
        name = form.name.data,
        email = form.email.data,
        date_of_birth = form.date_of_birth.data,
        tournament1 = form.tournament1.data,
        tournament2 = form.tournament2.data,
        confirmed = False
        )
        db.session.add(eventRegistration)
        db.session.commit()
        return redirect(url_for('main.payment'))

    return render_template('join-event.html', form=form)


@main.route('/payment', methods=['GET', 'POST'])
#SOmething that verifys it's the current user session here
def payment():
    form = Payment()

    if form.validate_on_submit():
        payment_session = PaymentSession(

            paymentmethod = form.paymentmethod.data,
            


        )

        db.session.add(payment_session)
        db.session.commit()
        return redirect(url_for('main.registration_confirmation'))

    return render_template('payment.html', form=form)

@main.route('/webshop')
def webshop():
    '''
    
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price': 'price_1J02EpCA4AXKnreiLZQq2glE',
            'quantity': 1,
        }],
        mode = 'payment',
        success_url=url_for('.success', _external=True) + '?session_id={CHECKOUT}http://127.0.0.1:5000/success?session_id={CHECKOUT_SESSION_ID}',
        cancel_url=url_for('.webshop', _external=True)

    )
    '''
    
    return render_template('main/webshop.html', #checkout_public_key=current_app.config['STRIPE_PUBLIC_KEY'], 
                                                 #checkout_session_id=session['id']
                         )

@main.route('/success', methods=['GET'])
def success():
    return render_template('/main/success.html')


@main.route('/stripe_pay')
def stripe_pay():
    print('IN STRIPE_PAY FUNCTION')
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price': 'price_1J02EpCA4AXKnreiLZQq2glE',
            'quantity': 1,
        }],
        mode = 'payment',
    success_url=url_for('.success', _external=True) + '?session_id={CHECKOUT_SESSION_ID}',
    cancel_url=url_for('.webshop', _external=True),

    )

    return {'checkout_session_id': session['id'], 
            'checkout_public_key': current_app.config['STRIPE_PUBLIC_KEY']}

@main.route('/stripe_webhook', methods=['POST'])
def stripe_webhook():
    print('WEBHOOK CALLED')

    if request.content_length > 1024 * 1024:
        print('REQUEST TO BIG')
        abort(400)
    payload = request.get_data()
    sig_header = request.environ.get('HTTP_STRIPE_SIGNATURE')
    endpoint_secret = 'whsec_VjrJNq0sh24UYFYfXuOOsZmZjlP3XEBU'
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # Invalid Payload
        print('INVALID PAYLOAD')
        return {}, 400
    except stripe.errorSignatureVerificationError as e:
        print('INVALID SIGNATURE')
        return {}, 400

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        print('Success!!')
        print(session)

    return {},