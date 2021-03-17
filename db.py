from mongoengine import connect
from flask import session
from backend.models.models import KC, Course, Question, Answer, Register, University, Country


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


def list_question_objects_lite() -> Question:
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
        list_item = [question, course_name]
        object_list.append(list_item)
    return object_list, selection_list

def write_answer_to_mongo(question, answer):
    my_string = session["user"]

    username_str_start = my_string.find('username') + 9
    username_str_end = my_string.find('email') - 4
    email_str_start = my_string.find('email') + 9
    email_str_end = my_string.find('password') - 4

    user_name = session["user"][username_str_start:username_str_end]
    user_email = session["user"][email_str_start:email_str_end]
    user = Register.objects(email=user_email).first()

    Answer.objects(question = question, user=user).update_one(user_name=user_name, answer=answer, upsert=True)

    
def get_question_by_obj_id(selections):
    for ques in Question.objects():
        db_id = str(ques.id)
        if selections == db_id:
            return ques
    return "Didn't find the question!"


def add_uni():
    if not University.objects(name="Otto-von-Guericke-Universität"):
        c = Country.objects(name="Germany").first()
        return University(name="Otto-von-Guericke-Universität", country=c).save()
    return "Uni already exists!"
