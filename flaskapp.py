from flask import Flask, render_template, url_for, flash, redirect, request, send_file, send_from_directory, abort, session
from user.forms import RegistrationForm, LoginForm
from functools import wraps
from werkzeug.utils import secure_filename

import db
import zipfile
import os
from user.models import User

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
        User().signup(form)
        return redirect('/')
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if form.email.data == 'admin@flask.com' and form.password.data == 'password':
            flash('You have been logged in!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
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

            tex = request.files["tex"]

            if tex.filename == "":
                print("No filename")
                return redirect(request.url)

            if allowed_file(tex.filename):
                filename = secure_filename(tex.filename)

                tex.save(os.path.join(app.config["TEX_UPLOADS"], filename))

                print("tex saved")

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


@app.route("/downloads/", methods=['GET', 'POST'])
@login_requiered
def downloads():

    files = os.listdir('backend/sample_data')
    data = db.list_question_objects()
    if request.method == 'POST':
        file_list = request.form.getlist('box')
        zipfolder = zipfile.ZipFile(
            'TEXfiles.zip', 'w', compression=zipfile.ZIP_STORED)
        for tex_file in file_list:
            zipfolder.write('static/clients/tex/'+tex_file, 'tex/'+tex_file)
        zipfolder.write('backend/sample_data/contentsmapping.tex',
                        'contentsmapping.tex')
        zipfolder.close()
        return send_file('TEXfiles.zip', mimetype='zip', attachment_filename='TEXfiles.zip', as_attachment=True, cache_timeout=-1)
    return render_template('downloads.html', title='Downloads', data=data)

    # Delete the zip file if not needed
    os.remove("TEXfiles.zip")


if __name__ == '__main__':
    app.run(debug=True)
