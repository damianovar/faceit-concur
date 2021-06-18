from flask import session
from os import name
import pandas as pd
import re
import zipfile
from TexSoup import TexSoup  # , TokenWithPosition

from backend.models.models import Course, Language, Question, CU, User, NotationStandard


# ---------------- HELPER METHODS ------------------

__alphabet__ = "abcdefghij"


# class to extract the questions from the zip files uploaded
# in the portal and to save them in the database
class Upload:

    def register_question(file_path):

        # convert the file in questions
        questions = zip_of_tex_files_to_questions(file_path)

        # for each of them, save it
        for q in questions:
            q.save()


def zip_of_tex_files_to_questions(zipf):
    """
    Parse a latex-file and a pandas dataframe table
    @:param: file (.tex), latex file with questions
    @:return: a list of Question objects
    """

    # storage allocation
    questions = []
    # get the various files within the zip file uploaded in the portal
    zip_file = zipfile.ZipFile(zipf)
    file_list = zip_file.namelist()

    # check each of such files independently
    for current_file in file_list:

        # check things only if you have a .tex file
        if current_file[-4:] == '.tex' and current_file != 'contentsmapping.tex':

            # read the file
            zfile = zip_file.open(current_file)
            data = zfile.read().decode('UTF-8')
            # create an ad-hoc object to search, navigate, and modify the LaTeX document.
            # Here each frame is an environment \begin{smt} ... \end{smt}
            tex = TexSoup(data)
            #frames = list(tex.children)

            frames = tex.find_all("IndexedQuestion")
            # check every "\begin{smt} ... \end{smt}" in the .tex
            # file under investigation
            for frame in frames:

                # check things only if it is an "IndexedQuestion"
                if frame.name == 'IndexedQuestion':

                    # get the .tex string
                    tex_frame_contents = list(frame.children)
                    # convert the .tex string into the object for the database
                     
                    q = tex_string_to_question(
                        tex_frame_contents, file_list, zip_file)
                    # add it to the list
                    if not question_already_in_db(q):
                        questions.append(q)
                    # debug
                    print("added question {}".format(len(questions)))
                    q.print()

                # debug
                print("finished processing frame {}".format(frame.name))

            # end if the file is a .tex file

        # debug
        print("finished processing file {}".format(current_file))

    return questions


# method to convert the text within a
# \begin{IndexedQuestion} ... \end{IndexedQuestion}
# frame into a "Question" object
#
def question_already_in_db(q):
    if not Question.objects(body=q.body):
        print("question does not exists in db")
        return False
    print("question already in db, skipping it..")
    return True

def tex_string_to_question(tex_frame_contents, file_list, zip_file):
    # Current version: 0.12

    # allocate the object before getting the various fields
    q = Question()

    q.creator = get_user()

    q.content_units = get_content_units(tex_frame_contents, q.creator)
    # taxonomy_levels            = str(get_field("QuestionTaxonomyLevels", tex_frame_contents))[1:-1]
    # q.taxonomy_levels          = taxonomy_levels.replace(' ,', ',').replace(', ', ',').replace(' ', '').split(",")

    q.body = get_question_body(tex_frame_contents)

    q.courses = get_question_courses(tex_frame_contents)

    q.body_image = get_image(
        tex_frame_contents, file_list, zip_file, "QuestionBodyImage")

    q.question_type = str(get_field("QuestionType", tex_frame_contents))[1:-1]
    if q.question_type == "multiple choice":
        potential_answers, correct_answers, correctness_of_the_answers = \
            get_answers_for_multiple_choice_questions(
                tex_frame_contents, q.question_type)

        q.potential_answers = potential_answers
        q.correctness_of_the_answers = correctness_of_the_answers

        q.correct_answers = correct_answers

    q.solutions = str(get_field("QuestionSolutions", tex_frame_contents))[1:-1]

    q.solutions_image = get_image(
        tex_frame_contents, file_list, zip_file, "QuestionSolutionsImage")

    #q.authors = state.user

    q.notes_for_the_teacher = str(
        get_field("QuestionNotesForTheTeachers", tex_frame_contents))[1:-1]

    q.notes_for_the_student = str(
        get_field("QuestionNotesForTheStudents", tex_frame_contents))[1:-1]

    q.feedback_for_the_student = str(
        get_field("QuestionFeedbackForTheStudents", tex_frame_contents))[1:-1]

    q.question_disclosability = str(
        get_field("QuestionDisclosability", tex_frame_contents))[1:-1]

    if q.question_disclosability == 'me':
        print('ok')
    else:
        q.question_disclosability = 'me'
    print(q.question_disclosability)

    q.solution_disclosability = str(
        get_field("QuestionSolutionDisclosability", tex_frame_contents))[1:-1]

    language = str(get_field("QuestionLanguage", tex_frame_contents))[1:-1]
    q.language = get_language(language)

    notation_standard = str(
        get_field("QuestionNotationStandard", tex_frame_contents))[1:-1]
    q.notation_standard = get_notation_standard(notation_standard)

    # sanity check
    assert is_question_type_well_defined(q.question_type), \
        "WARNING -- question {} has a ill-defined question type. \
           Check the .tex template!".format(q.question_counter)

    # return the object
    return q


def get_user():
    try:
        user = session.get("user").get("username")
        return User.objects(username=user).first()
    except Exception as e:
        print("User not found - a valid user is required to upload questions") 
        return None

