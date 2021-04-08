from typing import List

from mongoengine import connect
from flask import session
from bson.objectid import ObjectId
import time
from backend.models.models import KC, Course, Question, Answer, Register, University, Country, User

import matplotlib
import matplotlib.pyplot as plt
from io import BytesIO
import base64
import numpy as np
from collections import Counter

## old data base
#password="TTK4260",
#host="mongodb+srv://developer:TTK4260@kcbank.lwcpe.mongodb.net/KCMap?retryWrites=true&w=majority",

client = connect(db="KCMap",
                 username="developer",
                 password="bruxellesmagdeburgpadovatrondheimuppsala",
                 host="mongodb+srv://developer:bruxellesmagdeburgpadovatrondheimuppsala@la.ntmol.mongodb.net/KCMap?retryWrites=true&w=majority",
                 connectTimeoutMS=30000,
                 socketTimeoutMS=None,
                 socketKeepAlive=True,
                 connect=False,
                 maxPoolsize=1)

                     
def list_question_objects_old() -> Question:
    object_list = []
    selection_list = []
    for elements in Question.objects():
        selection_list.append(elements.id)
        question = elements.question
        course = elements.course
        course_name = course.name if course is not None else 'empty'
        kcs = elements.kc_list
        kc_name = []
        for kc in kcs:
            kc_name.append(kc.name)
        taxonomy_level = elements.kc_taxonomy
        list_item = [question, course_name, kc_name, taxonomy_level]
        object_list.append(list_item)
    return object_list, selection_list

def list_question_objects():
    """
        Goes through the Question collection on the MongoDB server and extracts the data into python lists
 
        object_list -> question text and question attributes
        selection_list -> question IDs
    """
    object_list = []
    selection_list = []
    for elements in Question.objects():
        selection_list.append(elements.id)
        question = elements.question
        course_name = elements.course_name
        kc_name = elements.kc_names_list
        taxonomy_level = elements.kc_taxonomy
        if course_name is None:
            course_name = 'empty'
        list_item = [question, course_name, kc_name, taxonomy_level]
        object_list.append(list_item)
    return object_list, selection_list

def write_answer_to_mongo(question, txt_answer, selected_option, perceived_difficulty):
    """
        Given a question object and an answer to that question the function updates the Answer collection with the provided answer.
        If the question has already been answered by the same user, the answer is overridden, otherwise a new answer object is added to collection.
    """
    session_data_string = session["user"]

    username_str_start = session_data_string.find('username') + 9
    username_str_end = session_data_string.find('email') - 4
    email_str_start = session_data_string.find('email') + 9
    email_str_end = session_data_string.find('password') - 4

    user_name = session["user"][username_str_start:username_str_end]
    user_email = session["user"][email_str_start:email_str_end]
    user = User.objects(email=user_email).first()

    # If difficulty is not rated, set the rating to -1
    if perceived_difficulty == None:
        perceived_difficulty = -1

    Answer.objects(question = question, user=user).update_one(user_name=user_name, answer=txt_answer, selected_option=selected_option, perceived_difficulty=perceived_difficulty, upsert=True)


def get_user_obj():
    """
        Accesses the session data and retrives the current user obj
    """
    session_data_string = session["user"]

    email_str_start = session_data_string.find('email') + 9
    email_str_end = session_data_string.find('password') - 4

    user_email = session["user"][email_str_start:email_str_end]
    user = User.objects(email=user_email).first()

    return user

def get_user_role():
    """
        Retrives user role and returns it as a string: "Admin", "Teacher" or "Student"
    """
    return get_user_obj().role

def get_question_image(question_id):
    """
        Loads in image from the question object given by the question id 
        and returns the decoded image as base64 byte string.
    """
    import sys
    from PIL import Image
    from io import BytesIO
    import base64

    question_obj = Question.objects(id = str(question_id)).first()

    image_raw = question_obj.image.read()
    if image_raw is None:
        return None

    base64_image = base64.b64encode(image_raw).decode("utf-8")
    return base64_image

def get_question_by_obj_id(question_id):
    """
        Retrieves question object from Question collection given question-object id
    """
    question_obj = Question.objects(id = str(question_id)).first()
    return question_obj

def get_answer_options_from_question_obj(selected_question_obj):
    """
        For a given question object, returns a list of answer options with a list of corresponding indices
    """
    list_of_options = [[x] for x in selected_question_obj.options]
    idx_list_for_options = list(range(0, len(selected_question_obj.options)))
    return list_of_options, idx_list_for_options

def get_avg_perceived_difficulty(question_id):
    """
        Given question ID, looks up the Answer collection and retrieves all recorded perceived difficulty scores for that question
        Returns the average perceived difficulty score
    """
    perceived_difficulty_list = Answer.objects(question=get_question_by_obj_id(question_id)).values_list('perceived_difficulty')
    if len(perceived_difficulty_list) > 0:
        print(perceived_difficulty_list)
        perceived_difficulty_list_valid = [item for item in perceived_difficulty_list if item != None and item >= 0]
        perceived_difficulty = np.format_float_positional(np.mean(np.array(perceived_difficulty_list_valid)),1)
    else:
        perceived_difficulty = 0
    return perceived_difficulty
    

def make_bar_plot(question_data):
    """
        Example function which retrives desired data, in this case number of total questions and number of unanswered questions by the current user
        and creates a matplotlib barplot based on that data. The barplot is returned as a base64 byte string which is easy to display in HTML
    """
    course_data = []
    for row in question_data:
        course_data.append(row[1])

    unique_courses_names = list(Counter(course_data).keys()) # equals to list(set(words))
    unique_courses_instances = Counter(course_data).values() # counts the elements' frequency

    answered_questions_list = Answer.objects(user=get_user_obj()).values_list('question')
    answered_questions_course_names = [x.course_name if x is not None else 'empty' for x in answered_questions_list]

    unique_answered_courses_instances = [0] * len(unique_courses_names)
    for course_name in answered_questions_course_names:
        idx = unique_courses_names.index(course_name)
        unique_answered_courses_instances[idx] += 1

    labels = unique_courses_names
    Total = unique_courses_instances
    Answered = unique_answered_courses_instances

    x = np.arange(len(labels))  # the label locations
    width = 0.30  # the width of the bars

    fig, ax = plt.subplots()
    ax.bar(x - width/2, Total, width, label='Total')
    ax.bar(x + width/2, Answered, width, label='Answered')
    ax.set_ylabel('Number of questions')
    ax.set_xlabel('Courses')
    ax.set_title('Answered question per course')
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.legend()
    ax.grid()
    fig.tight_layout()

    figfile = BytesIO()
    plt.savefig(figfile, format='png')
    figfile.seek(0)  # rewind to beginning of file
    
    figdata_png = base64.b64encode(figfile.read()).decode("utf-8")
    return figdata_png

def add_uni():
    if not University.objects(name="Otto-von-Guericke-Universität"):
        c = Country.objects(name="Germany").first()
        return University(name="Otto-von-Guericke-Universität", country=c).save()
    return "Uni already exists!"


# Test/Utility function, opens locally stored png image and uploads it to mongodb Question collection given question id 
def upload_image_to_question(question_id):
    question_id = "5f72f0e58373664b8505ea6b"
    question_obj = Question.objects(id = str(question_id)).first()
    with open('3x3_matrix.png', 'rb') as fd:
        question_obj.image.put(fd, content_type = 'image/png')
    question_obj.save()
    print("UPLOADED")
    return

