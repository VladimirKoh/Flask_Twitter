from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, EqualTo, Email, ValidationError, Length
from flask_wtf.file import FileField, FileAllowed, FileRequired

from app.models import User

class LoginForm(FlaskForm):
    login = StringField('Логин', validators=[DataRequired()], render_kw={"placeholder": "Логин"})
    password = PasswordField('Пароль', validators=[DataRequired()], render_kw={"placeholder": "Пароль"})
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class RegistrationForm(FlaskForm):
    login = StringField('Логин', validators=[DataRequired()], render_kw={"placeholder": "Логин"})
    email = StringField('Емаил', validators=[DataRequired(), Email()], render_kw={"placeholder": "Емеил"})
    password = PasswordField('Пароль', validators=[DataRequired()], render_kw={"placeholder": "Пароль"})
    password2 = PasswordField('Повторите пароль', validators=[DataRequired(), EqualTo('password')], render_kw={"placeholder": "Повторите пароль"})
    first_name = StringField('Имя', validators=[DataRequired()], render_kw={"placeholder": "Имя"})
    last_name = StringField('Фамилия', validators=[DataRequired()], render_kw={"placeholder": "Фамилия"})
    submit = SubmitField('Зарегистрироваться')

    def validate_username(self, login):
        user = User.query.filter_by(login=login.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')


class EditProfileForm(FlaskForm):
    # login = StringField('Логин', validators=[DataRequired()])
    profile_pic_url = FileField('Аватар профиля')
    email = StringField('Емаил', validators=[DataRequired(), Email()])
    first_name = StringField('Имя', validators=[DataRequired()])
    last_name = StringField('Фамилия', validators=[DataRequired()])
    about_me = TextAreaField('Обо мне', validators=[Length(min=0, max=140)])
    submit = SubmitField('Редактировать')

    #Включить при редактировани логина!

    def __init__(self, original_email, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_email = original_email

    def validate_email(self, email):
        if email.data != self.original_email:
            user = User.query.filter_by(email=self.email.data).first()
            if user is not None:
                raise ValidationError('Такой емеил уже существует')


class AddMessageForm(FlaskForm):
    text = TextAreaField('Что происходит', validators=[DataRequired()])
    photos = FileField('image', render_kw={'multiple': True})
    submit = SubmitField('Опубликовать')