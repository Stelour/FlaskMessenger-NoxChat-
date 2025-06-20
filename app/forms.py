from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
import sqlalchemy as sa
from app import db
from app.models import User, Profile
from wtforms import TextAreaField
from wtforms.validators import Length
from flask_wtf.file import FileField, FileAllowed

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = db.session.scalar(sa.select(User).where(
            User.username == username.data))
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = db.session.scalar(sa.select(User).where(
            User.email == email.data))
        if user is not None:
            raise ValidationError('Please use a different email address.')
        
class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    bio = TextAreaField('Bio', validators=[Length(min=0, max=140)])
    public_id = StringField('Public ID', validators=[DataRequired()])
    avatar = FileField('Update Avatar', validators=[FileAllowed(['jpg', 'png'], 'Images only!')])
    submit = SubmitField('Submit')
    
    def __init__(self, original_username, original_public_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.original_username = original_username
        self.original_public_id = original_public_id

    def validate_username(self, username):
        if username.data != self.original_username:
            user = db.session.scalar(sa.select(User).where(User.username == username.data))
            if user is not None:
                raise ValidationError('Please use a different username.')

    def validate_public_id(self, public_id):
        if public_id.data != self.original_public_id:
            profile = db.session.scalar(sa.select(Profile).where(Profile.public_id == public_id.data))
            if profile is not None:
                raise ValidationError('This Public ID is already in use.')

class EmptyForm(FlaskForm):
    submit = SubmitField('Submit')

class SearchUserForm(FlaskForm):
    search_user = StringField('Username or ID', validators=[DataRequired()])
    submit = SubmitField('Submit')