import asyncio
import os
from datetime import timedelta

from flask import Flask, render_template, url_for, flash, redirect, session, request, send_file, get_flashed_messages, \
    jsonify
from sqlalchemy.testing.pickleable import User

import io

from bot.amocrm import AmoConnect
from misc.models import dbSession as db_session, Users, TelegramAccounts, AmocrmAccounts, Setting, Session,  \
    add_telegram, add_amo, add_settings, add_session_id
from web.telegram import create_telegram_client, run_bot

from web.utils import login_required

app = Flask(__name__)

UPLOAD_FOLDER = '/sessions'
ALLOWED_EXTENSIONS = {'session'}

app.secret_key = ["FLASK_SECRET_KEY"]
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=60)
app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024  # 32 МБ в байтах
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.errorhandler(404)
def page_not_found(e):
    flash('Страницы не существует! Перенаправил вас на главную.', 'warning')
    return redirect('/')


@app.route('/')
def index():
    return render_template("home/home.html")


@app.route('/register', methods=['GET', 'POST'])
def index_register():
    if request.method == 'GET':
        return render_template('home/register.html')

    login = request.form.get("login", None)
    password = request.form.get("password", None)
    if login is not None and password is not None:
        user = db_session.query(Users).filter(Users.email == login).first()
        if user:
            flash("Пользователь уже существует!", 'warning')
            return redirect("/register")
        new_user = Users(email=login, password=password)
        db_session.add(new_user)
        db_session.commit()
        session["authenticated"] = True
        session['login'] = login
        flash("Спасибо за регистрацию!", 'success')
        return redirect(index_tgconnect)
    return render_template("home/register.html")


@app.route('/login', methods=['GET', 'POST'])
def index_login():
    if request.method == "GET":
        return render_template('home/login.html')

    login = request.form.get("login", None)
    password = request.form.get("password", None)
    print(login, password)
    user: Users = db_session.query(Users).filter(Users.email == login).first()

    if user is None:
        flash("Пользователя не существует!", 'warning')
        return redirect(request.path)

    if user.email == login and user.password == password:
        flash("Вход успешен!", 'success')
        session["authenticated"] = True
        session['login'] = login
        return redirect('/settings')

    flash("Некорректный пароль!")
    return render_template('home/login.html')


@app.route('/settings', methods=['GET', 'POST'])
@login_required
def index_settings():
    login = session["login"]
    print(login)
    if request.method == 'GET':
        return render_template("home/settings.html")
    data = request.form
    groups = data.getlist('field-value-left')
    keys = data.getlist('field-value-right')
    chat_id = data.get('field-value-telegram')

    if 'save_changes' in data:
        add_settings(login, groups=groups, keys=keys, chat_id=chat_id)
    elif 'execute_code' in data:
        asyncio.run(run_bot(login))
    return render_template("home/settings.html")


@app.route('/amoconnect', methods=['GET', 'POST'])
@login_required
def index_amoconnect():
    login = session["login"]
    if request.method == 'GET':
        return render_template("home/amoconnect.html")
    data = request.form
    amo_login = data.get('login', None)
    password = data.get('password', None)

    amo_user: User = db_session.query(AmocrmAccounts).filter(AmocrmAccounts.email == amo_login).first()

    if amo_user is not None:
        flash("Пользователь существует!", 'warning')
        return redirect(request.path)

    if amo_login and password != '':
        flash("Вход успешен!", 'success')
        AmoConnect(user_login=amo_login, user_password=password)
        add_amo(login, amo_login=amo_login, amo_password=password)
        return redirect(index_settings)

    return redirect(index_amoconnect)


@app.route('/tgconnect', methods=['GET', 'POST'], )
@login_required
def index_tgconnect():
    login = session['login']
    if request.method == 'GET':
        return render_template('home/telegram.html', need_code=False)

    data = request.form
    api_id = data.get('api_id', None)
    api_hash = data.get('api_hash', None)
    phone = data.get('phone_number', None)
    account_id = data.get('account_id', None)

    tg_user: User = db_session.query(TelegramAccounts).filter(TelegramAccounts.api_id == api_id,
                                                             TelegramAccounts.api_hash == api_hash).first()
    if tg_user is not None:
        flash("Пользователь существует!", 'warning')
        return redirect(request.path)

    if not (api_id and api_hash):
        flash("Не указаны все данные!", 'warning')
        return render_template('home/telegram.html')

    add_telegram(login, api_id, api_hash, phone, account_id)
    return redirect(index_tgconnect)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
