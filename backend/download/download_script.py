import os.path
import io
from zipfile import ZipFile
from PIL import Image
from backend.models.models import Question

##########################
# GET Questions #
##########################


class Download:
    def get_questions_by_selection(selections) -> Question:

        questions = []
        correct_answers = []
        options = []
        taxonomys = []
        taxonomy_levels = []
        author_emails = []
        question_types = []
        notes_teachers = []
        notes_students = []
        feedback_students = []
        question_disclosabilities = []
        solution_disclosabilities = []
        question_image = []

        for select_id in selections:
            for ques in Question.objects():
                db_id = str(ques.id)
                if select_id == db_id:
                    questions.append(ques.question)
                    correct_answers.append(ques.correct_answer)
                    options.append(ques.options)
                    kc_object = ques.kc_list
                    kc_list = []
                    for kc in kc_object:
                        kc_list.append(kc.name)
                    taxonomys.append(kc_list)
                    taxonomy_levels.append(ques.kc_taxonomy)
                    author_emails.append(ques.author_email)
                    question_types.append(ques.QuestionType)
                    notes_teachers.append(ques.notes_teacher)
                    notes_students.append(ques.notes_student)
                    feedback_students.append(ques.feedback_student)
                    question_disclosabilities.append(ques.question_disclosability)
                    solution_disclosabilities.append(ques.solution_disclosability)
                    if ques.image:
                        # Image.open(io.BytesIO(ques.image.read())).save('result_file' + '.png', 'PNG')
                        question_image.append(ques.image.read())
                    else: 
                        question_image.append("None")
                    break

        return {"Questions": questions, "answer": correct_answers, "Options": options, "kc": taxonomys, "kc_taxonomy": taxonomy_levels, "author_email": author_emails,
                "QuestionType": question_types, "notes_teacher": notes_teachers, "notes_student": notes_students, "feedback_student": feedback_students,
                "question_disclosability": question_disclosabilities, "solution_disclosability": solution_disclosabilities, "question_image": question_image} 

      
    def zip_download(download, zfn, fn):
        save_path = "static/clients/zip"
        zip_file_name = os.path.join(save_path, zfn)
        file_name = os.path.join(save_path, fn)
        image_path_list = []

        with open(file_name, 'w') as of:

            of.write(r"% global variable to conditionally print the solutions together with the questions" +'\n')
            of.write(r"\newif \ifshowsolutions" + '\n')
            of.write(r"% \showsolutionstrue % comment this line to have :showsolutionsfalse" )
            of.write('\n\n')
            of.write(r"% global variable to conditionally print the contents map of the instructional material" + '\n')
            of.write(r"\newif \ifshowcontentsmap" +'\n' +r"\showcontentsmaptrue % comment this line to have ``showcontentsmapfalse''" + '\n' + '\n')
            of.write(r"% required packages" + '\n' + r"\RequirePackage{enumerate}" + '\n' + r'\RequirePackage[table]{xcolor}' + '\n' + '\n')
            of.write(r"% supported document classes - decomment the one that you prefer" + '\n' + r"\documentclass{article}" + '\n' +r"% \documentclass{beamer}" +'\n\n')
            of.write(r"% commands to define the contents maps" +'\n' + r"\input{contentsmapping}"+ '\n\n')
            of.write(r"% -------------------------------------------------------------- %" + '\n')
            of.write(r"\begin{document}" + '\n'+ '\n')
            #of.write(r"% example of how to set some variables as global settings " + '\n')
            #of.write(r"\def\QUESTIONAUTHOREMAIL{myemail@something.edu}" +'\n' + r"\def\QUESTIONDISCLOSABILITY{everybody}" + '\n' + r"\def\QUESTIONSOLUTIONDISCLOSABILITY{everybody}" + '\n\n')
            #of.write(r"% example of a contents map -- always keep the ``ifshowcontentsmap .. \fi''" + '\n')
            #of.write(r"\ifshowcontentsmap" + '\n' + r'\begin{ContentsMap}' + '\n\t' +r'%' + '\n')
            #of.write("\t" + r"\begin{DevelopedContents}" + '\n\t\t' + r"free evolution & u1, e2 \\" + "\n\t" + "\end{DevelopedContents}" + "\n\t" +r"%" + "\n" )
            #of.write("\t" + r"\begin{PrerequisiteContents}" + '\n\t\t' + r"ODEs & u1, e1 \\" + '\n\t\t' + r"linear time invariant systems & u2, e2 \\" + "\n\t" + "\end{PrerequisiteContents}" + "\n\t" +r"%" + "\n" )
            #of.write(r"\end{ContentsMap}" +'\n' + r"\fi" + '\n' + '\n')

            ind = 0
            for i in list(range(len(download["Questions"]))):
                ind += 1
                of.write(r"\begin{IndexedQuestion}" +'\n' )
                of.write('\t'+ r"\QuestionAuthorEmail{{{}}}".format(download["author_email"][i]) + '\n')
                #of.write( "{" + r"Question {}".format(ind) + "}" +'\n' )
                #of.write('\t'+  r"\QuestionKCs{{{}}}".format(download["kc"][i]) + '\n')
                of.write('\t'+  r"\QuestionContentUnits{")
                for j in download["kc"][i]:
                    #print(download["kc"][i].index(j))
                    if download["kc"][i].index(j) == (len(download["kc"][i])-1):
                        of.write(str(j))
                    else:
                        of.write(str(j))
                        of.write(",")
                of.write("}")
                of.write('\n')


                #of.write('\t'+  r"\QuestionTaxonomyLevels{{{}}}".format(download["kc_taxonomy"][i])+ '\n')
                of.write('\t'+  r"\QuestionTaxonomyLevels{")
                for t in download["kc_taxonomy"][i]:
                    if download["kc_taxonomy"][i].index(t) == (len(download["kc_taxonomy"][i]) - 1):
                        of.write(str(t))
                    else:
                        of.write(str(t))
                        of.write(",")
                of.write("}")
                of.write('\n')

                of.write('\t' + r"\QuestionType{{{}}}".format(download["QuestionType"][i]) + '\n')

                question = download["Questions"][i]
                of.write('\t' + r"\QuestionBody{{{}}} ".format(question) + '\n')

                correct_ans = download["answer"][i]
                options = download["Options"][i]
                # print(correct_ans)
                # print(options)

                ques_image = download["question_image"][i]
                print(ques_image)
                #checking if the ques_image exists was getting difficult with "None" so using length because a binary image will definetly have a greater size
                if ques_image != None and len(ques_image) > 6:        
                    of.write('\t' + r"\QuestionImage" + "{" + r"\includegraphics{{{}}}".format("image" + str(i) + '.png') + '}' + '\n')
                    image_name = 'image' + str(i) + '.png'
                    image_save_path = os.path.join(save_path, image_name)
                    Image.open(io.BytesIO(ques_image)).save(image_save_path, 'PNG')
                    image_path_list.append(image_save_path)

                of.write('\t'+ r"\QuestionPotentialAnswers"+ '\n' )
                of.write('\t' +"{" + '\n')

                counter = 0

                for k, entry in enumerate(options):

                    if any(j.strip() == entry.strip() for j in correct_ans):
                        of.write('\t'+ '\t' + r"\correctanswer{}".format(options[k]) + '\n')
                        counter += 1
                    else:
                        of.write('\t'+ '\t' + r"\answer{}".format(options[k]) + '\n')
                        counter += 1

                of.write('\t' + "}" + '\n')

                of.write('\t' + r"\QuestionNotesForTheTeachers{{{}}}".format(download["notes_teacher"][i]) + '\n')
                of.write('\t' + r"\QuestionNotesForTheStudents{{{}}}".format(download["notes_student"][i]) + '\n')
                of.write('\t' + r"\QuestionFeedbackForTheStudents{{{}}}".format(download["feedback_student"][i]) + '\n')
                of.write('\t' + r"\QuestionDisclosability{{{}}}".format(download["question_disclosability"][i]) + '\n')
                of.write('\t' + r"\QuestionSolutionDisclosability{{{}}}".format(download["solution_disclosability"][i]) + '\n')

                of.write(r"\end{IndexedQuestion}")
                of.write('\n')
            of.write(r"\end{document}")

        zipobj = ZipFile(zip_file_name, 'w')
        zipobj.write(file_name, "questions.tex")
        zipobj.write(r"backend/download/contentsmapping.tex", "contentsmapping.tex")
        for image_file in image_path_list:
            zipobj.write(image_file, "images/"+os.path.basename(image_file))
        zipobj.close()
