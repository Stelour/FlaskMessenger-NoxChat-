from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime, timezone
from typing import Optional
import sqlalchemy as sa
import sqlalchemy.orm as so
from app import db
from app import login
from time import time
import jwt
from app import app

friends_table = sa.Table(
    'friends',
    db.metadata,
    sa.Column('user_id', sa.Integer, sa.ForeignKey('user.id'), primary_key=True),
    sa.Column('friend_id', sa.Integer, sa.ForeignKey('user.id'), primary_key=True)
)

friend_requests = sa.Table(
    'friend_requests',
    db.metadata,
    sa.Column('sender_id', sa.Integer, sa.ForeignKey('user.id'), primary_key=True),
    sa.Column('receiver_id', sa.Integer, sa.ForeignKey('user.id'), primary_key=True)
)

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
    
    friends: so.WriteOnlyMapped['User'] = so.relationship(
        secondary=friends_table,
        primaryjoin=(friends_table.c.user_id == id),
        secondaryjoin=(friends_table.c.friend_id == id)
    )

    sent_requests: so.WriteOnlyMapped['User'] = so.relationship(
        'User',
        secondary=friend_requests,
        primaryjoin=(friend_requests.c.sender_id == id),
        secondaryjoin=(friend_requests.c.receiver_id == id),
        back_populates='received_requests'
    )

    received_requests: so.WriteOnlyMapped['User'] = so.relationship(
        'User',
        secondary=friend_requests,
        primaryjoin=(friend_requests.c.receiver_id == id),
        secondaryjoin=(friend_requests.c.sender_id == id),
        back_populates='sent_requests'
    )
    
    def add_friend(self, user):
        if not self.is_friend(user) and user != self:
            self.friends.add(user)
            user.friends.add(self)

    def remove_friend(self, user):
        if self.is_friend(user):
            self.friends.remove(user)
            user.friends.remove(self)

    def is_friend(self, user):
        query = self.friends.select().where(User.id == user.id)
        return db.session.scalar(query) is not None

    def send_friend_request(self, user):
        if user == self or self.is_friend(user):
            return 'none'
        if self.received_request_from(user):
            self.accept_friend_request(user)
            return 'accepted'
        if not self.sent_request_to(user):
            self.sent_requests.add(user)
            return 'sent'
        return 'none'

    def cancel_friend_request(self, user):
        if self.sent_request_to(user):
            self.sent_requests.remove(user)

    def accept_friend_request(self, user):
        if self.received_request_from(user):
            self.received_requests.remove(user)
            self.add_friend(user)

    def decline_friend_request(self, user):
        if self.received_request_from(user):
            self.received_requests.remove(user)

    def sent_request_to(self, user):
        query = self.sent_requests.select().where(User.id == user.id)
        return db.session.scalar(query) is not None

    def received_request_from(self, user):
        query = self.received_requests.select().where(User.id == user.id)
        return db.session.scalar(query) is not None

    def has_pending_request(self, user):
        return self.sent_request_to(user) or self.received_request_from(user)

    def outgoing_requests_count(self):
        query = sa.select(sa.func.count()).select_from(
            self.sent_requests.select().subquery())
        return db.session.scalar(query)

    def incoming_requests_count(self):
        query = sa.select(sa.func.count()).select_from(
            self.received_requests.select().subquery())
        return db.session.scalar(query)

    def friends_count(self):
        query = sa.select(sa.func.count()).select_from(
            self.friends.select().subquery())
        return db.session.scalar(query)
    
    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            app.config['SECRET_KEY'], algorithm='HS256')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return db.session.get(User, id)

class Profile(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey("user.id"), unique=True)
    bio: so.Mapped[Optional[str]] = so.mapped_column(sa.Text)
    avatar_path: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256), default="base.jpg")
    last_seen: so.Mapped[datetime] = so.mapped_column(
        sa.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    public_id: so.Mapped[Optional[str]] = so.mapped_column(sa.String(64), index=True, unique=True)

    user: so.Mapped["User"] = so.relationship(back_populates="profile")
  
    def __repr__(self):
        return '<Profile of {}>'.format(self.user.username)

@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))
