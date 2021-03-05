import pandas as pd
import numpy as np
import re
from TexSoup import TexSoup  #, TokenWithPosition
import subprocess

# ---------------- HELPER METHODS ------------------

__alphabet__ = "abcdefghij"


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
    q = q.replace('$$',"$")
    q = q.replace("\Reals","")    #LaTex commands not identified by qti
    q = q.replace(r"\bm" ,"")
    q = q.replace("\qquad","")
    q = q.replace(" $","$")       #remove spacing to avoid problems with math
    #q = q.replace("includegraphics")
    #print(q)

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


# ---------------------------------------------------


################
# .tex to .txt #
################

def tex_to_txt(file, quiz_title, output_file=None):
    """
    Takes in a latex file with exercises and parses this into a .txt file
    :param file: latex file with questions
    :param quiz_title: title of quiz
    :param output_file: textfile we want to write to
    :return: text file we can easily convert to qti using text2qti
    """
    if output_file is None:
        output_file = file.split('/')[-1].replace(".tex", ".txt")

    with open(file) as f:
        data = f.read()
        tex = TexSoup(data)

    frames = list(tex.children)
    #print(frames[0])

    with open(output_file, 'w') as of:
        of.write("Quiz title: " + quiz_title + '\n')
        of.write("Quiz description: Hello\n\n")
        ind = 0
        for frame in frames:
            if frame.name == 'frame':
                ind += 1
                of.write("Title: " + "?" + '\n')
                frame_contents = list(frame.children)
                #print(frame_contents[0])

                # Was used to deal with inconsistent frame setups (use of small environment for entire frame)
                if len(frame_contents) == 1 and frame_contents[0].name == 'small':
                    frame_contents = list(frame_contents[0].children)

                question = get_question(frame_contents)
                of.write(str(ind) + ".    " + question + '\n')

                answers_i = 3  # Usually where the framecontents is

                # in case first field is \vspace or another setting instead
                if "\QuestionAnswers" not in str(frame_contents[answers_i]):
                    for i, field in enumerate(frame_contents):
                        if "\QuestionAnswers" in str(field):
                            answers_i = i
                            break
                answers = format_answers([token for token in frame_contents[answers_i]])

                counter = 0

                if(str(answers).count('\\correctanswer') > 1 ):

                    for i, entry in enumerate(answers):

                            if '\\answer' in entry:
                                of.write("[" + "]" + answers[i + 1] + '\n')
                                counter += 1
                            elif '\\correctanswer' in entry:
                                of.write("[" + '*'  + "]" + answers[i + 1] + '\n')
                                counter += 1
                else:

                    for i, entry in enumerate(answers):

                        if '\\answer' in entry:
                            of.write(__alphabet__[counter] + ")    " + answers[i + 1] + '\n')
                            counter += 1
                        elif '\\correctanswer' in entry:
                            of.write('*' + __alphabet__[counter] + ")   " + answers[i + 1] + '\n')
                            counter += 1


            of.write('\n')

    return output_file


###################

def parse_tex(file):
    """
    Parse from latex-file to a pandas dataframe table
    @:param: file (.tex), latex file with questions
    @:return: table, pandas dataframe table categorized
    """
    with open(file) as f:
        data = f.read()
        tex = TexSoup(data)

    frames = list(tex.children)
    table = pd.DataFrame()

    counter = 1
    for frame in frames:

        if frame.name == 'IndexedQuestion':


            frame_contents = list(frame.children)


            # Was used to deal with inconsistent frame setups (use of small environment for entire frame)
            if len(frame_contents) == 1 and frame_contents[0].name == 'small':
                frame_contents = list(frame_contents[0].children)

            #question = frame.args[0].value.split(' ')[-1].replace('Q', '')
            # question = str(get_field("QuestionBody", frame_contents))[1:-1]


            author_email = str(get_field("QuestionAuthorEmail", frame_contents))[1:-1]
            KCs = str(get_field("QuestionContentUnits", frame_contents))[1:-1]
            KCs = KCs.split(",")
            KCTaxonomies = str(get_field("QuestionTaxonomyLevels", frame_contents))[1:-1]
            #print(KCTaxonomies)
            #KCTaxonomies = eval(KCTaxonomies)
            KCTaxonomies = KCTaxonomies.replace(' ','').split(",")
            QuestionType = str(get_field("QuestionType", frame_contents))[1:-1]
            notes_teacher = str(get_field("QuestionNotesForTheTeachers", frame_contents))[1:-1]
            notes_student = str(get_field("QuestionNotesForTheStudents", frame_contents))[1:-1]
            feedback_stud = str(get_field("QuestionFeedbackForTheStudents", frame_contents))[1:-1]
            question_disclosa = str(get_field("QuestionDisclosability", frame_contents))[1:-1]
            solution_disclosa = str(get_field("QuestionSolutionDisclosability", frame_contents))[1:-1]
            question = get_question(frame_contents)

            #answers = str(get_field("QuestionAnswers", frame_contents))[1:-1]

            answers_i = 3  # Usually where the framecontents is

            # in case first field is \vspace or another setting instead
            if "\QuestionPotentialAnswers" not in str(frame_contents[answers_i]):
                for i, field in enumerate(frame_contents):
                    if "\QuestionPotentialAnswers" in str(field):
                        answers_i = i
                        break
            answers = format_answers([token for token in frame_contents[answers_i]])
            ans = []
            cor_ans = []
            for i, entry in enumerate(answers):

                if '\\answer' in entry:
                    ans.append( answers[i + 1])

                elif '\\correctanswer' in entry:
                    ans.append(answers[i + 1] )
                    cor_ans.append(answers[i + 1] )

            # separator = " , "
            # #ans = separator.join(ans)
            # cor_ans = separator.join(cor_ans)

            row = pd.DataFrame({ 'author_mail': author_email,
                                'question_number': int(counter),
                                'question': question,
                                'KCs': [KCs],
                                'KCTaxonomies':[KCTaxonomies] ,
                                'Notesforteacher' : notes_teacher,
                                'Notesforstudent': notes_student,
                                'feedbackforstudent': feedback_stud,
                                'question_disclosability': question_disclosa,
                                'solution_disclosability': solution_disclosa,
                                'Question_type': [QuestionType],
                                'correct_answer': [cor_ans],
                                'options' : [ans]

                                },
                               index=[0])
            table = table.append(row, ignore_index=True)
            counter += 1
    return table

#tab = parse_tex(r"C:\Users\jaf\Documents\programming\KC_map\sample_data\E4.tex")
# tab = parse_tex(r"C:\Users\manis\OneDrive\Desktop\Summer2020\HiWi\KC-Mapping\sample_data\test.tex")
# print(tab)
