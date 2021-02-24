from flask import Flask, render_template, url_for, redirect, request, send_file, send_from_directory, abort, session, jsonify
from functools import wraps
from werkzeug.utils import secure_filename

from backend.upload.upload_script import Upload
from backend.download.download_script import Download
from backend.user.forms import RegistrationForm, LoginForm
from backend.user.models import User

import db
import os
import uuid

app = Flask(__name__)
app.config.from_object("config.DevelopmentConfig")

if not os.path.exists(app.config["TEX_UPLOADS"]):
    os.makedirs(app.config["TEX_UPLOADS"])

# Decorators


def login_requiered(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            return redirect('/')
    return wrap


@app.route("/")
def index():
    return render_template('index.html', title='Home')


@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        return User().signup(form)
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        return User().login()
        """ if form.email.data == 'admin@flask.com' and form.password.data == 'password':
            flash('You have been logged in!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger') """
    return render_template('login.html', title='Login', form=form)


@app.route("/logout")
def signout():
    return User().signout()


def allowed_file(filename):
    if not "." in filename:
        return False

    ext = filename.rsplit(".", 1)[1]

    if ext.upper() in app.config["ALLOWED_EXTENSIONS"]:
        return True
    else:
        return False


@app.route("/upload", methods=["GET", "POST"])
def upload_tex():
    if request.method == "POST":
        if request.files:
            zipf = request.files["zipf"]
            if zipf.filename == "":
                print("No filename")
                return redirect(request.url)
            if allowed_file(zipf.filename):
                # print(tex.read().decode('UTF-8'))
                print(zipf)
                Upload.register_question(zipf)
                return redirect(request.url)
            else:
                print("That file extension is not allowed")
                return redirect(request.url)

    return render_template("upload_tex.html", title='Upload')


@app.route("/get-tex/<tex_name>", methods=['GET', 'POST'])
def get_image(tex_name):
    try:
        return send_from_directory(app.config["CLIENT_TEX"], filename=tex_name, as_attachment=True)
    except FileNotFoundError:
        abort(404)


@app.route("/downloads", methods=['GET', 'POST'])
@login_requiered
def downloads():
    data, selection_data = db.list_question_objects()
    if request.method == "POST":
        selection = request.form.getlist('id')
        if selection:
            zip_file_name = 'questions' + str(uuid.uuid4()) + '.zip'
            file_name = 'questions' + str(uuid.uuid4()) + '.tex'
            download = Download.get_questions_by_selection(selection)
            Download.zip_download(download, zip_file_name, file_name)
            return send_from_directory("static/clients/zip", zip_file_name, as_attachment=True)
        return redirect(request.url)
    return render_template('downloads.html', title='Downloads', data=data, selection_data=selection_data)


@app.after_request
def add_headers(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers',
                         'Content-Type,Authorization')
    return response


if __name__ == '__main__':
    app.run()
