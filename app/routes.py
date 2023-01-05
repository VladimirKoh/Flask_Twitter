from datetime import datetime
from werkzeug.urls import url_parse
from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug.utils import secure_filename
import uuid as uuid
import os
from app import app, db
from app.forms import AddMessageForm, EditProfileForm, LoginForm, RegistrationForm
from app.models import User, Message, Tag
from config import Config

@app.route('/')
@app.route('/index')
def index():
    content_left = [1, 2, 3]
    messages_base = Message.query.order_by(Message.date.desc()).all()
    return render_template("index.html", title='Home Page', messages_base=messages_base, content_left=content_left)


@app.route('/reading')
def reading():
    content_left = [1, 2, 3]
    messages_base = User.followed_posts(current_user)
    return render_template("index.html", title='Home Page', messages_base=messages_base, content_left=content_left)


@app.route('/search', methods=['GET', 'POST'])
def search():
    content_left = [1, 2, 3]
    tag_name = request.args.get('q', None)
    messages_base = Message.query.join(Tag, Tag.message_id==Message.id).filter_by(text=tag_name).order_by(Message.date.desc()).all()
    return render_template('index.html', title='Поиск', messages_base=messages_base, content_left=content_left)


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
        file = form.profile_pic_url.data
        pic_filename = secure_filename(file.filename)
        pic_name = str(uuid.uuid1()) + "_" + pic_filename
        #save that image
        file.save(os.path.join(os.path.abspath(os.path.dirname(__file__)), Config.UPLOAD_FOLDER, pic_name))
        user = User(login=form.login.data, email=form.email.data, first_name=form.first_name.data, last_name=form.last_name.data, profile_pic_url=pic_name)
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
        flash('User {} not found.'.format(userlogin))
        return redirect(url_for('index'))
    if user == current_user:
        flash('You cannot unfollow yourself!')
        return redirect(url_for('user', userlogin=userlogin))
    current_user.unfollow(user)
    db.session.commit()
    flash('You are not following {}.'.format(userlogin))
    return redirect(url_for('user', userlogin=userlogin))


@app.route('/user/<userlogin>', methods=['GET', 'POST'])
def user(userlogin):
    form = AddMessageForm()
    if request.method == "POST":
        if form.validate_on_submit():
            message = form.text.data
            #система отбирания тегов из сообщения
            tag_list = list()
            text_list = list()
            for row in message.split():
                if '#' in row:
                    tag_list.append(row.replace('#', ''))
                else:
                    text_list.append(row)
            if len(tag_list) > 0:
                tag = ' '.join(tag_list)
            else:
                tag = None
            message = ' '.join(text_list)
            #конец системы отбирания тегов
            author = current_user
            messages_base = Message(message, author, tag)
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