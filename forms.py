from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class AddArticleForm(FlaskForm):
    title = StringField("Title")
    text = StringField("Text")
    submit = SubmitField("Submit")

class AddUserForm(FlaskForm):
    name = StringField("Name")
    login = StringField("Login")
    password = StringField("Password")
    submit = SubmitField("Submit")


class LogInForm(FlaskForm):
    login = StringField("Login")
    password = StringField("Password")
    submit = SubmitField("Submit")

