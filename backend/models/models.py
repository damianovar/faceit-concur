# user.py
from mongoengine import *
import datetime


USERS_ROLES             = ( 'Student',
                            'Teacher',
                            'Admin' )
#
QUESTIONS_TYPES         = ( 'multiple choice',
                            'open',
                            'numeric' )
#
TAXONOMY_TYPES          = ( 'Bloom',
                            'SOLO',
                            'E+' )
#
CUs_RELATIONSHIPS_TYPES = ( 'is necessary for',
                            'is useful for',
                            'is part of',
                            'is a synonym of',
                            'is directly logically related to' )
#
DISCLOSABILITY_TYPES    = ( 'only me',
                            'only teachers',
                            'only my institution',
                            'everybody' )


class Country(Document):
    name = StringField(max_length=200, required=True, unique=True)

    @queryset_manager
    def objects(doc_cls, queryset):
        return queryset.order_by('+name')



class Language(Document):
    name = StringField(max_length=200, required=True, unique=True)

    @queryset_manager
    def objects(doc_cls, queryset):
        return queryset.order_by('+name')



class Institution(Document):
    name    = StringField(max_length=100, required=True)
    country = ReferenceField(Country, reverse_delete_rule=NULLIFY, required=True)

    @queryset_manager
    def objects(doc_cls, queryset):
        return queryset.order_by('+name')



class User(Document):
    #
    # note that each email can be used at most by one user
    username            = StringField(required=True,  max_length=50, unique=True)
    first_name          = StringField(required=True,  max_length=50)
    middle_name         = StringField(required=False, max_length=50)
    last_name           = StringField(required=True,  max_length=50)
    password            = StringField(required=True,  max_length=100)                   
    email               = StringField(required=True,  max_length=50, unique=True)
    #
    # this defines how much 'power' the user has, and thus which types
    # of actions the user can do in the portal
    role                = StringField(choices=USERS_ROLES)
    #
    # all these fields are lists because each person may have more
    # than one nationality, etc
    nationalities       = ListField(ReferenceField(Country,     reverse_delete_rule=CASCADE), required=False)
    institutions        = ListField(ReferenceField(Institution, reverse_delete_rule=CASCADE), required=True )
    preferred_languages = ListField(ReferenceField(Language,    reverse_delete_rule=CASCADE), required=False)

    @queryset_manager
    def objects(doc_cls, queryset):
        return queryset.order_by('+last_name')

    # to ease the debug
    def print(self):
        print("user:        {}".format(self.username))
        print("first name:  {}".format(self.first_name))
        print("middle name: {}".format(self.middle_name))
        print("last name:   {}".format(self.last_name))
        print("role:        {}".format(self.role))



class Taxonomy_level(Document):
    level         = IntField    (required=True)
    dimension     = StringField (max_length=100, required=True)
    taxonomy_type = StringField (choices=TAXONOMY_TYPES)

    @queryset_manager
    def objects(doc_cls, queryset):
        return queryset.order_by('+level')



# content unit
class CU(Document):
    name         = StringField    (max_length=150,                    required=True)
    creator      = ReferenceField (User, reverse_delete_rule=CASCADE, required=True)
    timestamp    = DateTimeField  (default=datetime.datetime.now())
    last_updated = DateTimeField  (default=datetime.datetime.now())

    @queryset_manager
    def objects(doc_cls, queryset):
        return queryset.order_by('+name')



# connection between two content units 
class CUs_connection(Document):
    creator              = ReferenceField(User, reverse_delete_rule=CASCADE, required=True)
    timestamp            = DateTimeField(default=datetime.datetime.now())
    last_updated         = DateTimeField(default=datetime.datetime.now())
    #
    # ordered pair of CUs
    CU_A                 = ListField(ReferenceField(CU, reverse_delete_rule=CASCADE),  required=True)
    CU_B                 = ListField(ReferenceField(CU, reverse_delete_rule=CASCADE),  required=True)
    #
    # potential definition of to which taxonomy levels
    # such a connection refers to
    taxonomy_level_CU_A  = ReferenceField(Taxonomy_level, reverse_delete_rule=CASCADE, required=False)
    taxonomy_level_CU_B  = ReferenceField(Taxonomy_level, reverse_delete_rule=CASCADE, required=False)
    #
    # relationship within a given fixed set of potential types
    relationship_type    = StringField(choices=CUs_RELATIONSHIPS_TYPES, required=True)
    #
    # notation:
    # 0 = the information I inserted was a purely random guess;
    # 1 = I am absolutely certain about the inserted values
    user_self_confidence = FloatField(min_value=0.0, max_value=1.0, required=False)

    @queryset_manager
    def objects(doc_cls, queryset):
        return queryset.order_by('+timestamp')



