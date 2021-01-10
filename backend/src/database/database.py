"""
database.py
This file contains functions for interacting with a Mongo database through python
Among the inclucions are functions for adding, updating, deleting and querying for each table described in models-> models.py

Classes:
    


Functions:
    Adding:
        add_user(name: str, nationality, pos: str, university, courses=None) -> User
        add_country(name: str, universities=None) -> Country
        add_university(name, country) -> University
        add_course(name, code, semester, kcs=None) -> Course
        add_kc(name, courses=None) -> KC
        add_connection(user, course, semester, kc_list, kc_matrix, percentage=0.0) -> Connection
        add_question(...) -> Question
        add_test(name, course, questions=None) -> Test

    Updating:
        update_user_name(user, new_name)
        update_user_position(user, new_position)
        update_country()
        update_university(university, new_name)
        update_course_name(course, new_name) 
        update_course_code(course, new_name) 
        update_course_kc_list(course, kc) 
        update_kc(kc, new_name) 
        update_connection(connection, new_map, percentage) 
        update_question_name(question, new_question) 
        update_question_correct_answer(question, new_correct_answer) 
        update_test_name(test, new_name) 

    Add values to list:
        add_course_to_kc(kc, course) 
        add_kc_to_course(course, kc) 
        update_kc_course_list(kc, course) 
        add_options_to_question(question, options) 

    Delete:
        delete_user(fn, ln)
        delete_country(name)
        delete_university(name)
        delete_course(code)
        delete_kc(name)
        delete_connection(course)
        delete_question(question_number)
        delete_test(name)
    
    Querying:
        find_user_by_name(name: str) -> User
        find_country(name: str) -> Country
        find_course(code: str) -> Course
        find_kc_by_name(name: str) -> KC
        find_university(name: str) -> University
        find_map_connection(user, course, semester)
        get_kc_list_course(course_code: str) -> Course
        get_kc_matrix(user: User, course: Course) -> np.array
        get_kc_matrices_course(course_code, course_name: str) -> np.array
        get_kc_matrices_user(user_name: str) -> np.array
        get_questions_by_kc(name) -> dict
        get_questions_by_kc_taxonomy(name) -> dict
        get_questions_by_course(name) -> dict

Misc variables:



Todo:
    update_kc_course_list: make this work and not reset list every time

"""


