from typing import List, Tuple

from mongoengine import connect
from flask import session
from backend.models.models import (
    KC,
    Course,
    Question,
    Answer,
    Register,
    University,
    Country,
)


client = connect(
    db="KCMap",
    username="developer",
    password="bruxellesmagdeburgpadovatrondheimuppsala",
    host="mongodb+srv://developer:bruxellesmagdeburgpadovatrondheimuppsala@la.ntmol.mongodb.net/KCMap?retryWrites=true&w=majority",
    connectTimeoutMS=30000,
    socketTimeoutMS=None,
    socketKeepAlive=True,
    connect=False,
    maxPoolsize=1,
)


def list_question_objects() -> Question:
    """Return an object list and a list of selections"""
    object_list = []
    selection_list = []
    for elements in Question.objects():
        selection_list.append(elements.id)
        question = elements.question
        course = elements.course
        course_name = course.name if course is not None else "empty"
        kcs = elements.kc_list
        kc_name = []
        for kc in kcs:
            kc_name.append(kc.name)
        taxonomy_level = elements.kc_taxonomy
        list_item = [question, course_name, kc_name, taxonomy_level]
        object_list.append(list_item)
    return object_list, selection_list


def list_question_objects_2() -> Tuple[List[list], list]:
    """Return an object list and a list of selections"""

    # TODO: give this function a better name please :P
    object_list = []
    selection_list = []
    for elements in Question.objects():
        selection_list.append(elements.id)
        question = elements.question
        course_name = elements.course_name
        kc_name = elements.kc_names_list
        taxonomy_level = elements.kc_taxonomy
        list_item = [question, course_name, kc_name, taxonomy_level]
        object_list.append(list_item)
    return object_list, selection_list


def list_question_objects_lite() -> Question:
    """Return an object list and a list of selections"""

    # TODO: Okay now you're just out of names :P
    object_list = []
    selection_list = []
    for elements in Question.objects():
        selection_list.append(elements.id)
        question = elements.question
        course_name = elements.course_name
        kc_name = elements.kc_names_list
        taxonomy_level = elements.kc_taxonomy
        list_item = [question, course_name]
        object_list.append(list_item)
    return object_list, selection_list


def write_answer_to_mongo(question, answer):
    """
    Retrieve an answer and send it to the database.
    """
    my_string = session["user"]

    username_str_start = my_string.find("username") + 9
    username_str_end = my_string.find("email") - 4
    email_str_start = my_string.find("email") + 9
    email_str_end = my_string.find("password") - 4

    user_name = session["user"][username_str_start:username_str_end]
    user_email = session["user"][email_str_start:email_str_end]
    user = Register.objects(email=user_email).first()

    Answer.objects(question=question, user=user).update_one(
        user_name=user_name, answer=answer, upsert=True
    )


def get_question_by_obj_id(selections) -> str:
    """
    Get a question if object id matches.

    str selections
    """
    for ques in Question.objects():
        db_id = str(ques.id)
        if selections == db_id:
            return ques
    return "Didn't find the question!"


def get_course(name):
    cu_list = []
    for c in Course.objects():
        if name == c.name:
            cus = c.cus
            for cu in cus:
                cu_list.append(cu.name)
            return cu_list
    return


def manually_add_stuff():

    """
    Add a university to the database.
    """
    # TODO: Remove default name after checking if this works.
    if not Course.objects(name="Operating Systems"):
        return Course(name="Operating Systems", code="TDT4186", semester="V21").save()
    if not University.objects(name="Otto-von-Guericke-Universität"):
        c = Country.objects(name="Germany").first()
        return University(name="Otto-von-Guericke-Universität", country=c).save()
    return "Uni already exists!"


def get_amount_of_cus_in_course(course: str) -> int:
    return len(Course.objects(name=course).first().cus)