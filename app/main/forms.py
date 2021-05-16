from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo
from wtforms import ValidationError
from ..models import User, Role


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
    postclass = SelectField('Orgparts', coerce=int)
    body = TexAreaField('Text', validators=[DataRequired()])
    submit = SubmitField('Submit')
