from flask import render_template, flash, redirect, url_for
from app import app
from app.forms import LoginForm
from flask_login import current_user, login_user
import sqlalchemy as sa
from app import db
from app.models import User, Profile
from flask_login import logout_user
from flask_login import login_required
from flask import request
from urllib.parse import urlsplit
from app.forms import RegistrationForm
from datetime import datetime, timezone
from app.forms import EditProfileForm
from app.avatar_utils import save_avatar, rename_avatar_directory, clear_old_avatars
from app.forms import EmptyForm
from app.updates import updates
from app.forms import SearchUserForm
from app.forms import FriendsForm

@app.route('/')
@app.route('/index')
@login_required
def index():
    welcome_message = f"Welcome to NoxChat, {current_user.username}! "
    sorted_updates = sorted(updates, key=lambda u: u['date'], reverse=True)
    return render_template(
        "index.html", 
        title='Home', 
        welcome_message=welcome_message, 
        updates=sorted_updates,)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()

    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.username == form.username.data))
        
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')

        if not next_page or urlsplit(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        
        profile = Profile(user_id=user.id, public_id=f'{user.username.lower()}_{user.id}')
        profile.bio = "No bio yet"
        db.session.add(profile)
        db.session.commit()

        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/user/<public_id>')
@login_required
def user(public_id):
    user = db.first_or_404(
        sa.select(User).join(Profile).where(Profile.public_id == public_id)
    )
    form = EmptyForm()
    return render_template('user.html', title='Profile', user=user, form=form)

@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.profile.last_seen = datetime.now(timezone.utc)
        db.session.commit()

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(
        original_username=current_user.username, 
        original_public_id=current_user.profile.public_id
        )
    if form.validate_on_submit():
        new_public_id = form.public_id.data.lower()
        old_public_id = current_user.profile.public_id
        
        if new_public_id != old_public_id:
            rename_avatar_directory(old_public_id, new_public_id)
            if current_user.profile.avatar_path and '/' in current_user.profile.avatar_path:
                _, filename = current_user.profile.avatar_path.split('/', 1)
                current_user.profile.avatar_path = f"{new_public_id}/{filename}"
            current_user.profile.public_id = new_public_id
        
        current_user.username = form.username.data
        current_user.profile.bio = form.bio.data

        if form.avatar.data:
            relative_path, new_filename = save_avatar(form.avatar.data, current_user.profile.public_id)
            current_user.profile.avatar_path = relative_path
            clear_old_avatars(current_user.profile.public_id, new_filename)
            
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit_profile'))
    
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.bio.data = current_user.profile.bio
        form.public_id.data = current_user.profile.public_id

    return render_template('edit_profile.html', title='Edit Profile', form=form)

@app.route('/send_request/<public_id>', methods=['POST'])
@login_required
def send_request(public_id):
    form = EmptyForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).join(Profile).where(Profile.public_id == public_id)
        )
        if user is None:
            flash(f'User {public_id} not found.')
            return redirect(request.referrer or url_for('index'))
        if user == current_user:
            flash('You cannot add yourself as a friend!')
            return redirect(request.referrer or url_for('user', public_id=user.profile.public_id))
        result = current_user.send_friend_request(user)
        db.session.commit()
        if result == 'accepted':
            flash(f'You are now friends with {public_id}.')
        elif result == 'sent':
            flash(f'Friend request sent to {public_id}.')
        return redirect(request.referrer or url_for('user', public_id=user.profile.public_id))
    return redirect(request.referrer or url_for('index'))

@app.route('/remove_friend/<public_id>', methods=['POST'])
@login_required
def remove_friend(public_id):
    form = EmptyForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).join(Profile).where(Profile.public_id == public_id)
        )
        if user is None:
            flash(f'User {public_id} not found.')
            return redirect(request.referrer or url_for('index'))
        if user == current_user:
            flash('You cannot remove yourself!')
            return redirect(request.referrer or url_for('user', public_id=user.profile.public_id))
        current_user.remove_friend(user)
        db.session.commit()
        flash(f'You are no longer friends with {public_id}.')
        return redirect(request.referrer or url_for('user', public_id=user.profile.public_id))
    return redirect(request.referrer or url_for('index'))

@app.route('/accept_request/<public_id>', methods=['POST'])
@login_required
def accept_request(public_id):
    form = EmptyForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).join(Profile).where(Profile.public_id == public_id)
        )
        if user is None:
            flash(f'User {public_id} not found.')
            return redirect(request.referrer or url_for('index'))
        current_user.accept_friend_request(user)
        db.session.commit()
        flash(f'Friend request from {public_id} accepted.')
        return redirect(request.referrer or url_for('user', public_id=user.profile.public_id))
    return redirect(request.referrer or url_for('index'))

@app.route('/decline_request/<public_id>', methods=['POST'])
@login_required
def decline_request(public_id):
    form = EmptyForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).join(Profile).where(Profile.public_id == public_id)
        )
        if user is None:
            flash(f'User {public_id} not found.')
            return redirect(request.referrer or url_for('index'))
        current_user.decline_friend_request(user)
        db.session.commit()
        flash(f'Friend request from {public_id} declined.')
        return redirect(request.referrer or url_for('user', public_id=user.profile.public_id))
    return redirect(request.referrer or url_for('index'))

@app.route('/cancel_request/<public_id>', methods=['POST'])
@login_required
def cancel_request(public_id):
    form = EmptyForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).join(Profile).where(Profile.public_id == public_id)
        )
        if user is None:
            flash(f'User {public_id} not found.')
            return redirect(request.referrer or url_for('index'))
        current_user.cancel_friend_request(user)
        db.session.commit()
        flash(f'Friend request to {public_id} canceled.')
        return redirect(request.referrer or url_for('user', public_id=user.profile.public_id))
    return redirect(request.referrer or url_for('index'))

@app.route('/search', methods=['GET', 'POST'])
@login_required
def search_user():
    form = SearchUserForm()
    results = None
    
    if form.validate_on_submit():
        query = form.search_user.data
        stmt = (
            sa.select(User)
            .join(Profile)
            .where(
                sa.or_(
                    User.username.ilike(f"%{query}%"),
                    Profile.public_id.ilike(f"%{query}%")
                )
            )
        )
        results = db.session.execute(stmt).scalars().all()
    
    return render_template('search.html', title='Search', form=form, results=results)

@app.route('/friends', methods=['GET', 'POST'])
@login_required
def friends():
    view = request.args.get('view', 'friends')
    form = FriendsForm()
    users = []

    if view == 'friends':
        stmt = current_user.friends.select().join(Profile)
    elif view == 'outgoing':
        stmt = current_user.sent_requests.select().join(Profile)
    elif view == 'incoming':
        stmt = current_user.received_requests.select().join(Profile)
    
    if form.validate_on_submit():
        query = form.search_user.data
        stmt = stmt.where(
            sa.or_(
                User.username.ilike(f'%{query}%'),
                Profile.public_id.ilike(f'%{query}%')
            )
        )
        
    users = db.session.execute(stmt).scalars().all()
    
    return render_template('friends.html', title='Friends', form=form, users=users, view=view)