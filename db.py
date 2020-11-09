from mongoengine import connect
from backend.src.database.models.models import KC, Course, Question

connect(db="KCMap",
        username="developer",
        password="TTK4260",
        host="mongodb+srv://developer:TTK4260@kcbank.lwcpe.mongodb.net/KCMap?retryWrites=true&w=majority")

def list_question_objects() -> Question:
        object_list = []
        for elements in Question.objects():
                question = elements.question
                course = elements.course
                course_name = ''
                if course is not None:
                        course_name = Course.objects.get(id=course.id).name
                else:
                        course_name ='empty'
                kcs = elements.kc_list
                kc_name = []
                for kc in kcs:
                        kc_name.append(KC.objects.get(id=kc.id).name)
                taxonomy_level = elements.kc_taxonomy
                list_item = []
                list_item = [question,course_name,kc_name,taxonomy_level]
                object_list.append(list_item) 
        return object_list
