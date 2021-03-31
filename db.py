from mongoengine import connect
from flask import session
from bson.objectid import ObjectId
import time
from backend.models.models import KC, Course, Question, Answer, Register, University, Country, User


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
        Given a question object and an answer to the question updates the Answer collection with the provided answer.
        If the question has already been answered by the same user, the answer is overridden, otherwise new answer object is crated.
    """
    my_string = session["user"]

    username_str_start = my_string.find('username') + 9
    username_str_end = my_string.find('email') - 4
    email_str_start = my_string.find('email') + 9
    email_str_end = my_string.find('password') - 4

    user_name = session["user"][username_str_start:username_str_end]
    user_email = session["user"][email_str_start:email_str_end]
    user = Register.objects(email=user_email).first()

    # If difficulty is not rated, set the rating to -1
    if perceived_difficulty == None:
        perceived_difficulty = -1

    Answer.objects(question = question, user=user).update_one(user_name=user_name, answer=txt_answer, selected_option=selected_option, perceived_difficulty=perceived_difficulty, upsert=True)

def get_user_role():
    my_string = session["user"]

    username_str_start = my_string.find('username') + 9
    username_str_end = my_string.find('email') - 4
    email_str_start = my_string.find('email') + 9
    email_str_end = my_string.find('password') - 4

    user_name = session["user"][username_str_start:username_str_end]
    user_email = session["user"][email_str_start:email_str_end]
    user = User.objects(email=user_email).first()

    return user.role

def upload_image_to_question(question_id):
    question_id = "5f72f0e58373664b8505ea6b"
    question_obj = Question.objects(id = str(question_id)).first()
    with open('3x3_matrix.png', 'rb') as fd:
        question_obj.image.put(fd, content_type = 'image/png')
    question_obj.save()
    print("UPLOADED")
    return

def get_question_image(question_id):
    import sys
    from PIL import Image
    from io import BytesIO
    import base64

    question_obj = Question.objects(id = str(question_id)).first()
    #IMAGE = base64.b64encode(question_obj.image.read())
    IMAGE = base64.b64encode(question_obj.image.read()).decode("utf-8")
    #stream = BytesIO(IMAGE)
    #image = Image.open(stream).convert("RGBA")
    #stream.close()
    #print(marmot.image.content_type)

    return IMAGE

def get_question_by_obj_id(question_id):
    """
        Retrieves question object from Question collection given question-object id
    """
    question_obj = Question.objects(id = str(question_id))
    return question_obj.get()

def add_uni():
    if not University.objects(name="Otto-von-Guericke-Universität"):
        c = Country.objects(name="Germany").first()
        return University(name="Otto-von-Guericke-Universität", country=c).save()
    return "Uni already exists!"


#def list_question_objects_old_v2() -> Question:
#    """
#        Doesn't work correctly, the index "id" to "question" is off by 1 for some reason
#    """
#    selection_list = Question.objects.all().values_list('id')
#    question_list = Question.objects.all().values_list('question')
#    taxonomy_level_list = Question.objects.all().values_list('kc_taxonomy')
#    kc_list_obj_list = Question.objects.all().values_list('kc_list')
#    course_obj_list = Question.objects.all().values_list('course')
#    kc_list_name_list = [[y.name for y in x] for x in kc_list_obj_list]
#    course_name_list = [x.name if x is not None else 'empty' for x in course_obj_list]
#    
#    object_list = zip(question_list, course_name_list, kc_list_name_list, taxonomy_level_list)
#    return object_list, selection_list
