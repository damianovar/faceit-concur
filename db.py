from config import ProductionConfig
from typing import List, Tuple

from mongoengine import connect
from flask import session

from bson.objectid import ObjectId
import time
from backend.models.models import CU, Course, Question, QuestionAnswer, Institution, Country, User, CUConnection

import matplotlib
import matplotlib.pyplot as plt
from io import BytesIO
import base64
import numpy as np
from collections import Counter
import ssl

# uppsala trondheim padova magdeburg bruxelles

client = connect(db       ="FaceIT-DB",
                 username ="developer",
                 password ="bruxelles magdeburg padova trondheim uppsala",
                 host     ="mongodb+srv://developer:bruxellesmagdeburgpadovatrondheimuppsala@la.ntmol.mongodb.net/FaceIT-DB?retryWrites=true&w=majority",
                 connectTimeoutMS =30000,
                 socketTimeoutMS  =None,
                 socketKeepAlive  =True,
                 connect          =False,
                 maxPoolsize      =1,
                ssl_cert_reqs=ssl.CERT_NONE)

def list_filtered_question_objects():
    """
        Goes through the collection of questions (object type Question)
        on the MongoDB server, and extracts the data into python lists

        list_of_questions_attributes -> question text and question attributes
        list_of_questions_IDs -> question IDs
    """

    # storage allocation
    list_of_questions_attributes    = []
    list_of_questions_IDs = []

    filtering = CU.objects(name= "complex numbers").first()
    # scan all the questions in the MongoDB
    for question in Question.objects(body__contains = "number"):

        # save the id
        list_of_questions_IDs.append(question.id)

        # save the course name
        course_list = [course.name for course in question.courses]
        if not course_list:
            course_list = ['N.D.']

        # if course_name is None:
        #     course_name = 'empty'

       # store the interesting attributes
        attributes_of_current_question = \
                [question.body,
                 course_list,
                 [cu.name for cu in question.content_units],
                 #question.taxonomy_levels
                 ]
        # push them in the list
        list_of_questions_attributes.append(attributes_of_current_question)

    return list_of_questions_attributes, list_of_questions_IDs
                   
def list_question_objects(question_type='multiple choice'):
    """
        Goes through the collection of questions (object type Question)
        on the MongoDB server, and extracts the data into python lists
 
        list_of_questions_attributes -> question text and question attributes
        list_of_questions_IDs -> question IDs
    """

    # storage allocation
    list_of_questions_attributes    = []
    list_of_questions_IDs = []

    # scan all the questions in the MongoDB
    for question in Question.objects():

        # save the id
        list_of_questions_IDs.append(question.id)

        # save the course name
        course_list = [course.name for course in question.courses]
        if not course_list:
            course_list = ['N.D.']

        # if course_name is None:
        #     course_name = 'empty'

       # store the interesting attributes
        attributes_of_current_question = \
                [question.body,
                 question.question_type,
                 course_list,
                 [cu.name for cu in question.content_units],
                 #question.taxonomy_levels
                 ]
        # push them in the list
        list_of_questions_attributes.append(attributes_of_current_question)

    return list_of_questions_attributes, list_of_questions_IDs


def write_answer_to_mongo(question, txt_answer, selected_answer, perceived_difficulty):
    """
        Given a question object and an answer to that question the function updates the Answer collection with the provided answer.
        If the question has already been answered by the same user, the answer is overridden, otherwise a new answer object is added to collection.
    """
    #session_data_string = session["user"]

    #username_str_start = session_data_string.find('username') + 9
    username = session.get("user").get("username")
    user = User.objects(username=username).first()
    # email = user.get("email")
    # username_str_end = session_data_string.find('email') - 4
    # email_str_start = session_data_string.find('email') + 9
    # email_str_end = session_data_string.find('password') - 4

    # user_name = session["user"][username_str_start:username_str_end]
    # user_email = session["user"][email_str_start:email_str_end]
    # user = User.objects(email=user_email).first()

    # If difficulty is not rated, set the rating to -1
    print(selected_answer)
    if perceived_difficulty == None:
        perceived_difficulty = -1

    QuestionAnswer.objects(question = question, user = user).update_one( \
            #answer=txt_answer,
            selected_answer=selected_answer,
            perceived_difficulty=perceived_difficulty,
            upsert=True)


