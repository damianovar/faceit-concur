# user.py
import re
from mongoengine import Document, StringField, IntField, FloatField, ImageField, ListField, ReferenceField, DateTimeField
from mongoengine.queryset.base import NULLIFY, CASCADE
from mongoengine.queryset.manager import queryset_manager

import datetime


USERS_ROLES = ('Student',
               'Teacher',
               'Admin')
QUESTIONS_TYPES = ('multiple choice',
                   'open',
                   'numeric')
TAXONOMY_TYPES = ('Bloom',
                  'SOLO',
                  'using-explaining')
CUs_RELATIONSHIPS_TYPES = ('necessary foo',
                           'useful for',
                           'part of',
                           'a synonym of',
                           'directly logically related to')
DISCLOSABILITY_TYPES = ('me',
                        'teachers',
                        'my institution',
                        'everybody')


class Country(Document):
    name = StringField(max_length=200, required=True, unique=True)
    institutions = ListField(ReferenceField('Institution'))

    @queryset_manager
    def objects(doc_cls, queryset):
        return queryset.order_by('+name')


class Language(Document):
    name = StringField(max_length=200, required=True, unique=True)

    @queryset_manager
    def objects(doc_cls, queryset):
        return queryset.order_by('+name')


class NotationStandard(Document):
    name = StringField(max_length=200, required=True, unique=True)
    description = StringField(max_length=20000, required=True, unique=True)
    #
    # useful to track things
    current_version = IntField(default=1, required=True)

    @queryset_manager
    def objects(doc_cls, queryset):
        return queryset.order_by('+name')


class Institution(Document):
    name = StringField(max_length=100, required=True)
    country = ReferenceField(
        Country, reverse_delete_rule=NULLIFY, required=True)

    @queryset_manager
    def objects(doc_cls, queryset):
        return queryset.order_by('+name')


class User(Document):
    #
    # note that each email can be used at most by one user
    username = StringField(required=True,  max_length=50, unique=True)
    first_name = StringField(required=True,  max_length=50)
    middle_name = StringField(required=False, max_length=50)
    last_name = StringField(required=True,  max_length=50)
    password = StringField(required=True,  max_length=100)
    email = StringField(required=True,  max_length=50, unique=True)
    #
    # this defines how much 'power' the user has, and thus which types
    # of actions the user can do in the portal
    role = StringField(choices=USERS_ROLES)
    #
    # all these fields are lists because each person may have more
    # than one nationality, etc
    nationalities = ListField(ReferenceField(
        Country, reverse_delete_rule=CASCADE), required=False)
    institutions = ListField(ReferenceField(
        Institution, reverse_delete_rule=CASCADE), required=True)
    preferred_languages = ListField(ReferenceField(
        Language, reverse_delete_rule=CASCADE), required=False)

    #confirmed_at = DateTimeField(required=True)


    @queryset_manager
    def objects(doc_cls, queryset):
        return queryset.order_by('+last_name')

    # to ease the debug - TODO ask Chris where to put these types of methods
    def print(self):
        print("user:        {}".format(self.username))
        print("first name:  {}".format(self.first_name))
        print("middle name: {}".format(self.middle_name))
        print("last name:   {}".format(self.last_name))
        print("role:        {}".format(self.role))


class TaxonomyLevel(Document):
    level = IntField(required=True)
    dimension = StringField(max_length=100, required=True)
    taxonomy_type = StringField(choices=TAXONOMY_TYPES)

    @queryset_manager
    def objects(doc_cls, queryset):
        return queryset.order_by('+level')


# content unit
class CU(Document):
    name = StringField(max_length=150, required=True)
    creator = ReferenceField(User, reverse_delete_rule=CASCADE, required=True)
    timestamp = DateTimeField(default=datetime.datetime.now())
    last_updated = DateTimeField(default=datetime.datetime.now())

    @queryset_manager
    def objects(doc_cls, queryset):
        return queryset.order_by('+name')


# connection between two content units
class CUConnection(Document):
    creator = ReferenceField(User, reverse_delete_rule=CASCADE, required=True)
    # timestamp = DateTimeField(default=datetime.datetime.now())
    # last_updated = DateTimeField(default=datetime.datetime.now())
    #
    course = ReferenceField("Course", required=True)
    # ordered pair of CUs
    cu_matrix = ListField(FloatField(required=True))
    # cu_a = ReferenceField(CU, reverse_delete_rule=CASCADE, required=True)
    # cu_b = ReferenceField(CU, reverse_delete_rule=CASCADE, required=True)
    #
    # potential definition of to which taxonomy levels
    # such a connection refers to
    taxonomy_level_cu_a = ReferenceField(
        TaxonomyLevel, reverse_delete_rule=CASCADE, required=False)
    taxonomy_level_cu_b = ReferenceField(
        TaxonomyLevel, reverse_delete_rule=CASCADE, required=False)
    #
    # relationship within a given fixed set of potential types
    # relationship_type = StringField(
    #     choices=CUs_RELATIONSHIPS_TYPES, required=True)
    #
    # notation:
    # 0 = the information I inserted was a purely random guess;
    # 1 = I am absolutely certain about the inserted values
    user_self_confidence = FloatField(
        min_value=0.0, max_value=1.0, required=False)

    @queryset_manager
    def objects(doc_cls, queryset):
        return queryset.order_by('+timestamp')


