from flask import Flask, render_template, request, make_response, session, redirect, jsonify, abort
import datetime as dt
from data import db_session
from data.users import User
from data.tasks import Tasks
from forms.user import RegisterForm
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from forms.login import LoginForm
from forms.task import TasksForm
from forms.task_del import TasksFormDel
from random import choices
from data.news import News


app = Flask(__name__)
app.config['SECRET_KEY'] = 'timkarazvod'
login_manager = LoginManager()
login_manager.init_app(app)


@app.route('/')
def main_page():
    db_sess = db_session.create_session()
    news = db_sess.query(News)
    return render_template('main_page.html', items=news)


@app.route('/main')
def index():
    news = None
    db_sess = db_session.create_session()
    if current_user.is_authenticated:
        news = db_sess.query(Tasks).filter(
            Tasks.user == current_user)
    return render_template('index.html', news=news)


@app.route('/profile')
def profile():
    return render_template('profile.html')


@app.route('/reg', methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('reg.html', title='Регистрация', form=form,
                                   message='Пароли не совпадают')
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('reg.html', title='Регистрация', form=form,
                                   message='Пользователь уже есть')
        code = generate_code()
        user = User(
            login=form.login.data,
            email=form.email.data,
            bot_id=code
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
    return render_template('reg.html', title='Регистрация', form=form)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect('/')
        else:
            return render_template('log.html', message='Неправильный логин или пароль',
                                   form=form)
    return render_template('log.html', title='Авторизация', form=form)


@app.route('/tasks',  methods=['GET', 'POST'])
@login_required
def add_tasks():
    form = TasksForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        tasks = Tasks()
        tasks.title = form.title.data
        tasks.content = form.content.data
        current_user.tasks.append(tasks)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect('/')
    return render_template('tasks.html', title='Добавление задачи',
                           form=form)


@app.route('/tasks_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def tasks_delete(id):
    form = TasksFormDel()
    db_sess = db_session.create_session()
    tasks = db_sess.query(Tasks).filter(Tasks.id == id,
                                      Tasks.user == current_user
                                      ).first()
    if tasks:
        db_sess.delete(tasks)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')


def generate_code():
    alph = 'qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM1234567890'
    arr = []
    for i in range(12):
        arr += choices(alph)
    code = ''
    for el in arr:
        code += el
    return code


def main():
    db_session.global_init('db/users.db')
    app.run()


if __name__ == '__main__':
    main()
