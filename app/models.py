from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app
from flask_login import UserMixin, AnonymousUserMixin
from . import db, login_manager
from datetime import datetime
orders_items = db.Table('orders_items', 
    db.Column('order_id', db.Integer, db.ForeignKey('order.id'), primary_key=True),
    db.Column('item_id', db.Integer, db.ForeignKey('item.id'), primary_key=True)
)

class Permission:
    SCHEDULE = 1
    WRITE = 2
    REGISTRATION = 4
    TOURNAMENT = 8
    ADMIN = 16

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    user = db.relationship('User', backref='role', lazy='dynamic')

    def __init__(self, **kwargs):
        super(Role, self).__init__(**kwargs)
        if self.permissions is None:
            self.permissions = 0


    @staticmethod
    def insert_roles():
        roles = {
            'User' : [Permission.SCHEDULE, Permission.COMMENT],
            'Staff' : [Permission.SCHEDULE, Permission.COMMENT, Permission.REGISTRATION],
            'TournamentManager' : [Permission.SCHEDULE, Permission.COMMENT, Permission.TOURNAMENT],
            'Administrator' : [Permission.SCHEDULE, Permission.COMMENT, Permission.TOURNAMENT, Permission.REGISTRATION, Permission.ADMIN],
        }
        default_role = 'User'
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.reset_permissions()
            for perm in roles[r]:
                role.add_permission(perm)
            role.default = (role.name == default_role)
            db.session.add(role)
        db.session.commit()

    def add_permission(self, perm):
        if not self.has_permission(perm):
            self.permissions += perm

    def remove_permission(self, perm):
        if self.has_permission(perm):
            self.permissions -= perm

    def reset_permissions(self):
        self.permissions = 0

    def has_permission(self, perm):
        return self.permissions & perm == perm

    def __repr__(self):
        return '<Role %r>' % self.name


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    name = db.Column(db.String(64), index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    password_hash = db.Column(db.String(128))
    country = db.Column(db.String(64))
    club = db.Column(db.String(64), nullable=True)
    #dateofbirth = db.Column(db.Date)
    #nextofkin = db.Column(db.String(64), nullable=True)
    #nextofkinphoneemail = db.Column(db.String(64), nullable=True)

    confirmed = db.Column(db.Boolean, default=False)
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    #order = db.relationship('Order', backref='user')

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config['EVENT_ADMIN']:
                self.role = Role.query.filter_by(name='Administrator').first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()
    
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id}).decode('utf-8')

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    def generate_reset_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset': self.id}).decode('utf-8')

    @staticmethod
    def reset_password(token, new_password):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        user = User.query.get(data.get('reset'))
        if user is None:
            return False
        user.password = new_password
        db.session.add(user)
        return True

    def generate_email_change_token(self, new_email, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps(
            {'change_email': self.id, 'new_email': new_email}).decode('utf-8')

    def change_email(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        if data.get('change_email') != self.id:
            return False
        new_email = data.get('new_email')
        if new_email is None:
            return False
        if self.query.filter_by(email=new_email).first() is not None:
            return False
        self.email = new_email
        db.session.add(self)
        return True

    def can(self, perm):
        return self.role is not None and self.role.has_permission(perm)

    def is_administrator(self):
        print(self.role, self.role_id)
        return self.can(Permission.ADMIN)
    
    def __repr__(self):
        return '<User %r>' % self.name

class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False
    
    def is_administrator(self):
        return False

login_manager.anonymous_user = AnonymousUser


class Post(db.Model):
    __tablename__='posts'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128))
    body = db.Column(db.Text)
    timestamp =db.Column(db.DateTime, index=True, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    type_id = db.Column(db.Integer, db.ForeignKey('orgparts.id'))

class Orgpart(db.Model):
    __tablename__ = 'orgparts'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    visible = db.Column(db.Boolean, default=True)

    @staticmethod
    def insert_orgpart(): 
        orgparts = {
            'Tournament': [True],
            'Workshop' : [True],
            'Instructor': [True],
            'Venue' : [True],
            'Rules' : [True],
            'Other_info' : [False],
            'Event' : [True],

        }

        for part in orgparts:
            orgpart = Orgpart.query.filter_by(name=part).first()
            if orgpart is None:
                orgpart = Orgpart(name=part)
            db.session.add(orgpart)
        db.session.commit()

    def __repr__(self):
        return '%r' % self.name

    def __str__(self):
        return self.name

class Event(db.Model):
    __tablename__ = 'event'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    maxparticipants = db.Column(db.Integer)
    participants = db.Column(db.Integer)
    sleepingonsite = db.Column(db.Boolean)
    tournament = db.relationship('Tournament', backref='event')
    workshop = db.relationship('Workshops', backref='event')
    body = db.Column(db.Text)

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
    body = db.Column(db.Text)
    

    def __repr__(self):
        return '<Tournament %r>' % self.name

    def __str__(self):
        return self.name



class Workshops(db.Model):
    __tablename__ = 'workshops'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    year = db.Column(db.Date)
    description = db.Column(db.Text)
    body = db.Column(db.Text)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    

    def __repr__(self):
        return '<Event %r>' % self.name

class Instructors(db.Model):
    __tablename__ = 'instructors'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    body = db.Column(db.Text)

    def __repr__(self):
        return '<Instructor %r>' % self.name


class Product(db.Model):
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
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))


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

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class EventRegistration():
    pass