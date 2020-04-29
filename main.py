from flask import Flask, render_template, url_for, redirect, request
from flask_wtf import FlaskForm
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from wtforms import StringField, SubmitField, BooleanField, PasswordField
from wtforms.validators import DataRequired
from data import db_session
from data.users import *


app = Flask(__name__)
app.config["SECRET_KEY"] = 'T616gram80tR6m1ndM61nd6x2874E7o4'

login_manager = LoginManager()
login_manager.init_app(app)


class RegistrationForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Register")


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Enter")


@app.route('/')
def index():
    if current_user.is_authenticated:
        username = current_user.username
        return render_template('index.html', user_login=True, username=username)
    return render_template('index.html', user_login=False)


@app.route('/register', methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        # TODO


@login_manager.user_loader
def load_user(user_id):
    session = db_session.create_session()
    return session.query(User).get(user_id)


if __name__ == '__main__':
    db_session.global_init("db/data.sqlite")
    app.run()