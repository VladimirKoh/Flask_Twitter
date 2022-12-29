from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login_manager
from datetime import datetime


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(1024), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __init__(self, text, author, tags=None):
        self.text = text
        self.author = author
        if tags:
            self.tags = [Tag(text=tag) for tag in tags.split(' ')]


class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(32), nullable=False)
    message_id = db.Column(db.Integer, db.ForeignKey('message.id'), nullable=False)
    message = db.relationship('Message', backref=db.backref('tags', lazy=True))


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password_hash = db.Column(db.String(128))
    login = db.Column(db.String(100), nullable=False, unique=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(100), nullable=True)
    messages = db.relationship('Message', backref=db.backref('author', lazy=True))

    def __repr__(self):
        return f"<User {self.login}>"

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))