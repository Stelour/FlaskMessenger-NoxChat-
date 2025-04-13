from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime
from typing import Optional
import sqlalchemy as sa
import sqlalchemy.orm as so
from app import db
from app import login

class User(UserMixin, db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(sa.String(64), index=True, unique=True)
    email: so.Mapped[str] = so.mapped_column(sa.String(120), index=True, unique=True)
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))
    
    profile: so.Mapped["Profile"] = so.relationship(back_populates="user")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return '<User {}>'.format(self.username)

class Profile(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey("user.id"), unique=True)
    bio: so.Mapped[Optional[str]] = so.mapped_column(sa.Text)
    avatar_path: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256), default="base.jpg")
    last_seen: so.Mapped[Optional[datetime]] = so.mapped_column(sa.DateTime)
    public_id: so.Mapped[Optional[str]] = so.mapped_column(sa.String(64), index=True, unique=True)

    user: so.Mapped["User"] = so.relationship(back_populates="profile")
  
    def __repr__(self):
        return '<Profile of {}>'.format(self.user.username)

@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))