"""import datetime
from bson.objectid import ObjectId

from mongoengine import connect, disconnect
from src.database.models.models import Course, Connection, User, University, KC, Country, Question, Test

import numpy as np


#######
# ADD #
#######


def add_user(name: str, nationality, pos: str, university, courses=None) -> User:
    name = name.split()
    fn = name[0]
    last = len(name) - 1
    if len(name) > 2:
        mn = name[1:last].join()
    ln = name[last]
    return User(
        first_name=fn,
        last_name=ln,
        nationality=nationality,
        position=pos,
        university=university,
        courses=courses).save()


def add_country(name: str, universities=None) -> Country:
    if universities:
        return Country(name=name, universities=universities).save()
    else:
        return Country(name=name).save()


def add_university(name, country) -> University:
    return University(name=name, country=country).save()


def add_course(name, code, semester, kcs=None) -> Course:
    if kcs:
        return Course(name=name, code=code, kcs=kcs, semester=semester).save()
    else:
        return Course(name=name, code=code, kcs=[], semester=semester).save()


def add_kc(name, courses=None) -> KC:
    # TODO: Courses is actually a single course here, should probably get both course list and course itself
    if courses:
        return KC(name=name, courses=[courses]).save()
    else:
        return KC(name=name, courses=[]).save()


def add_connection(user, course, semester, kc_list, kc_matrix, percentage=0.0) -> Connection:
    #  TODO: Course or course.id? Should be course rigth?
    return Connection(user=user, course=course, semester=semester, kc_list=kc_list, kc_matrix=kc_matrix,
                      percentage=percentage, last_updated=datetime.datetime.now()).save()




def add_question(question_number, question, author, course, kc_list, kc_taxonomy, correct_answer, options,
                 author_email = None, QuestionType = None, notes_teacher = None, notes_student = None,
                 feedback_student = None, question_disclosability = None, solution_disclosability = None, test=None) -> Question:
    return Question(question_number=question_number, question=question, author=author ,course=course, kc_list=kc_list, kc_taxonomy = kc_taxonomy, correct_answer=correct_answer, options=options ,
                    author_email = author_email, QuestionType = QuestionType, notes_teacher = notes_teacher, notes_student = notes_student,
                 feedback_student = feedback_student, question_disclosability = question_disclosability, solution_disclosability = solution_disclosability, test=test). save()




def add_test(name, course, questions=None) -> Test:
    return Test(name=name, course=course, questions=questions).save()


##########
# UPDATE #
##########


def update_user_name(user, new_name):
    names = new_name.split()
    fn, ln = names[0], names[-1]
    user.update(first_name=fn, last_name=ln)


def update_user_position(user, new_position):
    if new_position not in ["STUDENT", "PROFESSOR", "OTHER"]:
        return
    user.update(position=new_position)


def update_country():
    raise NotImplementedError


def update_university(university, new_name):
    university.update(name=new_name)


def update_course_name(course, new_name):
    course.update(name=new_name)


def update_course_code(course, new_code):
    course.update(code=new_code)


def update_course_kc_list(course, kc):
    if course.kcs:
        if kc not in course.kcs:
            course.update(push__kcs=kc)
            print(f"{kc.name} added to {course.name}")
    else:
        course.update(kcs=[kc])
        print(f"{course.name} now has a kc")


def update_kc(kc, new_name):
    kc.update(set__name=new_name)


def update_connection(connection, new_map, percentage):
    connection.update(kc_matrix=new_map, percentage=percentage,
                      last_updated=datetime.datetime.now())


def update_question_name(question, new_question):
    question.update(question=new_question)


def update_question_correct_answer(question, new_correct_answer):
    question.update(correct_answer=new_correct_answer)


def update_test_name(test, new_name):
    test.update(name=new_name)


def update_test_name(test, new_name):
    test.update(name=new_name)


###################################
# ADD VALUES TO LIST IN DOCUMENTS #
###################################

def add_course_to_kc(kc, course):
    kc.update(add_to_set__courses=[course])


def add_kc_to_course(course, kc):
    course.update(add_to_set__kcs=[kc])


# TODO: make this work and not reset list every time
def update_kc_course_list(kc, course):
    if kc.courses:
        if course not in kc.courses:
            kc.update(push__courses=course,
                      last_updated=datetime.datetime.now())
            print(f"{course.name} added to {kc.name}")
    else:
        kc.update(courses=[course], last_updated=datetime.datetime.now())
        print(f"{kc.name} now has a course")


def add_options_to_question(question, options):
    question.update(add_to_set__options=[options])


##########
# DELETE #
##########


def delete_user(fn, ln):
    return User.objects(first_name=fn, last_name=ln).delete()


def delete_country(name):
    return Country.objects(name=name).delete()


def delete_university(name):
    return University.objects(name=name).delete()


def delete_course(code):
    return Course.objects(code=code).delete()


def delete_kc(name):
    return KC.objects(name=name).delete()


def delete_connection(course):
    return Connection.objects(course=course).delete()


def delete_question(question_number):
    return Question.objects(question_number=question_number).delete()


def delete_test(name):
    return Test.objects(name=name).delete()


##############
# FIND USERS #
##############

def find_user_by_name(name: str) -> User:
    names = name.split()
    fn, ln = names[0], names[-1]
    return User.objects(first_name=fn, last_name=ln).first()


def find_country(name: str) -> Country:
    return Country.objects(name=name).first()


################
# FIND COURSES #
################

def find_course(code: str) -> Course:
    return Course.objects(code=code).first()

############
# FIND KCs #
############


def find_kc_by_name(name: str) -> KC:
    return KC.objects(name=name).first()


def find_university(name: str) -> University:
    return University.objects(name=name).first()


def find_map_connection(user, course, semester):
    return Connection.objects(user=user, course=course, semester=semester).first()


##########################
# GET LISTS AND MATRICES #
##########################


def get_kc_list_course(course_code: str):
    return Course.objects(code=course_code).first().kcs


def get_kc_matrix(user: User, course: Course):
    fn = user.first_name
    ln = user.last_name

    user = User.objects(first_name=fn, last_name=ln).first()
    course = Course.objects(code=course.code).first()

    conn = Connection.objects(user=user, course=course).first()
    return np.array(conn.kc_matrix)


def get_kc_matrices_course(course_code, course_name: str):
    """ TEACHERS WILL USE THIS FOR AVERAGE """
    course = Course.objects(name=course_name, code=course_code).first()
    conns = Connection.objects(course=course)
    kc_matrices = [conn.kc_matrix for conn in conns]

    return np.array(kc_matrices)


def get_kc_matrices_user(user_name: str):
    user = User.objects(name=user_name).first()
    conns = Connection.objects(user=user)
    kc_matrices = [conn.kc_matrix for conn in conns]

    return np.array(kc_matrices)


##########################
# GET Questions #
##########################

def get_questions_by_kc(name):
    kc = KC.objects(name=name).first()
    questions_obj = Question.objects(kc_list = kc)
    questions = [ques.question for ques in questions_obj ]
    correct_ans = [ques.correct_answer for ques in questions_obj ]
    options = [ques.options for ques in questions_obj]
    kc_object = [ques.kc_list for ques in questions_obj]

    kc_list = []
    for i in kc_object:
        kc = []
        for j in i:
            kc.append(j.name)
        kc_list.append(kc)

    kc_taxonomy = [ques.kc_taxonomy for ques in questions_obj]

    author_email = [ques.author_email for ques in questions_obj]
    QuestionType = [ques.QuestionType for ques in questions_obj]
    notes_teacher = [ques.notes_teacher for ques in questions_obj]
    notes_student = [ques.notes_student for ques in questions_obj]
    feedback_student = [ques.feedback_student for ques in questions_obj]
    question_disclosability = [ques.question_disclosability for ques in questions_obj]
    solution_disclosability = [ques.solution_disclosability for ques in questions_obj]



    return {"Questions" : questions, "answer": correct_ans, "Options": options, "kc" : kc_list, "kc_taxonomy" : kc_taxonomy, "author_email" : author_email,
            "QuestionType": QuestionType, "notes_teacher": notes_teacher, "notes_student" :notes_student, "feedback_student": feedback_student,
            "question_disclosability": question_disclosability, "solution_disclosability": solution_disclosability }

def get_questions_by_kc_taxonomy(level):
    taxonomy_level = level
    questions_obj = Question.objects(kc_taxonomy = taxonomy_level)
    questions = [ques.question for ques in questions_obj ]
    correct_ans = [ques.correct_answer for ques in questions_obj ]
    options = [ques.options for ques in questions_obj]

    return {"Questions" : questions, "answer": correct_ans, "Options": options}

def get_questions_by_course(name):
    course = Course.objects(name=name).first()
    questions_obj = Question.objects(course=course)
    questions = [ques.question for ques in questions_obj]
    correct_ans = [ques.correct_answer for ques in questions_obj]
    options = [ques.options for ques in questions_obj]

    return {"Questions": questions, "answer": correct_ans, "Options": options}

"""