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


client = connect(db="KCMap",
                 username="developer",
                 password="TTK4260",
                 host="mongodb+srv://developer:TTK4260@kcbank.lwcpe.mongodb.net/KCMap?retryWrites=true&w=majority",
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
        if course is not None:
            course_name = course.name
        else:
            course_name = 'empty'
        kcs = elements.kc_list
        kc_name = []
        for kc in kcs:
            kc_name.append(kc.name)
        taxonomy_level = elements.kc_taxonomy
        list_item = []
        list_item = [question, course_name, kc_name, taxonomy_level]
        object_list.append(list_item)
    return object_list, selection_list

def list_question_objects() -> Question:
    """
        Goes through the question database and extracts the data into python lists

        Returns two lists:
        object_list - question text and misc "course name, CU , ..."
        selection_list - MongoDB question object id's 
    """
    object_list = []
    selection_list = []
    for elements in Question.objects():
        selection_list.append(elements.id)
        question = elements.question
        course_name = elements.course_name
        kc_name = elements.kc_names_list
        taxonomy_level = elements.kc_taxonomy
        list_item = []
        list_item = [question, course_name, kc_name, taxonomy_level]
        object_list.append(list_item)
    return object_list, selection_list

def write_answer_to_mongo(question, txt_answer, selected_option, perceived_difficulty):
    """
        Given a question object and an answer to that question the function updates the Answer collection with the provided answer.
        If the question has already been answered by the same user, the answer is overridden, otherwise a new answer object is crated.
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

def get_user_role():
    """
        Accesses the session data and retrives the current user's role
        The role is returned as a string: "Admin", "Teacher" or "Student"
    """
    session_data_string = session["user"]

    email_str_start = session_data_string.find('email') + 9
    email_str_end = session_data_string.find('password') - 4

    user_email = session["user"][email_str_start:email_str_end]
    user = User.objects(email=user_email).first()

    return user.role

def get_user():
    """
        Accesses the session data and retrives the current user obj
    """
    session_data_string = session["user"]

    email_str_start = session_data_string.find('email') + 9
    email_str_end = session_data_string.find('password') - 4

    user_email = session["user"][email_str_start:email_str_end]
    user = User.objects(email=user_email).first()

    return user

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

    if image_raw is not None:
        base64_image = base64.b64encode(image_raw).decode("utf-8")
    else:
        return None

    return base64_image

def get_question_by_obj_id(question_id):
    """
        Retrieves question object from Question collection given question-object id
    """
    question_obj = Question.objects(id = str(question_id)).first()
    return question_obj

def add_uni():
    if not University.objects(name="Otto-von-Guericke-Universität"):
        c = Country.objects(name="Germany").first()
        return University(name="Otto-von-Guericke-Universität", country=c).save()
    return "Uni already exists!"

def get_answers_data():
    answered_questions_list = Answer.objects(user=get_user()).values_list('question')
    answered_questions_course_names = [x.course_name if x is not None else 'empty' for x in answered_questions_list]
    return answered_questions_course_names

def get_perceived_difficulty(question_id):
    perceived_difficulty_list = Answer.objects(question=get_question_by_obj_id(question_id)).values_list('perceived_difficulty')
    if len(perceived_difficulty_list) > 0:
        print(perceived_difficulty_list)
        perceived_difficulty_list_valid = [item for item in perceived_difficulty_list if item != None and item >= 0]
        perceived_difficulty = np.mean(np.array(perceived_difficulty_list_valid))
    else:
        perceived_difficulty = 0
    return perceived_difficulty
    

def make_bar_plot(data, selection_data):
    course_data = []
    for row in data:
        course_data.append(row[1])

    unique_courses_names = list(Counter(course_data).keys()) # equals to list(set(words))
    unique_courses_instances = Counter(course_data).values() # counts the elements' frequency

    answered_questions_course_names = get_answers_data()

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
    rects1 = ax.bar(x - width/2, Total, width, label='Total')
    rects2 = ax.bar(x + width/2, Answered, width, label='Answered')

    # Add some text for labels, title and custom x-axis tick labels, etc.
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

# Utility function, opens locally stored png image and uploads it to mongodb Question collection 
def upload_image_to_question(question_id):
    question_id = "5f72f0e58373664b8505ea6b"
    question_obj = Question.objects(id = str(question_id)).first()
    with open('3x3_matrix.png', 'rb') as fd:
        question_obj.image.put(fd, content_type = 'image/png')
    question_obj.save()
    print("UPLOADED")
    return