def get_question_courses(tex_frame_contents):
    courses = str(
        get_field("QuestionCourses", tex_frame_contents))[1:-1]
    courses = courses.replace(
        ' ,', ',').replace(', ', ',').split(",")
    course_list = []
    for course in courses:
        print(Course.objects())
        if Course.objects(name=course).first() is not None:
            course_list.append(Course.objects(name=course).first())
            print("Course found: " + str(course))
        else:
            print("Course not found - creating a new Course")
            continue
    return course_list


def get_content_units(tex_frame_contents, creator):
    content_units = str(
        get_field("QuestionContentUnits", tex_frame_contents))[1:-1]
    content_units = content_units.replace(
        ' ,', ',').replace(', ', ',').split(",")
    cu = []
    for content_unit in content_units:
        if CU.objects(name=content_unit).first() is not None:
            cu.append(CU.objects(name=content_unit).first())
            print("CU found: " + str(content_unit))
        else:
            print("CU not found - creating a new CU")
            cu.append(CU(name=content_unit, creator=creator).save())
    return cu

def get_language(language):
    try:
        return Language.objects(name=language).first()
    except Exception as e:
        return None


def get_notation_standard(notation):
    try:
        return NotationStandard.objects(name=notation).first()
    except Exception as e:
        return None


def get_field(token_name, tex_frame_contents):
    """
    Check whether a specific token_name is in the
    tex_frame_contents string. If so returns the contents
    in tex_frame_contents that refer to that token
    """
    for token in tex_frame_contents:
        if token.name == token_name:
            return [token.args[-1] for token in tex_frame_contents if token.name == token_name][0]
    return {None}


def get_question_body(tex_frame_contents):
    """
    Ugly function to format the question body
    :param tex_frame_contents:
    :return: question_body in string format
    """
    q = [str(token) for token in tex_frame_contents if token.name == "QuestionBody"][0] \
        .replace("\\QuestionBody{", "")[:-1]
    q = re.sub("[\n\t]", "", q)
    q = re.sub('\s{2,}', ' ', q)
    q = q.replace('$$', "$")
    q = q.replace(r"\bm", "")
    q = q.replace("\qquad", "")
    q = q.replace(" $", "$")  # remove spacing to avoid problems with math

    # remove LaTex commands that are not identified by qti
    q = q.replace("\Reals", "")

    # remove other things
    q = q.replace("\\begin{small}", "")
    q = q.replace("\\end{small}", "")
    q = q.replace("\\begin{footnotesize}", "")
    q = q.replace("\\end{footnotesize}", "")

    return q


def get_image(tex_frame_contents, file_list, zip_file, field_name):
    """
    Parameters
    ----------
    tex_frame_contents : str
        the string within the
        \begin{IndexedQuestion} ... \end{IndexedQuestion}
        environment
    file_list : str
        list of the files included in the .zip file uploaded
        in the portal
    field_name : str
        either "QuestionBodyImage" or "QuestionSolutionsImage"
    """

    # initialization
    image = None

    # get the name of the image
    image_string = str(get_field(field_name, tex_frame_contents))[1:-1]
    if image_string != 'None':
        #image_string = re.findall(r'{(?:[^{}])*}', image_string)
        for fil in file_list:
            if fil == image_string:
                image = zip_file.open(fil)

    return image


def get_answers_for_multiple_choice_questions(tex_frame_contents, question_type):

    # if the question is not of the right type then return immediately
    if question_type != "multiple choice":
        potential_answers = correct_answers = None
        return potential_answers, correct_answers

    # answers = str(get_field("QuestionAnswers", tex_frame_contents))[1:-1]
    answers_i = 3  # Usually where the framecontents is
    # in case first field is \vspace or another setting instead
    if "\QuestionPotentialAnswers" not in str(tex_frame_contents[answers_i]):
        for i, field in enumerate(tex_frame_contents):
            if "\QuestionPotentialAnswers" in str(field):
                answers_i = i
                break
    answers = format_answers(
        [token for token in tex_frame_contents[answers_i]])

    potential_answers = []
    correctness_of_the_answers = []
    correct_answers = []
    for i, entry in enumerate(answers):

        if '\\answer' in entry:
            potential_answers.append(answers[i + 1])
            correctness_of_the_answers.append(0.0)

        elif '\\correctanswer' in entry:
            potential_answers.append(answers[i + 1])
            correct_answers.append(answers[i + 1])
            correctness_of_the_answers.append(1.0)

    # separator = " , "
    # #potential_answers = separator.join(potential_answers)
    # correct_answers = separator.join(correct_answers)

    return potential_answers, correct_answers, correctness_of_the_answers


def is_question_type_well_defined(question_type):
    if question_type in ["multiple choice", "open", "numeric"]:

        # debug
        print('well-defined question type: {}'.format(question_type))

        return True

    else:

        # debug
        print('!!! ILL-DEFINED QUESTION TYPE: {}'.format(question_type))

        return True


def format_answers(answers):
    """
    Modifies the list of TexNodes and TokenWithPosition
    into a pure string list
    :param answers: list of possible answers
    :return: new list with answers
    """
    # Make every element a string
    for i, elem in enumerate(answers):
        if "\n\t\t" in str(elem):
            answers[i] = str(elem).replace("\n\t\t", "")
        elif "\n\t" in str(elem):
            answers[i] = str(elem).replace("\n\t", "")
        else:  # LaTex math expressions
            answers[i] = str(elem)

    # Concatenate strings and place in a new list
    formatted_answers = []
    answer = ""
    for elem in answers:
        if elem == "\\answer" or elem == "\\correctanswer":
            if answer:
                formatted_answers.append(answer)
                answer = ""
            formatted_answers.append(elem)
        else:  #
            answer += elem

    # Need to append last alternative as well
    formatted_answers.append(answer)

    return formatted_answers
