from mongoengine import connect
from flask import session
from backend.models.models import KC, Course, Question, Answer

client = connect(db="KCMap",
                 username="developer",
                 password="TTK4260",
                 host="mongodb+srv://developer:TTK4260@kcbank.lwcpe.mongodb.net/KCMap?retryWrites=true&w=majority")


def list_question_objects() -> Question:
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


def list_questions() -> Question:
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
        list_item = [question, taxonomy_level]
        object_list.append(list_item)
    return object_list, selection_list

def write_answer_to_mongo(question_id, answer):
    my_string = session["user"]
    result_start = my_string.find('username') + 12
    result_end = my_string.find('email') - 4
    author = session["user"][result_start:result_end]
    answer_form = Answer(
        question_id = question_id,
        author_name = author,
        answer = answer
    )
    answer_form.save()

    return 