class Course(Document):
    name                  = StringField   (max_length=50, required=True)
    #
    # the course code should not include the semester
    course_code           = StringField   (required=True, max_length=20)
    #
    # different institutions may use different names for the semester
    semester              = StringField   (max_length=20)
    institution           = ReferenceField(Institution, reverse_delete_rule=CASCADE, required=False)
    #
    # different types of users with different powers
    creator               = ReferenceField(User, reverse_delete_rule=CASCADE, required=True)
    teachers              = ListField     (ReferenceField(User, reverse_delete_rule=CASCADE), required=False)
    subscribers           = ListField     (ReferenceField(User, reverse_delete_rule=CASCADE), required=False)
    #
    ECTS_credits          = IntField      (required=False)
    timestamp             = DateTimeField (default=datetime.datetime.now())
    #
    # list of what people should know before starting the course so
    # to be sure of making a successful participation to the course 
    prerequisite_CUs_list = ListField(ReferenceField(CU),             required=True)
    #
    # list of what people should theoretically know after ending
    # the course
    taught_CUs_list       = ListField(ReferenceField(CU),             required=True)
    #
    # intended learning flow within the course, as the teacher
    # imagines it
    CUs_connections       = ListField(ReferenceField(CUs_connection), required=False)
    #
    # ideal levels of how well the students should know things before
    # starting the course so to have good chances of taking it
    # successfully
    prerequisite_CUs_nominal_taxonomy_levels = ListField(ReferenceField(Taxonomy_level), required=False)
    #
    # ideal levels of how well the students should know things after
    # having taken successfully the course
    taught_CUs_nominal_taxonomy_levels       = ListField(ReferenceField(Taxonomy_level), required=False)

    @queryset_manager
    def objects(doc_cls, queryset):
        return queryset.order_by('+timestamp')



# actual question saved in the database
#
# note that this object must be synchronized with the .tex file
# 'contentsmapping.tex' used to create the questions and upload
# / download them in / from the portal
#
# Current version: 0.12
#
class Question(Document):
    #
    # different types of users with different powers
    creator                  = ReferenceField (User, reverse_delete_rule=CASCADE, required=True)
    authors                  = ListField      (ReferenceField(User,   reverse_delete_rule=CASCADE), required=False)
    subscribers              = ListField      (ReferenceField(User,   reverse_delete_rule=CASCADE), required=False)
    #
    institutions             = ListField      (ReferenceField(Institution, reverse_delete_rule=CASCADE), required=False)
    courses                  = ListField      (ReferenceField(Course, reverse_delete_rule=CASCADE), required=False)
    #
    language                 = ReferenceField (Language, reverse_delete_rule=CASCADE, required=False)
    notation_standard        = StringField    (required=False)
    timestamp                = DateTimeField  (default=datetime.datetime.now())
    last_updated             = DateTimeField  (default=datetime.datetime.now())
    #
    # useful to be able to say who answered to what in a precise way 
    # e.g.: John answers to Q12.V1 in 2020, then in 2021 Q12 is
    # modified into V2. The database should keep then track of the
    # fact that John's answer refers to V1, and not V2 (so that
    # one can do learning analytics in a more rigorous way)
    current_version            = IntField       (default=1, required=True)
    #
    content_units              = ListField      (ReferenceField(CU, reverse_delete_rule=CASCADE), required=True)
    taxonomy_levels            = ListField      (ReferenceField(Taxonomy_level, reverse_delete_rule=CASCADE), required=False)
    #
    question_type              = StringField    (choices=QUESTIONS_TYPES, required=True)
    body                       = StringField    (required=True)
    body_image                 = ImageField     (required=False)
    #
    # useful only in 'multiple choice' questions:
    # save the list of potential answers each as a separate string
    potential_answers          = ListField      (StringField, required=False)
    #
    # useful only in 'multiple choice' questions:
    # save for each potential answer how correct that answer is
    # notation:
    # -1 = the answer is very wrong, and who answered in this
    #      way indicates that she/he did not understand a thing
    #  0 = the answer is wrong, but who answered in this way
    #      may have made only a slip
    #  1 = the answer is correct
    correctness_of_the_answers = ListField      (FloatField(min_value=-1.0, max_value=1.0), required=False)
    #
    # may also be an URL
    solutions                  = StringField    (required=False)
    solutions_image            = ImageField     (required=False)
    #
    # potential additional information 
    notes_for_the_teacher      = StringField    (required=False)
    notes_for_the_student      = StringField    (required=False)
    feedback_for_the_student   = StringField    (required=False)
    #
    question_disclosability    = StringField    (choices=DISCLOSABILITY_TYPES, required=False)
    solution_disclosability    = StringField    (choices=DISCLOSABILITY_TYPES, required=False)

    @queryset_manager
    def objects(doc_cls, queryset):
        return queryset.order_by('+timestamp')

    # to ease the debug
    def print(self):
        print("question ID: {}".format(self._ID))
        print("body:        {}".format(self.body))
        print("type:        {}".format(self.type))



