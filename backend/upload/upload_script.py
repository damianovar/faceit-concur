import pandas as pd
import re
import zipfile
from TexSoup import TexSoup  # , TokenWithPosition
from backend.models.models import Question, KC
from backend.upload.state import State

# ---------------- HELPER METHODS ------------------

__alphabet__ = "abcdefghij"
state = State()  # GLOBAL STATE - make into a singleton


def get_field(token_name, frame_contents):
    for token in frame_contents:
        if token.name == token_name:
            return [token.args[0] for token in frame_contents if token.name == token_name][0]
    return {None}


def get_question(frame_contents):
    """
    Ugly function to format the question
    :param frame_contents:
    :return: question in string format
    """
    q = [str(token) for token in frame_contents if token.name == "QuestionBody"][0] \
        .replace("\\QuestionBody{", "")[:-1]

    q = re.sub("[\n\t]", "", q)
    q = re.sub('\s{2,}', ' ', q)
    q = q.replace('$$', "$")
    q = q.replace("\Reals", "")  # LaTex commands not identified by qti
    q = q.replace(r"\bm", "")
    q = q.replace("\qquad", "")
    q = q.replace(" $", "$")  # remove spacing to avoid problems with math
    # q = q.replace("includegraphics")
    # print(q)

    # .strip("\n\t\t").strip("\n\t")\
    # .replace("$\n\t\t", " $").replace("\n\t$", "$").strip("$")

    return q


