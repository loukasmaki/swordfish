from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo
from wtforms import ValidationError
from ..models import User


class EditProfileForm(FlaskForm):
    name = StringField('Name', validators=[Length(0, 64)])
    country = StringField('Country', validators=[Length(0, 64)])
    club = StringField('Club', validators=[Length(0, 64)])
    submit = SubmitField('Submit')