class Course(Document):
    name = StringField(max_length=50, required=True)
    #
    # the course code should not include the semester
    course_code = StringField(max_length=20, required=True)
    #
    # different institutions may use different names for the semester
    semester = StringField(max_length=20, required=False)
    institution = ReferenceField(
        Institution, reverse_delete_rule=CASCADE, required=False)
    #
    # different types of users with different powers
    creator = ReferenceField(User, reverse_delete_rule=CASCADE, required=True)
    teachers = ListField(ReferenceField(
        User, reverse_delete_rule=CASCADE), required=False)
    subscribers = ListField(ReferenceField(
        User, reverse_delete_rule=CASCADE), required=False)
    #
    ects_credits = IntField(required=False)
    timestamp = DateTimeField(default=datetime.datetime.now())
    #
    # list of what people should know before starting the course so
    # to be sure of making a successful participation to the course
    prerequisite_cus_list = ListField(ReferenceField(
        CU, reverse_delete_rule=CASCADE), required=True)
    #
    # list of what people should theoretically know after ending
    # the course
    taught_cus_list = ListField(ReferenceField(
        CU, reverse_delete_rule=CASCADE), required=True)

    course_graph = StringField()
    #
    # intended learning flow within the course, as the teacher
    # imagines it. Note that these connections will also contain
    # the taxonomy levels, i.e.,
    # - the ideal levels of how well the students should know things before
    #   starting the course so to have good chances of taking it
    #   successfully
    # - the ideal levels of how well the students should know things after
    #   having taken successfully the course
    cu_connections = ListField(ReferenceField(
        CUConnection, reverse_delete_rule=CASCADE), required=False)

    @queryset_manager
    def objects(doc_cls, queryset):
        return queryset.order_by('+timestamp')


# actual question saved in the database
#
# note that this object must be synchronized with the .tex file
# 'contentsmapping.tex' used to create the questions and upload
# / download them in / from the portal
#
# Current version: 0.13
#
class Question(Document):
    #
    # different types of users with different powers
    creator = ReferenceField(User, reverse_delete_rule=CASCADE, required=True)
    authors = ListField(ReferenceField(
        User, reverse_delete_rule=CASCADE), required=False)
    subscribers = ListField(ReferenceField(
        User, reverse_delete_rule=CASCADE), required=False)
    #
    institutions = ListField(ReferenceField(
        Institution, reverse_delete_rule=CASCADE), required=False)
    courses = ListField(ReferenceField(
        Course, reverse_delete_rule=CASCADE), required=False)
    #
    language = ReferenceField(
        Language, reverse_delete_rule=CASCADE, required=False)
    notation_standard = ReferenceField(
        NotationStandard, reverse_delete_rule=CASCADE, required=False)
    timestamp = DateTimeField(default=datetime.datetime.now())
    #
    # useful to be able to say who  ed to what in a precise way
    # e.g.: John answers to Q12.V1 in 2020, then in 2021 Q12 is
    # modified into V2. The database should keep then track of the
    # fact that John's answer refers to V1, and not V2 (so that
    # one can do learning analytics in a more rigorous way)
    # TODO tell Chris about this feature, and to make some code to update the version in the DB dynamically!
    current_version = IntField(default=1, required=True)
    #
    content_units = ListField(ReferenceField(
        CU, reverse_delete_rule=CASCADE), required=True)
    #
    # important note: the taxonomy levels are associated to the solutions,
    # not the questions!
    #
    question_type = StringField(choices=QUESTIONS_TYPES, required=True)
    body = StringField(required=True)
    body_image = ImageField(required=False)
    #
    # useful only in 'multiple choice' questions:
    # save the list of potential answers each as a separate string
    potential_answers = ListField(StringField(), required=False)
    #
    # useful only in 'multiple choice' questions:
    # save for each potential answer how correct that answer is
    # notation:
    # -1 = the answer is very wrong, and who answered in this
    #      way indicates that she/he did not understand a thing
    #  0 = the answer is wrong, but who answered in this way
    #      may have made only a slip
    #  1 = the answer is correct
    correctness_of_the_answers = ListField(FloatField(
        min_value=-1.0, max_value=1.0), required=False)
    #
    # potential additional information
    notes_for_the_teacher = StringField(required=False)
    notes_for_the_student = StringField(required=False)
    feedback_for_the_student = StringField(required=False)
    #
    # whether the creator prefers this question to be
    # of public domain or not
    question_disclosability = StringField(
        choices=DISCLOSABILITY_TYPES, required=False)
    #
    # whether the creator prefers the various solutions to this question to be
    # of public domain or not. Note that this may be used to enforce
    # a stricter disclosability property than the ones of each of the solutions
    solutions_disclosability = StringField(
        choices=DISCLOSABILITY_TYPES, required=False)

    @queryset_manager
    def objects(doc_cls, queryset):
        return queryset.order_by('+timestamp')

    # to ease the debug
    def print(self):
        #print("question ID: {}".format(self._ID))
        print("creator:        {}".format(self.creator))
        print("current version:        {}".format(self.current_version))
        print("content units:        {}".format(self.content_units))
        print("body:        {}".format(self.body))
        print("type:        {}".format(self.question_type))


