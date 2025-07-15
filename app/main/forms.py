from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import ValidationError, DataRequired
import re
import sqlalchemy as sa
from app import db
from app.models import User, Profile
from wtforms.validators import Length
from flask_wtf.file import FileField, FileAllowed

USERNAME_RE = re.compile(r'^[A-Za-z0-9](?:[A-Za-z0-9_]*[A-Za-z0-9])?$')
        
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
            if not USERNAME_RE.match(username.data):
                raise ValidationError('Use letters, numbers or _; cannot start or end with _.')
            user = db.session.scalar(sa.select(User).where(User.username == username.data))
            if user is not None:
                raise ValidationError('Please use a different username.')

    def validate_public_id(self, public_id):
        if public_id.data != self.original_public_id:
            if not USERNAME_RE.match(public_id.data):
                raise ValidationError('Use letters, numbers or _; cannot start or end with _.')
            profile = db.session.scalar(sa.select(Profile).where(Profile.public_id == public_id.data))
            if profile is not None:
                raise ValidationError('This Public ID is already in use.')

class EmptyForm(FlaskForm):
    submit = SubmitField('Submit')

class SearchUserForm(FlaskForm):
    search_user = StringField('Username or ID', validators=[DataRequired()])
    submit = SubmitField('Submit')

class FriendsForm(FlaskForm):
    search_user = StringField('Username or ID', validators=[DataRequired()])
    submit = SubmitField('Submit')