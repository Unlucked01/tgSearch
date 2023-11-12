from datetime import timedelta

from flask import Flask, render_template, url_for, flash, redirect, session, request, get_flashed_messages
from misc.models import session as db_session, Users

from web.utils import login_required

app = Flask(__name__)
app.secret_key = ["FLASK_SECRET_KEY"]
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=60)
app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024  # 32 МБ в байтах


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
        flash("Спасибо за регистрацию!", 'success')
        return redirect("home/telegram.html")
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
        return redirect('/settings')

    flash("Некорректный пароль!")
    return render_template('home/login.html')


@app.route('/settings')
@login_required
def index_settings():
    return render_template("home/settings.html")


@app.route('/amoconnect')
@login_required
def index_amoconnect():
    return render_template("home/amoconnect.html")


@app.route('/tgconnect', methods=['GET', 'POST'])
@login_required
def index_tgconnect():
    if request.method == 'GET':
        return render_template('home/telegram.html')

    data = request.json
    api_id = data.get('api_id', None)
    api_hash = data.get('api_hash', None)
    session_name = data.get('')

    if not (api_id and api_hash):
        flash("Не указаны все данные!", 'warning')
        return render_template('home/telegram.html')





    return render_template("home/telegram.html")


if __name__ == '__main__':
    app.run(debug=True)
