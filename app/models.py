from werkzeug.security import generate_password_hash,  check_password_hash
from . import db

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
    password_hash = db.Column(db.String(128))
    email = db.Column(db.String(64), unique=True)
    country = db.Column(db.String(64))
    dateofbirth = db.Column(db.Date)
    nextofkin = db.Column(db.String(64), nullable=True)
    nextofkinphoneemail = db.Column(db.String(64), nullable=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    
    #order = db.relationship('Order', backref='user')

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)


        

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