def get_user_obj():
    """
        Accesses the session data and retrieves the current user obj
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
    user = session.get("user").get("username")
    return User.objects(username=user).first().role


def get_question_image(question_id):
    """
        Loads in image from the question object given by the question id 
        and returns the decoded image as base64 byte string.
    """

    question_obj = Question.objects(id = str(question_id)).first()

    image_raw = question_obj.body_image.read()
    if image_raw is None:
        return None

    # Turn the image into a base64 byte string (decoded using utf-8 charset)
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
    # list_of_options = [[x] for x in selected_question_obj.options]
    # idx_list_for_options = list(range(0, len(selected_question_obj.options)))
    if selected_question_obj.question_type == 'multiple choice':
        list_of_options = selected_question_obj.potential_answers
        idx_list_for_options = list(range(0, len(selected_question_obj.potential_answers)))  
    elif selected_question_obj.question_type == 'numeric':
        list_of_options = None
        idx_list_for_options = None
    return list_of_options, idx_list_for_options


def get_avg_perceived_difficulty(question_id):
    """
        Given question ID, looks up the Answer collection and retrieves all recorded perceived difficulty scores for that question
        Returns the average perceived difficulty score
    """
    perceived_difficulty_list = QuestionAnswer.objects(question=get_question_by_obj_id(question_id)).values_list('perceived_difficulty')
    if len(perceived_difficulty_list) > 0:
        print(perceived_difficulty_list)
        perceived_difficulty_list_valid = [item for item in perceived_difficulty_list if item != None and item >= 0]
        perceived_difficulty = np.format_float_positional(np.mean(np.array(perceived_difficulty_list_valid)),1)
    else:
        perceived_difficulty = 0
    return perceived_difficulty

def make_correctness_percentage_plot(question_id):
    """
        Example function which retrives desired data,
        in this case number of total questions and number of
        unanswered questions by the current user
        and creates a matplotlib barplot based on that data.
        The barplot is returned as a base64 byte string
        which is easy to display in HTML
    """
    question_correct_answer = np.argmax(np.array(get_question_by_obj_id(question_id).correctness_of_the_answers))
    question_answers = QuestionAnswer.objects(question=question_id)
    selected_answers_array = np.array([question_answer.selected_answer for question_answer in question_answers])
    #print(selected_answer_array[selected_answers_array == question_correct_answer] = 0)


def make_course_plot(question_id):
    #courses_name = [course.name for course in courses]
    course_dict = dict()
    # Get the courses associated to the questions
    if not get_question_by_obj_id(question_id).courses:
        return None

    for course in get_question_by_obj_id(question_id).courses:
        questions_of_course = Question.objects(courses__in=[course])
        number_of_course_questions = len(questions_of_course)
        number_of_course_answers = 0
        number_of_course_correct_answers = 0
        for question in questions_of_course:
            user = User.objects(username=session.get("user").get("username")).first()
            question_correct_answer_idx = np.argmax(np.array(question.correctness_of_the_answers))
            if QuestionAnswer.objects(user=user, question=question): # if current user has answered the current question of the course           
                number_of_course_answers += 1               
                if QuestionAnswer.objects(user=user, question=question).first().selected_answer == question_correct_answer_idx:
                    number_of_course_correct_answers += 1

        course_dict[course.name] = [number_of_course_questions, number_of_course_answers, number_of_course_correct_answers]
    
    labels = list(course_dict.keys())
    total = np.array(list(course_dict.values()))[:,0]
    answered = np.array(list(course_dict.values()))[:,1]
    correct = np.array(list(course_dict.values()))[:,2]
    x = np.arange(len(labels))  # the label locations
    width = 0.20  # the width of the bars

    # Create barplot
    fig, ax = plt.subplots()
    ax.bar(x - width, total, width, label='total')
    ax.bar(x, answered, width, label='answered')
    ax.bar(x + width, correct, width, label='correct')
    ax.set_ylabel('Number of questions')
    ax.set_xlabel('Courses')
    ax.set_title('answered question per course')
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.legend()
    ax.grid()
    fig.tight_layout()

    figfile = BytesIO()
    plt.savefig(figfile, format='png')
    figfile.seek(0)  # rewind to beginning of file
    
    # Turn the figure into a base64 byte string (decoded using utf-8 charset)
    figdata_png = base64.b64encode(figfile.read()).decode("utf-8")
    return figdata_png


def make_bar_plot(question_data):
    """
        Example function which retrives desired data,
        in this case number of total questions and number of
        unanswered questions by the current user
        and creates a matplotlib barplot based on that data.
        The barplot is returned as a base64 byte string
        which is easy to display in HTML
    """
    course_data = []
    for row in question_data:
        course_data.append(row[1])

    unique_courses_names = list(Counter(course_data).keys()) # equals to list(set(words))
    unique_courses_instances = Counter(course_data).values() # counts the elements' frequency

    answered_questions_list = QuestionAnswer.objects(user=get_user_obj()).values_list('question')
    
    answered_questions_course_names = []
    for item in answered_questions_list:
        if item.course_name is not None:
            answered_questions_course_names.append(item.course_name)
        else:
            answered_questions_course_names.append('empty')

    unique_answered_courses_instances = [0] * len(unique_courses_names)
    for course_name in answered_questions_course_names:
        idx = unique_courses_names.index(course_name)
        unique_answered_courses_instances[idx] += 1

    labels = unique_courses_names
    total = unique_courses_instances
    answered = unique_answered_courses_instances

    x = np.arange(len(labels))  # the label locations
    width = 0.30  # the width of the bars

    # Create barplot
    fig, ax = plt.subplots()
    ax.bar(x - width/2, total, width, label='total')
    ax.bar(x + width/2, answered, width, label='answered')
    ax.set_ylabel('Number of questions')
    ax.set_xlabel('Courses')
    ax.set_title('answered question per course')
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.legend()
    ax.grid()
    fig.tight_layout()

    figfile = BytesIO()
    plt.savefig(figfile, format='png')
    figfile.seek(0)  # rewind to beginning of file
    
    # Turn the figure into a base64 byte string (decoded using utf-8 charset)
    figdata_png = base64.b64encode(figfile.read()).decode("utf-8")
    return figdata_png


def get_course(name):
    cu_list = []
    for c in Course.objects():
        if name == c.name:
            cus = c.taught_cus_list
            for cu in cus:
                cu_list.append(cu.name)
            return cu_list
    return 'No course found with the name: "' + name + '"'


def get_amount_of_cus_in_course(course: str) -> int:
    return len(Course.objects(name=course).first().taught_cus_list)


# Example function to manually add data
def add_institution():
    if not Institution.objects(name="NTNU"):
        c = Country.objects(name="Norway").first()
        return Institution(name="NTNU", country=c).save()
    return "This institution already exists!"

# def add_cuconnection():
#     creator = User.objects(username="chlang").first()
#     course = Course.objects(name="Operating Systems").first()
#     cu_matrix = [
#         "0", 
#         "1", 
#         "2", 
#         "3", 
#         "0", 
#         "4", 
#         "5", 
#         "6", 
#         "0"
#     ]
#     print(course)
#     CUConnection(creator=creator,course=course,cu_matrix=cu_matrix ).save()
#     return 

# Test/Utility function, opens locally stored png image and uploads it to mongodb Question collection given question id 
def upload_image_to_question(question_id):
    question_id = "5f72f0e58373664b8505ea6b"
    question_obj = Question.objects(id = str(question_id)).first()
    with open('3x3_matrix.png', 'rb') as fd:
        question_obj.image.put(fd, content_type = 'image/png')
    question_obj.save()
    print("UPLOADED")
    return


