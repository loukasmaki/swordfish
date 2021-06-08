from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, BooleanField, SubmitField, TextAreaField, DateField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo
from wtforms import ValidationError
from ..models import User, Role, Orgpart, Tournament
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from .. import db

class EditProfileForm(FlaskForm):
    name = StringField('Name', validators=[Length(0, 64)])
    country = StringField('Country', validators=[Length(0, 64)])
    club = StringField('Club', validators=[Length(0, 64)])
    submit = SubmitField('Submit')

class EditProfileAdminForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Length(1,64), Email()])
    name = StringField('Name', validators=[DataRequired(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z]*$', 0, 'Names must have only letters')])
    confirmed = BooleanField('Confirmed')
    country = StringField('Country', validators=[DataRequired(), Length(1, 64)])
    club = StringField('Club', validators=[DataRequired(), Length(1, 64)])
    role = SelectField('Role', coerce=int)
    submit = SubmitField('Submit')

    def __init__(self, user, *args, **kwargs):
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name) for role in Role.query.order_by(Role.name).all()]
        self.user = user

    def validate_email(self, field):
        if field.data != self.user.email and User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered')

        
class PostForm(FlaskForm):

    def type_choices():
        return db.session.query(Orgpart)



    title = StringField('Title', validators=[DataRequired()])
    orgpart = QuerySelectField('Category', validators=[DataRequired()], 
                                query_factory=type_choices)
    body = TextAreaField('Text', validators=[DataRequired()])
    submit = SubmitField('Submit')


class JoinEventForm(FlaskForm):
    def tournaments():
        return db.session.query(Tournament)

    name = StringField('Name', validators=[DataRequired(), Length(1, 64)])
    email = StringField('Email', validators=[DataRequired(), Length(1,64), Email()])
    date_of_birth = DateField('Date of birth', format='%Y-%m-%d', validators=[DataRequired()])
    tournament1 = QuerySelectField('Tournament 1', validators=[DataRequired()], query_factory=tournaments)
    tournament2 =  QuerySelectField('Tournament 2', validators=[DataRequired()], query_factory=tournaments)
    submit = SubmitField('Submit')
    
