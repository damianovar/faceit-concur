# user.py
from mongoengine import *
import datetime

CONFIDENCE = ('VERY LOW', 'LOW', 'MEDIUM', 'HIGH', 'VERY HIGH')
POSITION = ('Student', 'Teacher', 'Admin')


class Country(Document):
    name = StringField(max_length=200, required=True, unique=True)
    universities = ListField(ReferenceField('University'))

    @queryset_manager
    def objects(doc_cls, queryset):
        return queryset.order_by('+name')



class University(Document):
    name = StringField(max_length=100, required=True)
    country = ReferenceField(
        Country, reverse_delete_rule=NULLIFY, required=True)

    @queryset_manager
    def objects(doc_cls, queryset):
        return queryset.order_by('+name')


class Course(Document):
    name = StringField(required=True, max_length=50)
    code = StringField(required=True, max_length=10)
    kcs = ListField(ReferenceField('KC'))
    semester = StringField(max_length=5)

    @queryset_manager
    def objects(doc_cls, queryset):
        return queryset.order_by('+code')


class User(Document):
    first_name = StringField(required=True, max_length=50)
    middle_name = StringField(required=False, max_length=50)
    last_name = StringField(required=True, max_length=50)
    username = StringField(required=True, max_length=50, unique=True)
    email = StringField(required=True, max_length=50, unique=True)
    password = StringField(required=True, max_length=100)                   
    nationality = ReferenceField(
        Country, reverse_delete_rule=CASCADE, required=False)
    role = StringField(choices=POSITION)
    university = ReferenceField(University, reverse_delete_rule=CASCADE, required=True)
    courses = ListField(ReferenceField(
        Course, reverse_delete_rule=CASCADE), required=False)

    @queryset_manager
    def objects(doc_cls, queryset):
        return queryset.order_by('+last_name')

class Register(Document):
    username = StringField(required=True, max_length=50)
    email = StringField(required=True, max_length=50)
    password = StringField(required=True, max_length=100)

    @queryset_manager
    def objects(doc_cls, queryset):
        return queryset.order_by('+email')

class KC(Document):
    name = StringField(max_length=150, required=True)
    courses = ListField(ReferenceField('Course', reverse_delete_rule=CASCADE))
    created = DateTimeField(default=datetime.datetime.now())
    last_updated = DateTimeField(default=datetime.datetime.now())

    @queryset_manager
    def objects(doc_cls, queryset):
        return queryset.order_by('+name')


class Connection(Document):
    user = ReferenceField(User, reverse_delete_rule=CASCADE, required=True)
    course = ReferenceField(Course, reverse_delete_rule=CASCADE, required=True)
    # Optional which semester you want to look at
    semester = StringField(max_length=10)
    kc_list = ListField(ReferenceField(
        KC, reverse_delete_rule=CASCADE), required=True)
    kc_matrix = ListField(ListField(FloatField(required=True)))
    percentage = FloatField(min_value=0.0, max_value=1.0)
    last_updated = DateTimeField(default=datetime.datetime.now())

    @queryset_manager
    def objects(doc_cls, queryset):
        return queryset.order_by('+course')


class Question(Document):
    question_number = IntField(required=False)
    kc_list = ListField(ReferenceField(KC, reverse_delete_rule=CASCADE), required=True)
    question = StringField(required=True)
    #options = ListField(required=True)
    #correct_answer = StringField(required=True)
    #solution = StringField(required=True)
    author = ReferenceField(User, reverse_delete_rule=CASCADE, required=False)
    course = ReferenceField(Course, reverse_delete_rule=CASCADE, required=False)
    course_name = StringField(required=False)

    kc_list = ListField(ReferenceField(KC, reverse_delete_rule=CASCADE), required=True)
    kc_names_list = ListField(StringField(required=False))
    kc_taxonomy = ListField(required=False)
    correct_answer = ListField(required=True)
    options = ListField(required=True)

    author_email = StringField(required=False)
    QuestionType = StringField(required=False)
    notes_teacher = StringField(required=False)
    notes_student = StringField(required=False)
    feedback_student = StringField(required=False)
    question_disclosability = StringField(required=False)
    solution_disclosability = StringField(required=False)
    image = ImageField(required=False)

    test = ReferenceField(('Test'), required=False)

    @queryset_manager
    def objects(doc_cls, queryset):
        return queryset.order_by('+kc_list')


class Answer(Document):
    question = ReferenceField(Question, reverse_delete_rule=CASCADE, required=True)
    user = ReferenceField(User, reverse_delete_rule=CASCADE, required=True)
    user_name = StringField(unique=False, required=True)
    selected_option = StringField(unique=False, required=True)
    answer = StringField(unique=False, required=True)
    perceived_difficulty = IntField(unique=False, required=True)

    @queryset_manager
    def objects(doc_cls, queryset):
        return queryset.order_by('+author_name')


class Test(Document):
    name = StringField(required=True)
    course = ReferenceField(
        Course, reverse_delete_rule=CASCADE, required=False)
    questions = ListField(ReferenceField(
        Question, reverse_delete_rule=CASCADE, required=False))

    @queryset_manager
    def objects(doc_cls, queryset):
        return queryset.order_by('+course')