class QuestionSolution(Document):
    #
    creator = ReferenceField(User, reverse_delete_rule=CASCADE, required=True)
    authors = ListField(ReferenceField(
        User, reverse_delete_rule=CASCADE), required=False)
    subscribers = ListField(ReferenceField(
        User, reverse_delete_rule=CASCADE), required=False)
    timestamp = DateTimeField(default=datetime.datetime.now())
    language = ReferenceField(
        Language, reverse_delete_rule=CASCADE, required=False)
    notation_standard = StringField(required=False)
    #
    # useful to be able to say who answered to what in a precise way
    # e.g.: John answers to Q12.V1 in 2020, then in 2021 Q12 is
    # modified into V2. The database should keep then track of the
    # fact that John's answer refers to V1, and not V2 (so that
    # one can do learning analytics in a more rigorous way)
    question = ListField(ReferenceField(
        Question, reverse_delete_rule=CASCADE), required=True)
    question_version = IntField(default=1, required=True)
    solution_version = IntField(default=1, required=True)
    #
    body = StringField(required=True)
    body_image = ImageField(required=False)
    #
    content_units = ListField(ReferenceField(
        CU, reverse_delete_rule=CASCADE), required=True)
    #
    # note that the length of the taxonomy levels field
    # may not be equal to the length of the content units field.
    # This captures the taxonomy levels of the solution, not of the CUs!
    taxonomy_levels = ListField(ReferenceField(
        TaxonomyLevel, reverse_delete_rule=CASCADE), required=False)
    #
    # whether the creator prefers this specific solution to be
    # of public domain or not
    disclosability = StringField(choices=DISCLOSABILITY_TYPES, required=False)

    @queryset_manager
    def objects(doc_cls, queryset):
        return queryset.order_by('+timestamp')


# useful to define batches of questions, and then
# let students search for these batches instead of
# single questions
class Test(Document):
    #
    # different types of users with different powers
    creator = ReferenceField(User, reverse_delete_rule=CASCADE, required=True)
    authors = ListField(ReferenceField(
        User, reverse_delete_rule=CASCADE), required=False)
    subscribers = ListField(ReferenceField(
        User, reverse_delete_rule=CASCADE), required=False)
    timestamp = DateTimeField(default=datetime.datetime.now())
    #
    # string useful to ease students' searches in the database
    name = StringField(max_length=200, required=True)
    #
    # potential additional information
    notes_for_the_teacher = StringField(max_length=2000, required=False)
    notes_for_the_student = StringField(max_length=2000, required=False)
    test_disclosability = StringField(
        choices=DISCLOSABILITY_TYPES, required=False)
    #
    # useful to be able to say who answered to what in a precise way
    # e.g.: John answers to Q12.V1 in 2020, then in 2021 Q12 is
    # modified into V2. The database should keep then track of the
    # fact that John's answer refers to V1, and not V2 (so that
    # one can do learning analytics in a more rigorous way)
    current_version = IntField(default=1, required=True)
    #
    institutions = ListField(ReferenceField(
        Institution, reverse_delete_rule=CASCADE), required=False)
    courses = ListField(ReferenceField(
        Course, reverse_delete_rule=CASCADE), required=False)
    #
    # finally, the list of questions
    questions = ListField(ReferenceField(
        Question, reverse_delete_rule=CASCADE), required=False)

    @queryset_manager
    def objects(doc_cls, queryset):
        return queryset.order_by('+timestamp')


