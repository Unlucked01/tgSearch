from flask import Flask, render_template, url_for

app = Flask(__name__)


@app.route('/')
def index():
    return render_template("home/home.html")


@app.route('/register')
def index_register():
    return render_template("home/register.html")


@app.route('/login')
def index_login():
    return render_template("home/login.html")


@app.route('/settings')
def index_settings():
    return 'Hello World!'


@app.route('/amoconnect')
def index_amoconnect():
    return render_template("home/amoconnect.html")


@app.route('/tgconnect')
def index_tgconnect():
    return render_template("home/telegram.html")


if __name__ == '__main__':
    app.run(debug=True)
