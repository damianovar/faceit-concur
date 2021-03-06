from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo


class RegistrationForm(FlaskForm):
    first_name  = StringField('First Name', validators=[DataRequired(), Length(min=2, max=30)])
    last_name   = StringField('Last Name', validators=[DataRequired(), Length(min=2, max=30)])
    institution = SelectField('Institution', validators=[DataRequired()])
    role        = SelectField(u'Role', choices=['Student', 'Teacher', 'Admin'])
    username    = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email       = StringField('Email', validators=[DataRequired(), Email()])
    password    = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit      = SubmitField('Sign Up')


class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class DownloadForm(FlaskForm):
    submit = SubmitField('Send')
