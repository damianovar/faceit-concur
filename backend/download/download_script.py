import os.path
import io
from zipfile import ZipFile
from PIL import Image
from backend.models.models import Question

##########################
# GET Questions #
##########################


class Download:
    """Class for handling downloads. This does not have to be a class!!!!"""
    # TODO: why can't this just be functions??
    def get_questions_by_selection(selections) -> Question:
        """
        Get questions based on a list of object ids.

        List[str] selections

        return obj 
        """

        questions = []
        correct_answers = []
        answers_options = []
        content_units = []
        taxonomy_levels = []
        author_emails = []
        question_types = []
        notes_teachers = []
        notes_students = []
        feedback_students = []
        question_disclosability = []
        solution_disclosability = []
        question_image = []

        for select_id in selections:
            for ques in Question.objects():
                db_id = str(ques.id)
                if select_id == db_id:
                    questions.append(ques.question)
                    correct_answers.append(ques.correct_answer)
                    answers_options.append(ques.options)
                    kc_object = ques.kc_list
                    kc_list = []
                    for kc in kc_object:
                        kc_list.append(kc.name)
                    content_units.append(kc_list)
                    taxonomy_levels.append(ques.kc_taxonomy)
                    author_emails.append(ques.author_email)
                    question_types.append(ques.QuestionType)
                    notes_teachers.append(ques.notes_teacher)
                    notes_students.append(ques.notes_student)
                    feedback_students.append(ques.feedback_student)
                    question_disclosability.append(
                        ques.question_disclosability)
                    solution_disclosability.append(
                        ques.solution_disclosability)
                    if ques.image:
                        # Image.open(io.BytesIO(ques.image.read())).save('result_file' + '.png', 'PNG')
                        question_image.append(ques.image.read())
                    else:
                        question_image.append("None")
                    break

        return {"Questions": questions, "answer": correct_answers, "Options": answers_options, "kc": content_units, "kc_taxonomy": taxonomy_levels, "author_email": author_emails,
                "QuestionType": question_types, "notes_teacher": notes_teachers, "notes_student": notes_students, "feedback_student": feedback_students,
                "question_disclosability": question_disclosability, "solution_disclosability": solution_disclosability, "question_image": question_image}

    def zip_download(download, zfn, fn):
        """
        Make a zip file filled with questions.

        str download
        fun fn
        str zfn
        """
        save_path = "static/clients/zip"
        zip_file_name = os.path.join(save_path, zfn)
        file_name = os.path.join(save_path, fn)
        image_path_list = []

        with open(file_name, 'w') as of:

            # Write the preamble of the main.tex file
            of.write(
                r"% global variable to conditionally print the solutions together with the questions" + '\n')
            of.write(r"\newif \ifshowsolutions" + '\n')
            of.write(
                r"% \showsolutionstrue % comment this line to have :showsolutionsfalse" + '\n')
            of.write('\n')
            of.write(
                r"% global variable to conditionally print the contents map of the instructional material" + '\n')
            of.write(r"\newif \ifshowcontentsmap" + '\n')
            of.write(
                r"\showcontentsmaptrue % comment this line to have ``showcontentsmapfalse''" + '\n')
            of.write('\n')
            of.write(r"% required packages" + '\n')
            of.write(r"\RequirePackage{enumerate}" + '\n')
            of.write(r'\RequirePackage[table]{xcolor}' + '\n')
            of.write('\n')
            of.write(
                r"% supported document classes - decomment the one that you prefer" + '\n')
            of.write(r"\documentclass{article}" + '\n')
            of.write(r"% \documentclass{beamer}" + '\n')
            of.write('\n')
            of.write(r"% commands to define the contents maps" + '\n')
            of.write(r"\input{contentsmapping}" + '\n')
            of.write('\n')
            of.write(
                r"% -------------------------------------------------------------- %" + '\n')
            of.write(r"\begin{document}" + '\n')
            of.write('\n')

            # Write in the main.tex file each question independently
            ind = 0
            for i in list(range(len(download["Questions"]))):
                ind += 1

                # start the environment
                of.write(r"\begin{IndexedQuestion}" + '\n')

                # add the author email
                of.write(
                    '\t' + r"\QuestionAuthorEmail{{{}}}".format(download["author_email"][i]) + '\n')

                # add all the various content units
                of.write('\t' + r"\QuestionContentUnits{")
                for j in download["kc"][i]:
                    if download["kc"][i].index(j) == (len(download["kc"][i])-1):
                        of.write(str(j))
                    else:
                        of.write(str(j))
                        of.write(",")
                of.write("}")
                of.write('\n')

                # add all the various taxonomy levels
                of.write('\t' + r"\QuestionTaxonomyLevels{")
                for t in download["kc_taxonomy"][i]:
                    if download["kc_taxonomy"][i].index(t) == (len(download["kc_taxonomy"][i]) - 1):
                        of.write(str(t))
                    else:
                        of.write(str(t))
                        of.write(",")
                of.write("}")
                of.write('\n')

                # specify the type of question
                of.write(
                    '\t' + r"\QuestionType{{{}}}".format(download["QuestionType"][i]) + '\n')

                # insert the body of the question
                question = download["Questions"][i]
                of.write(
                    '\t' + r"\QuestionBody{{{}}} ".format(question) + '\n')

                # adding, if existing, the image of the body of the question. note that checking
                # if the ques_image exists was getting difficult with "None", so here the code
                # is using "length" (indeed a binary image will definitely have a greater size)
                ques_image = download["question_image"][i]
                print(ques_image)
                if ques_image != None and len(ques_image) > 6:
                    of.write('\t' + r"\QuestionImage" + "{" + r"\includegraphics{{{}}}".format(
                        "image" + str(i) + '.png') + '}' + '\n')
                    image_name = 'image' + str(i) + '.png'
                    image_save_path = os.path.join(save_path, image_name)
                    Image.open(io.BytesIO(ques_image)).save(
                        image_save_path, 'PNG')
                    image_path_list.append(image_save_path)

                # starting adding the potential answers
                correct_ans = download["answer"][i]
                answers_options = download["Options"][i]
                of.write('\t' + r"\QuestionPotentialAnswers" + '\n')
                of.write('\t' + "{" + '\n')

                # adding one answer per time
                for k, entry in enumerate(answers_options):
                    if any(j.strip() == entry.strip() for j in correct_ans):
                        of.write(
                            '\t' + '\t' + r"\correctanswer{}".format(answers_options[k]) + '\n')
                    else:
                        of.write(
                            '\t' + '\t' + r"\answer{}".format(answers_options[k]) + '\n')

                # closing writing the potential answers
                of.write('\t' + "}" + '\n')

                # writing the ancillary fields
                of.write(
                    '\t' + r"\QuestionNotesForTheTeachers{{{}}}".format(download["notes_teacher"][i]) + '\n')
                of.write(
                    '\t' + r"\QuestionNotesForTheStudents{{{}}}".format(download["notes_student"][i]) + '\n')
                of.write('\t' + r"\QuestionFeedbackForTheStudents{{{}}}".format(
                    download["feedback_student"][i]) + '\n')
                of.write('\t' + r"\QuestionDisclosability{{{}}}".format(
                    download["question_disclosability"][i]) + '\n')
                of.write('\t' + r"\QuestionSolutionDisclosability{{{}}}".format(
                    download["solution_disclosability"][i]) + '\n')

                # end writing the question environment
                of.write(r"\end{IndexedQuestion}")
                of.write('\n')

            # end writing the main.tex document
            of.write(r"\end{document}")
            of.write('\n')

        # create a .zip file where we compress the various things
        zipobj = ZipFile(zip_file_name, 'w')

        # add the main.tex file
        zipobj.write(file_name, "main.tex")

        # add the contentsmapping.tex file
        zipobj.write(r"backend/download/contentsmapping.tex",
                     "contentsmapping.tex")

        # add the various images
        for image_file in image_path_list:
            zipobj.write(image_file, "images/"+os.path.basename(image_file))

        # finish the job
        zipobj.close()
