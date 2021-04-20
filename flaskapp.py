"""Entry Point."""
from typing import *

from flask import (
    Flask,
    render_template,
    url_for,
    redirect,
    request,
    send_from_directory,
    abort,
    session,
    jsonify,
)
from functools import wraps
from werkzeug.utils import secure_filename

from backend.upload.upload_script import Upload
from backend.download.download_script import Download
from backend.user.forms import RegistrationForm, LoginForm
from backend.user.models import Account
from backend.models.models import University, Course, User

import db
import matrix
import os
import uuid
import random
import numpy


app = Flask(__name__)
app.config.from_object("config.DevelopmentConfig")

if not os.path.exists(app.config["TEX_UPLOADS"]):
    os.makedirs(app.config["TEX_UPLOADS"])


def login_requiered(f):
    """
    Check if user is logged in.

    function f
    """

    @wraps(f)
    def wrap(*args, **kwargs):
        if "logged_in" in session:
            return f(*args, **kwargs)
        else:
            return redirect("/")

    return wrap


@app.route("/")
def index() -> Any:
    """Return homepage."""
    db.manually_add_stuff()
    return render_template("index.html", title="Home")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Return a page for registering a user."""
    form = RegistrationForm()
    form.university.choices = [
        universities.name for universities in University.objects()
    ]
    if request.method == "POST" and form.validate():
        if Account().signup(form):
            return redirect("/")
    return render_template("register.html", title="Register", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Redirect a user to the logged in page if user credentials are correct."""
    form = LoginForm()
    if form.validate_on_submit():
        return Account().login()
    return render_template("login.html", title="Login", form=form)


@app.route("/logout")
def signout():
    """Sign out a user."""
    return Account().signout()


def allowed_file(filename):
    """
    Check if filename is valid.

    str filename

    return bool
    """
    if not "." in filename:
        return False

    ext = filename.rsplit(".", 1)[1]

    if ext.upper() in app.config["ALLOWED_EXTENSIONS"]:
        return True
    else:
        return False


@app.route("/upload", methods=["GET", "POST"])
def upload_tex():
    """Upload a tex-file."""
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
    return render_template("upload_tex.html", title="Upload")


@app.route("/submit_answer", methods=["GET", "POST"])
@login_requiered
def submit_answer():
    """Check if user answered a question and redirect accordingly."""
    data, selection_data = db.list_question_objects_lite()
    if request.method == "POST":
        selection = request.form.get("id")
        if selection:
            answer = request.form.get("answer")
            question_obj = db.get_question_by_obj_id(selection)
            db.write_answer_to_mongo(question_obj, answer)

            return render_template(
                "answer_submitted_successfully.html",
                answer=answer,
                question=question_obj.question,
            )
        else:
            return render_template(
                "no_question_selected.html", title="Answer not submitted"
            )

    return render_template(
        "submit_answer.html",
        title="Submit Answer",
        data=data,
        selection_data=selection_data,
    )


@app.route("/get-tex/<tex_name>", methods=["GET", "POST"])
def get_image(tex_name):
    """
    Get a image to store for a question.

    str tex_name

    return image
    """
    try:
        return send_from_directory(
            app.config["CLIENT_TEX"], filename=tex_name, as_attachment=True
        )
    except FileNotFoundError:
        abort(404)


@app.route("/downloads", methods=["GET", "POST"])
@login_requiered
def downloads():
    """Let a user download questions."""
    data, selection_data = db.list_question_objects_2()
    if request.method == "POST":
        selection = request.form.getlist("id")
        if selection:
            zip_file_name = "questions" + str(uuid.uuid4()) + ".zip"
            file_name = "questions" + str(uuid.uuid4()) + ".tex"
            download = Download.get_questions_by_selection(selection)
            Download.zip_download(download, zip_file_name, file_name)
            return send_from_directory(
                "static/clients/zip", zip_file_name, as_attachment=True
            )
        return redirect(request.url)
    return render_template(
        "downloads.html", title="Downloads", data=data, selection_data=selection_data
    )


@app.route("/game", methods=["GET", "POST"])
@login_requiered
def game() -> Any:
    cu_amount = db.get_amount_of_cus_in_course("Operating Systems")

    # This is for when the user resets its progress on the game or we create an entire new connection
    matrix_cp = matrix.init_matrix(cu_amount)

    # matrix_cp =
    course = Course.objects(name="Operating Systems").first()
    user = User.objects(first_name="Jørgen", last_name="Fagervik").first()
    user_matrix = matrix.get_matrix(user, course, cu_amount)
    print(user_matrix)
    # if not np.array_equal(user_matrix, matrix_cp):

    # List of cu's
    cu1 = None
    cu2 = None

    cu_list = db.get_course("Operating Systems")
    while cu1 == cu2:
        cu1 = random.choice(cu_list)
        cu2 = random.choice(cu_list)

    cu1_index = cu_list.index(cu1)
    cu2_index = cu_list.index(cu2)

    print(cu1_index, cu2_index)
    question_string = f"How important is {cu1} to {cu2}?"

    # list of previous mapping if exists
    init_matrix = matrix.init_matrix(3)

    new_cu_matrix = []
    """Let user play game to map out a course"""
    data, sel_data = db.list_question_objects_2()
    if request.method == "POST":
        # User has now mapped something and we got a list/matrix of questions to store
        # Need to send what we've got back to database and possibly map out

        if request.form["btn_value"] == 1:
            pass

        return redirect(request.url)  # ?

    return render_template(
        "game.html",
        course="Operating Systems",
        code="TDT4186",
        title="Game",
        data=data,
        selection_data=sel_data,
        question_string=question_string,
    )


@app.after_request
def add_headers(response):
    """
    Add headers to a response message.

    return str response
    """
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
    return response


if __name__ == "__main__":
    app.run()
