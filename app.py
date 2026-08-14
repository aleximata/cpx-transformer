# ===== FORMULARIOS =====
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, BooleanField
from wtforms.validators import DataRequired, Email, Length, EqualTo

class LoginForm(FlaskForm):
    username = StringField('Usuario', validators=[DataRequired()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    remember_me = BooleanField('Recordarme')
    submit = SubmitField('Iniciar Sesión')

class RegisterForm(FlaskForm):
    username = StringField('Usuario', validators=[DataRequired(), Length(min=3, max=50)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Contraseña', validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField('Confirmar Contraseña', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Registrarme')

class LinkTransformForm(FlaskForm):
    original_link = TextAreaField('Link Original', validators=[DataRequired()])
    submit = SubmitField('Transformar Link')