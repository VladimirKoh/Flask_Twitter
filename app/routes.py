from werkzeug.urls import url_parse
from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from app import app, db
from app.forms import AddMessageForm, LoginForm, RegistrationForm
from app.models import User, Message, Tag

@app.route('/')
@app.route('/index')
def index():
    content_left = [1, 2, 3]
    messages_base = Message.query.order_by(Message.date.desc()).all()
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
        user = User(login=form.login.data, email=form.email.data, first_name=form.first_name.data, last_name=form.last_name.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulation, you are now a registred user')
        login_user(user)
        return redirect(url_for('index'))
    return render_template('register.html', title='Register', form=form)


@app.route('/user/<userlogin>', methods=['GET', 'POST'])
def user(userlogin):
    form = AddMessageForm()
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