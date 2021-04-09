from flask import Flask, render_template, url_for, redirect, request, send_from_directory, abort, session, jsonify
from functools import wraps
from werkzeug.utils import secure_filename

from backend.upload.upload_script import Upload
from backend.download.download_script import Download
from backend.user.forms import RegistrationForm, LoginForm

from backend.user.models import User
import backend.graph.visualization as vis
import backend.graph.spreadsheet as ss

from backend.user.models import Account
from backend.models.models import University

import db
import os
import uuid
import time


import json

app = Flask(__name__)
app.config.from_object("config.DevelopmentConfig")

if not os.path.exists(app.config["TEX_UPLOADS"]):
    os.makedirs(app.config["TEX_UPLOADS"])


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
    db.add_uni()
    form = RegistrationForm()
    form.university.choices = [
        universities.name for universities in University.objects()]
    if request.method == 'POST' and form.validate():
        if Account().signup(form):
            return redirect('/')
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        return Account().login()
    return render_template('login.html', title='Login', form=form)


@app.route("/logout")
def signout():
    return Account().signout()


def allowed_file(filename):
    if not "." in filename:
        return False

    ext = filename.rsplit(".", 1)[1]

    if ext.upper() in app.config["ALLOWED_EXTENSIONS"]:
        return True
    else:
        return False

@app.route("/graphviz/<sheet>/")
def graphs(sheet):
    #ss.upload_CU_file("filename")
    #lists = ss.read_course_category_tree("linear-algebra", "specification of the content units' hierarchies", 4)
    #lists = ss.read_course_category_tree("Course_content_signals", "specification of the content un", 4)
    #print("Lists:",lists)
    #print()
    #nodes, edges = vis.get_nodes_and_edges_cu_hierarchies(lists)
    #print()
    #lists = ss.read_course_category_tree("testing", "specification of the content un", 4)
    lists = ss.read_course_category_tree(sheet, "content units hierarchies", 5)
    #print("Lists:",lists)
    #print()
    nodes, edges = vis.get_nodes_and_edges_cu_hierarchies(lists)
    print()
    print("Nodes", nodes, "\n")
    print("Edges:", edges, "\n")
    #print()
    #print("Values:",nodes)
    return render_template("graphviz.html", title='Visualize graphs',nodes=nodes, edges=edges)

@app.route("/graphlist")
def graph_list():
    ss.delete_all_files()
    available_CU_files = ss.get_available_CU_files()
    return render_template("graphlist.html", title="Graph list", CU_files=available_CU_files)


@app.route("/upload_excel", methods=["GET", "POST"])
def upload_excel():
    if request.method == "POST":
        if request.files:
            excel_file = request.files["xlsx"]
            if excel_file.filename == "":
                print("No filename")
                return redirect(request.url)
            if excel_file.filename[-5:] == ".xlsx":
                print("Working file upload")
                ss.upload_CU_file(excel_file)
                return redirect(request.url)
            else:
                print("That file extension is not allowed")
                return redirect(request.url)
            
    return render_template("upload_excel.html", title="Upload Excel")




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


@app.route("/submit_answer", methods=["GET", "POST"])
@login_requiered
def show_questions():
    data, selection_data = db.list_question_objects()

    if request.method == "POST":
        selected_question = request.form.get('question_button')
        messages = json.dumps({"selected_question_id": selected_question})
        return redirect(url_for('answer_selected_question', messages=messages))

    return render_template("submit_answer/question_list.html", data=data, selection_data=selection_data)


@app.route("/submit_answer/answer_selected_question", methods=["GET", "POST"])
@login_requiered
def answer_selected_question():
    messages = request.args['messages']
    selected_question_id = json.loads(messages)['selected_question_id']

    if request.method == "POST":
        selected_multiple_choice_answer = request.form.get('id')
        if not selected_multiple_choice_answer:
            return render_template("submit_answer/error_no_answer_selected.html", title='Answer not submitted')

        question_id = request.form.get('multiple_choice_button')
        written_answer = request.form.get('written_answer')
        perceived_difficulty = request.form.get('rating')

        messages = json.dumps({"selected_multiple_choice_answer": selected_multiple_choice_answer, 
                                "question_id": question_id, 
                                "written_answer": written_answer, 
                                "perceived_difficulty": perceived_difficulty})

        return redirect(url_for('show_submission_info', messages=messages))

    selected_question_obj = db.get_question_by_obj_id(selected_question_id)
    list_of_options, idx_list_for_options = db.get_answer_options_from_question_obj(selected_question_obj)
    question_image = db.get_question_image(selected_question_obj.id)

    current_user_role = db.get_user_role()
    if current_user_role == 'Admin' or current_user_role == 'Teacher':
        correct_answer = "The correct answer is: " + selected_question_obj.correct_answer[0]
    else: # current_user_role == 'Student'
        correct_answer = None

    return render_template("submit_answer/selected_question_page.html", data=list_of_options, selection_data=idx_list_for_options, question_id = selected_question_obj.id, 
                            question_text = selected_question_obj.question, correct_answer=correct_answer, question_image=question_image)


@app.route("/submit_answer/successfully_submitted", methods=["GET"])
@login_requiered
def show_submission_info():
    messages = request.args['messages']
    selected_multiple_choice_answer = json.loads(messages)['selected_multiple_choice_answer']
    question_id = json.loads(messages)['question_id'] 
    written_answer = json.loads(messages)['written_answer'] 
    perceived_difficulty = json.loads(messages)['perceived_difficulty'] 

    answered_question_obj = db.get_question_by_obj_id(question_id)
    db.write_answer_to_mongo(answered_question_obj, written_answer, selected_multiple_choice_answer, perceived_difficulty)

    options_list = answered_question_obj.options
    display_answer = str(options_list[int(selected_multiple_choice_answer)])

    data, _ = db.list_question_objects()
    info_plot = db.make_bar_plot(data)
    perceived_difficulty = db.get_avg_perceived_difficulty(question_id)

    return render_template("submit_answer/answer_submitted_successfully.html", answer=display_answer,question=answered_question_obj.question, plot=info_plot, perceived_difficulty=perceived_difficulty)

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


