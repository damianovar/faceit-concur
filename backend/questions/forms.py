from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo

class QuestionFilterForm(FlaskForm):
    question_type = SelectField('Question Type')
    cu = SelectField('Content Unit')
    submit = SubmitField('Search')