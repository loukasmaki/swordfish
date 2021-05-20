from flask import render_template, session, redirect, url_for, flash
from flask_login import login_required, current_user
from . import main
from .forms import EditProfileAdminForm, EditProfileForm, PostForm
from .. import db
from ..models import Permission, User, Role, Post, Orgpart
from app.decorators import admin_required


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
        print("Heyooo!")
        print(form.orgpart.data)
        post = Post(body=form.body.data, 
                    author=current_user._get_current_object(),
                    title=form.title.data,
                    type_id=form.orgpart.data)
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('.posts'))
    posts = Post.query.order_by(Post.timestamp.desc()).all()
    
    return render_template('main/admin_post.html', form=form, posts=posts)
