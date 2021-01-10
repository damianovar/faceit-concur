"""
models.py
This file contains the tabels for the database in mongoDB used to store user and question data

Classes:
    Country(Document)
    University(Document)
    Course(Document)
    User(Document)
    Register(Document)
    KC(Document)
    Connection(Document)
    Question(Document)
    Test(Document)

Functions:

Misc variables:
    POSITION
    CONFIDENCE
"""

from mongoengine import *
import datetime
import uuid
"""
from database.models.country import Country
from database.models.course import Course
from database.models.university import University
"""

CONFIDENCE = ('VERY LOW', 'LOW', 'MEDIUM', 'HIGH', 'VERY HIGH')
POSITION = ('STUDENT', 'PROFESSOR', 'OTHER')

# Country table column, setup for querying for name and id of the country
class Country(Document):
    name = StringField(max_length=200, required=True, unique=True)
    universities = ListField(ReferenceField('University'))

    @queryset_manager
    def objects(doc_cls, queryset):
        return queryset.order_by('+name')

    @queryset_manager
    def objectss(doc_cls, queryset):
        return queryset.order_by('_id')

# University table column, contains a name and country field
class University(Document):
    name = StringField(max_length=100, required=True)
    country = ReferenceField(
        Country, reverse_delete_rule=NULLIFY, required=True)

    @queryset_manager
    def objects(doc_cls, queryset):
        return queryset.order_by('+country')

# Course table column, includes name, course code and semester
class Course(Document):
    name = StringField(required=True, max_length=50)
    code = StringField(required=True, max_length=10)
    kcs = ListField(ReferenceField('KC'))
    semester = StringField(max_length=5)

    @queryset_manager
    def objects(doc_cls, queryset):
        return queryset.order_by('+code')

# User table column, contains the name, nationality, position, university and courses taken.
class User(Document):
    #userid = UUIDField(primary_key=True)
    first_name = StringField(required=True, max_length=50)
    middle_name = StringField(required=False, max_length=50)
    last_name = StringField(required=True, max_length=50,
                            unique_with='first_name')
    nationality = ReferenceField(
        Country, reverse_delete_rule=CASCADE, required=True)
    position = StringField(choices=POSITION)
    university = ReferenceField(University, reverse_delete_rule=CASCADE)
    courses = ListField(ReferenceField(
        Course, reverse_delete_rule=CASCADE), required=False)

    @queryset_manager
    def objects(doc_cls, queryset):
        return queryset.order_by('+last_name')

# Registration table column, contains the username, email and password
class Register(Document):
    #userid = UUIDField(primary_key=True)
    username = StringField(required=True, max_length=50)
    email = StringField(required=True, max_length=50)
    password = StringField(required=True, max_length=100)

    @queryset_manager
    def objects(doc_cls, queryset):
        return queryset.order_by('+email')

# KC table column, contains the name, courses, when created and last updated.
class KC(Document):
    name = StringField(max_length=150, required=True)
    courses = ListField(ReferenceField('Course', reverse_delete_rule=CASCADE))
    created = DateTimeField(default=datetime.datetime.now())
    last_updated = DateTimeField(default=datetime.datetime.now())

    @queryset_manager
    def objects(doc_cls, queryset):
        return queryset.order_by('+name')

# Connection table column, contains the user, course, semester, percentage completed and last updated 
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

# Question table column, contains necessary metadata of a question and the author
class Question(Document):
    question_number = IntField(required=False)
    kc_list = ListField(ReferenceField(KC, reverse_delete_rule=CASCADE), required=True)
    question = StringField(required=True)
    #options = ListField(required=True)
    #correct_answer = StringField(required=True)
    #solution = StringField(required=True)
    author = ReferenceField(User, reverse_delete_rule=CASCADE, required=True)
    course = ReferenceField(Course, reverse_delete_rule=CASCADE, required=False)

    kc_list = ListField(ReferenceField(KC, reverse_delete_rule=CASCADE), required=True)
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


    test = ReferenceField(('Test'), required=False)

    @queryset_manager
    def objects(doc_cls, queryset):
        return queryset.order_by('+kc_list')






class Test(Document):
    name = StringField(required=True)
    course = ReferenceField(
        Course, reverse_delete_rule=CASCADE, required=False)
    questions = ListField(ReferenceField(
        Question, reverse_delete_rule=CASCADE, required=False))

    @queryset_manager
    def objects(doc_cls, queryset):
        return queryset.order_by('+course')