# useful to define batches of questions, and then
# let students search for these batches instead of
# single questions
class Test(Document):
    #
    # different types of users with different powers
    creator         = ReferenceField (User, reverse_delete_rule=CASCADE, required=True)
    authors         = ListField      (ReferenceField(User,   reverse_delete_rule=CASCADE), required=False)
    subscribers     = ListField      (ReferenceField(User,   reverse_delete_rule=CASCADE), required=False)
    #
    # string useful to ease students' searches in the database
    name            = StringField(required=True)
    #
    # potential additional information 
    notes_for_the_teacher = StringField    (required=False)
    notes_for_the_student = StringField    (required=False)
    test_disclosability   = StringField    (choices=DISCLOSABILITY_TYPES, required=False)
    #
    timestamp       = DateTimeField (default=datetime.datetime.now())
    last_updated    = DateTimeField (default=datetime.datetime.now())
    #
    # useful to be able to say who answered to what in a precise way 
    # e.g.: John answers to Q12.V1 in 2020, then in 2021 Q12 is
    # modified into V2. The database should keep then track of the
    # fact that John's answer refers to V1, and not V2 (so that
    # one can do learning analytics in a more rigorous way)
    current_version = IntField      (default=1, required=True)
    #
    institutions    = ListField(ReferenceField(Institution, reverse_delete_rule=CASCADE), required=False)
    courses         = ListField(ReferenceField(Course,      reverse_delete_rule=CASCADE), required=False)
    #
    # finally, the list of questions
    questions       = ListField(ReferenceField(Question, reverse_delete_rule=CASCADE, required=False))

    @queryset_manager
    def objects(doc_cls, queryset):
        return queryset.order_by('+timestamp')



class Answer_to_question(Document):
    #
    creator              = ReferenceField (User,     reverse_delete_rule=CASCADE, required=True)
    question             = ReferenceField (Question, reverse_delete_rule=CASCADE, required=True)
    timestamp            = DateTimeField  (default=datetime.datetime.now())
    #
    # useful to be able to say who answered to what in a precise way 
    # e.g.: John answers to Q12.V1 in 2020, then in 2021 Q12 is
    # modified into V2. The database should keep then track of the
    # fact that John's answer refers to V1, and not V2 (so that
    # one can do learning analytics in a more rigorous way)
    question_version     = IntField       (default=1, required=True)
    #
    # independently of the question_type, this is going to be a string.
    # More precisely,
    # type = multiple choice => a comma-separated list of options, e.g.
    #                           '2,4,5'. May also be empty, i.e., ''
    # type = open            => a LaTeX string 
    # type = numeric         => a number or a LaTeX expression
    answer               = StringField    (required=True)
    #
    # notation:
    # 0 = the information I inserted was a purely random guess;
    # 1 = I am absolutely certain about the inserted values
    user_self_confidence = FloatField     (min_value=0.0, max_value=1.0, required=False)

    @queryset_manager
    def objects(doc_cls, queryset):
        return queryset.order_by('+timestamp')



class Opinion_on_question(Document):
    #
    creator              = ReferenceField (User,     reverse_delete_rule=CASCADE, required=True)
    question             = ReferenceField (Question, reverse_delete_rule=CASCADE, required=True)
    timestamp            = DateTimeField  (default=datetime.datetime.now())
    #
    # useful to be able to say who answered to what in a precise way 
    # e.g.: John gives feedback about Q12.V1 in 2020, then in 2021 Q12
    # is modified into V2. The database should keep then track of the
    # fact that John's answer refers to V1, and not V2 (so that
    # one can do learning analytics in a more rigorous way)
    question_version     = IntField       (default=1, required=True)
    #
    user_assessed_CUs             = ListField   (ReferenceField(CU),             reverse_delete_rule=CASCADE, required=False)
    user_assessed_taxonomy_levels = ListField   (ReferenceField(Taxonomy_level), reverse_delete_rule=CASCADE, required=False)
    feedback_from_the_user        = StringField (required=False)
    #
    # notation:
    # 0 = this question is the worst question I have seen
    # 1 = I think this is an excellent question
    rating_from_the_user          = FloatField  (min_value=0.0, max_value=1.0,   required=False)
    #
    # notation:
    # 0 = the information I inserted was a purely random guess;
    # 1 = I am absolutely certain about the inserted values
    user_self_confidence_on_CUs             = FloatField (min_value=0.0, max_value=1.0, required=False)
    user_self_confidence_on_taxonomy_levels = FloatField (min_value=0.0, max_value=1.0, required=False)

    @queryset_manager
    def objects(doc_cls, queryset):
        return queryset.order_by('+timestamp')


