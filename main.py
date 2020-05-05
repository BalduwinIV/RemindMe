from flask import Flask, render_template, jsonify, redirect, request, abort, make_response
from flask_wtf import FlaskForm
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from wtforms import StringField, SubmitField, BooleanField, PasswordField, TextAreaField
from wtforms.validators import DataRequired
import notes_api
import users_api
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
    remember_me = BooleanField("Remember me?")
    submit = SubmitField("Enter")


class NotesCreateForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    content = TextAreaField("Content", validators=[DataRequired()])
    submit = SubmitField("Add")


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect('/notes')
    return render_template('index.html', user_login=False)


@app.route('/register', methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        session = db_session.create_session()

        if session.query(User).filter(User.username == form.username.data).first():
            return render_template('register.html', form=form, user_login=False,
                                   message="This username has been already used.")
        new_user = User()
        new_user.username = form.username.data
        new_user.set_password(form.password.data)
        session.add(new_user)
        session.commit()
        login_user(new_user, remember=True)
        return redirect('/')
    return render_template('register.html', form=form, user_login=False)


@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        user = session.query(User).filter(User.username == form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect('/')
        return render_template('login.html', form=form, user_login=False,
                               message="Wrong username or password")
    return render_template('login.html', form=form, user_login=False)


@app.route('/notes')
def notes():
    username = current_user.username
    session = db_session.create_session()
    notes = session.query(Notes).filter(Notes.user_id == current_user.id).all()
    return render_template('content.html', user_login=True, username=username, notes=notes)


@app.route('/create_note', methods=["GET", "POST"])
def create_note():
    form = NotesCreateForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        new_note = Notes()
        new_note.user_id = current_user.id
        new_note.title = form.title.data
        new_note.content = form.content.data
        session.add(new_note)
        session.commit()
        return redirect("/")
    return render_template("create_note.html", form=form, user_login=True,
                           username=current_user.username)


@app.route('/edit_note/<int:note_id>', methods=["GET", "POST"])
def change_note(note_id):
    form = NotesCreateForm()
    if request.method == "GET":
        session = db_session.create_session()
        note = session.query(Notes).get(note_id)
        if note:
            form.title.data = note.title
            form.content.data = note.content
        else:
            abort(404)
    if form.validate_on_submit():
        session = db_session.create_session()
        note = session.query(Notes).get(note_id)
        if note:
            note.title = form.title.data
            note.content = form.content.data
            session.commit()
            return redirect('/notes')
        else:
            abort(404)
    return render_template('create_note.html', form=form, user_login=True,
                           username=current_user.username)


@app.route('/delete_note/<int:note_id>')
def delete_note(note_id):
    session = db_session.create_session()
    note = session.query(Notes).get(note_id)
    if not note:
        return redirect('/notes')

    session.delete(note)
    session.commit()
    return redirect('/notes')


@app.route('/features')
def features():
    if current_user.is_authenticated:
        return render_template('features.html', user_login=True, username=current_user.username)
    return render_template('features.html', user_login=False)


@app.route('/logout')
def logout():
    logout_user()
    return redirect('/')


@login_manager.user_loader
def load_user(user_id):
    session = db_session.create_session()
    return session.query(User).get(user_id)


if __name__ == '__main__':
    db_session.global_init("db/data.sqlite")
    app.register_blueprint(notes_api.blueprint)
    app.register_blueprint(users_api.blueprint)
    app.run()