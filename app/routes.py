from datetime import datetime
from werkzeug.urls import url_parse
from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug.utils import secure_filename
from werkzeug.datastructures import CombinedMultiDict
import uuid as uuid
import os
from app import app, db
from app.forms import AddMessageForm, EditProfileForm, LoginForm, RegistrationForm
from app.func import avatar_saver, examination_message, photo_saver
from app.models import User, Message, Tag
from config import Config


@app.route('/')
@app.route('/index')
def index():
    messages_base = Message.query.order_by(Message.date.desc()).all()
    return render_template("index.html", title='Home Page', messages_base=messages_base, popular_tags=popular_tags)


@app.route('/reading')
def reading():
    messages_base = User.followed_posts(current_user)
    return render_template("index.html", title='Home Page', messages_base=messages_base, popular_tags=popular_tags)


@app.route('/search', methods=['GET', 'POST'])
def search():
    tag_name = request.args.get('q', None)
    messages_base = Message.query.join(Tag, Tag.message_id==Message.id).filter_by(text=tag_name).order_by(Message.date.desc()).all()
    return render_template('index.html', title='Поиск', messages_base=messages_base, popular_tags=popular_tags)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(login=form.login.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(login=form.login.data, email=form.email.data, first_name=form.first_name.data, last_name=form.last_name.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulation, you are now a registred user')
        login_user(user)
        return redirect(url_for('index'))
    return render_template('register.html', title='Register', form=form)


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    #Добавить в скобки current_user.login при включении редактирвоания логина
    form = EditProfileForm(current_user.email)
    if form.validate_on_submit():
        photo = avatar_saver(form.profile_pic_url.data)
        current_user.profile_pic_url = photo
        current_user.email = form.email.data
        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Данные успешно обновлены')
        return redirect(url_for('edit_profile'))
    elif request.method == "GET":
        form.email.data = current_user.email
        form.first_name.data = current_user.first_name
        form.last_name.data = current_user.last_name
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Редактирвоать профиль', form=form)


@app.route('/follow/<userlogin>')
@login_required
def follow(userlogin):
    user = User.query.filter_by(login=userlogin).first()
    if user is None:
        flash('User {} not found.'.format(userlogin))
        return redirect(url_for('index'))
    if user == current_user:
        flash('You cannot follow yourself!')
        return redirect(url_for('user', userlogin=userlogin))
    current_user.follow(user)
    db.session.commit()
    flash('You are following {}!'.format(userlogin))
    return redirect(url_for('user', userlogin=userlogin))


@app.route('/unfollow/<userlogin>')
@login_required
def unfollow(userlogin):
    user = User.query.filter_by(login=userlogin).first()
    if user is None:
        # flash('User {} not found.'.format(userlogin))
        return redirect(url_for('index'))
    if user == current_user:
        # flash('You cannot unfollow yourself!')
        return redirect(url_for('user', userlogin=userlogin))
    current_user.unfollow(user)
    db.session.commit()
    # flash('You are not following {}.'.format(userlogin))
    return redirect(url_for('user', userlogin=userlogin))


@app.route('/user/<userlogin>', methods=['GET', 'POST'])
def user(userlogin):
    form = AddMessageForm(CombinedMultiDict((request.files, request.form)))
    if request.method == "POST":
        if form.validate_on_submit():
            message, tags = examination_message(form.text.data)
            photos = photo_saver(form.photos.raw_data)
            messages_base = Message(text=message, author=current_user, tags=tags, photos=photos)
            db.session.add(messages_base)
            db.session.commit()
            return redirect(url_for('user', userlogin=current_user.login))
    userprofile = User.query.filter_by(login=userlogin).first_or_404()
    messages_base = Message.query.filter_by(author_id=userprofile.id).order_by(Message.date.desc()).all()

    return render_template('user.html', title=f"Профиль {userlogin}", messages_base=messages_base, userprofile=userprofile, form=form)


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


@app.before_first_request
def before_first_request():
    global popular_tags
    popular_tags = Tag.query.order_by(Tag.id.desc()).distinct(Tag.text).limit(10).all()