def format_answers(answers):
    """
    Modifies list of TexNodes and TokenWithPosition to a pure string list
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


def parse_tex(zipf):
    """
    Parse from latex-file to a pandas dataframe table
    @:param: file (.tex), latex file with questions
    @:return: table, pandas dataframe table categorized
    """
    zip_file = zipfile.ZipFile(zipf)
    file_list = zip_file.namelist()

    for file in file_list:
        if file[-4:] == '.tex':
            file = zip_file.open(file)
            data = file.read().decode('UTF-8')
            tex = TexSoup(data)
            frames = list(tex.children)
            table = pd.DataFrame()
            counter = 1
            for frame in frames:
                print(frame.name)
                if frame.name == 'IndexedQuestion':
                    frame_contents = list(frame.children)
                    # Was used to deal with inconsistent frame setups (use of small environment for entire frame)
                    if len(frame_contents) == 1 and frame_contents[0].name == 'small':
                        frame_contents = list(frame_contents[0].children)

                    # question = frame.args[0].value.split(' ')[-1].replace('Q', '')
                    # question = str(get_field("QuestionBody", frame_contents))[1:-1]

                    author_email = str(
                        get_field("QuestionAuthorEmail", frame_contents))[1:-1]
                    KCs = str(get_field("QuestionContentUnits", frame_contents))[
                        1:-1]
                    KCs = KCs.split(",")
                    KCTaxonomies = str(
                        get_field("QuestionTaxonomyLevels", frame_contents))[1:-1]
                    # print(KCTaxonomies)
                    # KCTaxonomies = eval(KCTaxonomies)
                    KCTaxonomies = KCTaxonomies.replace(' ', '').split(",")
                    QuestionType = str(
                        get_field("QuestionType", frame_contents))[1:-1]
                    notes_teacher = str(
                        get_field("QuestionNotesForTheTeachers", frame_contents))[1:-1]
                    notes_student = str(
                        get_field("QuestionNotesForTheStudents", frame_contents))[1:-1]
                    feedback_stud = str(
                        get_field("QuestionFeedbackForTheStudents", frame_contents))[1:-1]
                    question_disclosa = str(
                        get_field("QuestionDisclosability", frame_contents))[1:-1]
                    solution_disclosa = str(
                        get_field("QuestionSolutionDisclosability", frame_contents))[1:-1]
                    question_image_string = str(
                        get_field("QuestionImage", frame_contents))[1:-1]

                    question_image = None
                    if question_image_string != 'None':
                        question_image_string = re.findall(r'{(?:[^{}])*}',question_image_string)
                        for fil in file_list:
                            if fil == question_image_string[0][1:-1]:
                                question_image = zip_file.open(fil)
        
                    image = question_image
                    question = get_question(frame_contents)

                    # answers = str(get_field("QuestionAnswers", frame_contents))[1:-1]

                    answers_i = 3  # Usually where the framecontents is

                    # in case first field is \vspace or another setting instead
                    if "\QuestionPotentialAnswers" not in str(frame_contents[answers_i]):
                        for i, field in enumerate(frame_contents):
                            if "\QuestionPotentialAnswers" in str(field):
                                answers_i = i
                                break
                    answers = format_answers(
                        [token for token in frame_contents[answers_i]])

                    ans = []
                    cor_ans = []
                    for i, entry in enumerate(answers):

                        if '\\answer' in entry:
                            ans.append(answers[i + 1])

                        elif '\\correctanswer' in entry:
                            ans.append(answers[i + 1])
                            cor_ans.append(answers[i + 1])

                    # separator = " , "
                    # #ans = separator.join(ans)
                    # cor_ans = separator.join(cor_ans)

                    row = pd.DataFrame({'author_mail': author_email,
                                        'question_number': int(counter),
                                        'question': question,
                                        'KCs': [KCs],
                                        'KCTaxonomies': [KCTaxonomies],
                                        'Notesforteacher': notes_teacher,
                                        'Notesforstudent': notes_student,
                                        'feedbackforstudent': feedback_stud,
                                        'question_disclosability': question_disclosa,
                                        'solution_disclosability': solution_disclosa,
                                        'Question_type': [QuestionType],
                                        'correct_answer': [cor_ans],
                                        'options': [ans],
                                        'question_image': [image]
                                        },
                                       index=[0])
                    table = table.append(row, ignore_index=True)
                    counter += 1
            return table


def find_kc(name: str) -> KC:
    return KC.objects(name=name).first()


def add_kc(name, courses=None) -> KC:
    # TODO: Courses is actually a single course here, should probably get both course list and course itself
    if courses:
        return KC(name=name, courses=[courses]).save()
    else:
        return KC(name=name, courses=[]).save()


def add_question(question_number, question, author, course, kc_list, kc_taxonomy, correct_answer, options,
                 author_email=None, QuestionType=None, notes_teacher=None, notes_student=None,
                 feedback_student=None, question_disclosability=None, solution_disclosability=None, test=None, image=None) -> Question:
    return Question(question_number=question_number, question=question, author=author, course=course, kc_list=kc_list, kc_taxonomy=kc_taxonomy, correct_answer=correct_answer, options=options,
                    author_email=author_email, QuestionType=QuestionType, notes_teacher=notes_teacher, notes_student=notes_student,
                    feedback_student=feedback_student, question_disclosability=question_disclosability, solution_disclosability=solution_disclosability, test=test, image=image).save()


# ---------------- EXECUTION METHOD ------------------
class Upload:
    def register_question(file_path):

        author = state.user
        tab = parse_tex(file_path)
        for i in range(len(tab)):
            question_number = tab.question_number[i]
            question = tab.question[i]
            kc_list = []
            for kc in tab.KCs[i]:
                kc_l = find_kc(kc)
                if not kc_l:
                    kc_l = add_kc(kc, state.course)
                kc_list.append(kc_l)

            kc_taxonomy = tab.KCTaxonomies[i]
            correct_answer = tab.correct_answer[i]
            options = tab.options[i]
            author_email = tab.author_mail[i]
            question_type = tab.Question_type[i]
            notes_teacher = tab.Notesforteacher[i]
            notes_student = tab.Notesforstudent[i]
            feedback_student = tab.feedbackforstudent[i]
            question_disclosability = tab.question_disclosability[i]
            solution_disclosability = tab.solution_disclosability[i]
            question_img = tab.question_image[i]

            add_question(question_number=question_number,
                         question=question,
                         author=author,
                         course=state.course,
                         kc_list=kc_list,
                         kc_taxonomy=kc_taxonomy,
                         correct_answer=correct_answer,
                         options=options,
                         author_email=author_email,
                         QuestionType=question_type,
                         notes_teacher=notes_teacher,
                         notes_student=notes_student,
                         feedback_student=feedback_student,
                         question_disclosability=question_disclosability,
                         solution_disclosability=solution_disclosability,
                         image=question_img)
