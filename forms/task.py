from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, TextAreaField, SubmitField
from wtforms.validators import DataRequired


class TasksForm(FlaskForm):
    title = StringField('Заголовок', validators=[DataRequired()])
    content = TextAreaField('Содержание новости')
    is_private = BooleanField('Личное')
    submit = SubmitField('Добавить новость')
