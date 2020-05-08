from flask import Flask, render_template, jsonify, redirect, request, abort, make_response, url_for
from flask_wtf import FlaskForm
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from wtforms import StringField, SubmitField, BooleanField, PasswordField, TextAreaField
from wtforms.validators import DataRequired
import notes_api
import users_api
import tgbot
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
    submit = SubmitField("Sign in")


class UserDataForm(FlaskForm):
    username = StringField("Username")
    old_password = PasswordField("Old password")
    new_password = PasswordField("New password")
    submit = SubmitField("Confirm")


class NotesCreateForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    content = TextAreaField("Content", validators=[DataRequired()])
    submit = SubmitField("Add")


class TaskCreateForm(FlaskForm):
    task = StringField("Task", validators=[DataRequired()])
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


@app.route('/profile', methods=["GET", "POST"])
def profile():
    form = UserDataForm()
    if request.method == "GET":
        session = db_session.create_session()
        user = session.query(User).get(current_user.id)
        form.username.data = user.username
    if form.validate_on_submit():
        session = db_session.create_session()
        user = session.query(User).get(current_user.id)
        try:
            user.username = form.username.data
            session.commit()
        except Exception:
            return render_template('profile.html', form=form, user_login=True,
                                   username=current_user.username,
                                   message="This username has been already taken.",
                                   user_id=current_user.id)
        if form.old_password.data or form.new_password.data:
            if not form.old_password.data:
                return render_template('profile.html', form=form, user_login=True,
                                       username=current_user.username,
                                       message="Write an old password.",
                                       user_id=current_user.id)
            if user.check_password(form.old_password.data):
                if not form.new_password.data:
                    return render_template('profile.html', form=form, user_login=True,
                                           username=current_user.username,
                                           message="Write a new password.",
                                           user_id=current_user.id)
                user.set_password(form.new_password.data)
                session.commit()
                return redirect('/notes')
            return render_template('profile.html', form=form, user_login=True,
                                   username=current_user.username,
                                   message="Old password is wrong.",
                                   user_id=current_user.id)
        return redirect('/notes')
    return render_template('profile.html', form=form, user_login=True,
                           username=current_user.username, user_id=current_user.id)


@app.route('/delete_user/<int:user_id>')
def delete_user(user_id):
    session = db_session.create_session()
    user = session.query(User).get(user_id)
    if not user:
        abort(404)
    session.delete(user)
    session.commit()
    return redirect('/')


@app.route('/notes')
def notes():
    if current_user.is_authenticated:
        username = current_user.username
        session = db_session.create_session()
        notes = session.query(Notes).filter(Notes.user_id == current_user.id).all()
        return render_template('content.html', user_login=True, username=username, notes=notes)
    return render_template('permission.html', user_login=False)


@app.route('/create_note', methods=["GET", "POST"])
def create_note():
    if current_user.is_authenticated:
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
    return render_template('permission.html', user_login=False)


@app.route('/edit_note/<int:note_id>', methods=["GET", "POST"])
def change_note(note_id):
    if current_user.is_authenticated:
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
    return render_template('permission.html', user_login=False)


@app.route('/delete_note/<int:note_id>')
def delete_note(note_id):
    if current_user.is_authenticated:
        session = db_session.create_session()
        note = session.query(Notes).get(note_id)
        if not note:
            return redirect('/notes')

        session.delete(note)
        session.commit()
        return redirect('/notes')
    return render_template('permission.html', user_login=False)


@app.route('/tasks')
def tasks():
    if current_user.is_authenticated:
        username = current_user.username
        session = db_session.create_session()
        tasks = session.query(Tasks).filter(Tasks.user_id == current_user.id).all()
        return render_template('tasks.html', user_login=True, username=username, tasks=tasks)
    return render_template('permission.html', user_login=False)


@app.route('/complete_task/<int:task_id>')
def complete_task(task_id):
    if current_user.is_authenticated:
        session = db_session.create_session()
        task = session.query(Tasks).get(task_id)
        if not task:
            abort(404)
        task.state = True
        session.commit()
        return redirect('/tasks')
    return render_template('permission.html', user_login=False)


@app.route('/ruin_task/<int:task_id>')
def ruin_task(task_id):
    if current_user.is_authenticated:
        session = db_session.create_session()
        task = session.query(Tasks).get(task_id)
        if not task:
            abort(404)
        task.state = False
        session.commit()
        return redirect('/tasks')
    return render_template('permission.html', user_login=False)


@app.route('/create_task', methods=["GET", "POST"])
def create_task():
    if current_user.is_authenticated:
        form = TaskCreateForm()
        if form.validate_on_submit():
            session = db_session.create_session()
            new_task = Tasks()
            new_task.user_id = current_user.id
            new_task.task = form.task.data
            session.add(new_task)
            session.commit()
            return redirect("/tasks")
        return render_template("create_task.html", form=form, user_login=True,
                               username=current_user.username)
    return render_template('permission.html', user_login=False)


@app.route('/edit_task/<int:task_id>', methods=["GET", "POST"])
def edit_task(task_id):
    if current_user.is_authenticated:
        form = TaskCreateForm()
        if request.method == "GET":
            session = db_session.create_session()
            task = session.query(Tasks).get(task_id)
            if task:
                form.task.data = task.task
            else:
                abort(404)
        if form.validate_on_submit():
            session = db_session.create_session()
            task = session.query(Tasks).get(task_id)
            if task:
                task.task = form.task.data
                session.commit()
                return redirect('/tasks')
            else:
                abort(404)
        return render_template('create_task.html', form=form, user_login=True,
                               username=current_user.username)
    return render_template('permission.html', user_login=False)


@app.route('/delete_task/<int:task_id>')
def delete_task(task_id):
    if current_user.is_authenticated:
        session = db_session.create_session()
        task = session.query(Tasks).get(task_id)
        if not task:
            abort(404)
        session.delete(task)
        session.commit()
        return redirect('/tasks')
    return render_template('permission.html', user_login=False)


@app.route('/features')
def features():
    if current_user.is_authenticated:
        return render_template('features.html', user_login=True, username=current_user.username,
                               release_pic=url_for('static', filename='img/release_img.png'),
                               feature_pic=url_for('static', filename='img/feature_img.jpg'))
    return render_template('features.html', user_login=False,
                           release_pic=url_for('static', filename='img/release_img.png'),
                           feature_pic=url_for('static', filename='img/feature_img.jpg'))


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