class QuestionAnswer(Document):
    #
    user = ReferenceField(
        User, reverse_delete_rule=CASCADE, required=True)
    question = ReferenceField(
        Question, reverse_delete_rule=CASCADE, required=True)
    timestamp = DateTimeField(default=datetime.datetime.now())
    #
    # useful to be able to say who answered to what in a precise way
    # e.g.: John answers to Q12.V1 in 2020, then in 2021 Q12 is
    # modified into V2. The database should keep then track of the
    # fact that John's answer refers to V1, and not V2 (so that
    # one can do learning analytics in a more rigorous way)
    question_version = IntField(default=1, required=True)

    selected_answer = ListField(IntField(), required=True)
    #
    # independently of the question_type, this is going to be a string.
    # More precisely,
    # type = multiple choice => a comma-separated list of options, e.g.
    #                           '2,4,5'. May also be empty, i.e., ''
    # type = open            => a LaTeX string
    # type = numeric         => a number or a LaTeX expression
    # answer = StringField(max_length=20000, required=True)

    perceived_difficulty = IntField(
        min_value=1, max_value=5, required=True)
    #
    # notation:
    # 0 = the answer I inserted was a purely random guess;
    # 1 = I am absolutely certain about the inserted answer
    user_self_confidence = FloatField(
        min_value=0.0, max_value=1.0, required=False)

    @queryset_manager
    def objects(doc_cls, queryset):
        return queryset.order_by('+timestamp')


class QuestionOpinion(Document):
    #
    creator = ReferenceField(
        User,     reverse_delete_rule=CASCADE, required=True)
    question = ReferenceField(
        Question, reverse_delete_rule=CASCADE, required=True)
    timestamp = DateTimeField(default=datetime.datetime.now())
    #
    # useful to be able to say who answered to what in a precise way
    # e.g.: John gives feedback about Q12.V1 in 2020, then in 2021 Q12
    # is modified into V2. The database should keep then track of the
    # fact that John's answer refers to V1, and not V2 (so that
    # one can do learning analytics in a more rigorous way)
    question_version = IntField(default=1, required=True)
    #
    # if somebody wants to update the opinion, this should should
    # be tracked too
    opinion_version = IntField(default=1, required=True)
    #
    # notation:
    # 0 = this question is the worst question I have seen
    # 1 = I think this is an excellent question
    rating_from_the_user = FloatField(
        min_value=0.0, max_value=1.0,   required=False)
    feedback_on_the_question = StringField(max_length=2000, required=False)
    #
    # to track what the user thinks the CUs are
    user_assessed_cus = ListField(ReferenceField(
        CU, reverse_delete_rule=CASCADE), required=False)
    #
    # notation:
    # 0 = the information I inserted was a purely random guess;
    # 1 = I am absolutely certain about the inserted values
    user_self_confidence_on_cus = FloatField(
        min_value=0.0, max_value=1.0, required=False)

    @queryset_manager
    def objects(doc_cls, queryset):
        return queryset.order_by('+timestamp')


class SolutionOpinion(Document):
    #
    creator = ReferenceField(User, reverse_delete_rule=CASCADE, required=True)
    solution = ReferenceField(QuestionSolution,
                              reverse_delete_rule=CASCADE, required=True)
    timestamp = DateTimeField(default=datetime.datetime.now())
    #
    # useful to be able to say to which solution this opinion refers to
    solution_version = IntField(default=1, required=True)
    #
    # if somebody wants to update the opinion, this should should
    # be tracked too
    opinion_version = IntField(default=1, required=True)
    #
    # notation:
    # 0 = this question is the worst question I have seen
    # 1 = I think this is an excellent question
    rating_from_the_user = FloatField(
        min_value=0.0, max_value=1.0, required=False)
    feedback_on_the_solution = StringField(max_length=2000, required=False)
    #
    # to track what the user thinks the CUs and TLs are
    user_assessed_cus = ListField(ReferenceField(
        CU, reverse_delete_rule=CASCADE), required=False)
    user_assessed_taxonomy_levels = ListField(ReferenceField(
        TaxonomyLevel, reverse_delete_rule=CASCADE), required=False)
    #
    # notation:
    # 0 = the information I inserted was a purely random guess;
    # 1 = I am absolutely certain about the inserted values
    user_self_confidence_on_cus = FloatField(
        min_value=0.0, max_value=1.0, required=False)
    user_self_confidence_on_taxonomy_levels = FloatField(
        min_value=0.0, max_value=1.0, required=False)

    @queryset_manager
    def objects(doc_cls, queryset):
        return queryset.order_by('+timestamp')

CUConnection.register_delete_rule(Course, 'course', CASCADE)