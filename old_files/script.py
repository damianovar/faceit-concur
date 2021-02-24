from pymongo.errors import ServerSelectionTimeoutError
from src.database.models.models import *
import pandas as pd
from src.texParser import parse_tex, tex_to_txt
from src.database import database as api
import src.visualisation as vis
import src.spreadsheet as ss
import numpy as np
from src.infrastructure.state import State
from src.cu_rel import CU_Relations
from src import data_handling, upload_canvas
from mongoengine import InvalidCollectionError, connect, disconnect, InvalidDocumentError
from zipfile import ZipFile
#####################################################################
#                               GLOBALS                             #
#####################################################################

state = State()  # GLOBAL STATE - make into a singleton


#####################################################################
#                               MENUS                               #
#####################################################################

def welcome():
    print("Please login or signup to use this service")
    print("1: Login")
    print("2: Sign up")


def menu():
    print("E: Exit the application")
    print("1: Register question")
    print("2: Download Questions in latex format")
    #print("2: Fetch a list of CUs from a spreadsheet")
    #print("3: Visualize a KC Mapping")
    #print("4: Get probability graph")
    #print("5: Upload test to canvas")
    #print("6: Play the KC Mapping game")
    print("3: Hierarchy tree")
    #print("8: Download Questions")



def database_menu():
    print("======= DATABASE OPTIONS =======")
    print("[I]NSERT - [U]PDATE - [D]ELETE")
    print("E: Exit the game")
    print("1: Country")
    print("2: University")
    print("3: KC")
    print("4: Connection (KC Map)")
    print("5: Course")
    print("6: User")
    print("7: Questions")
    print("Example: I3 will let you insert a new KC row, U2 would let you update a row and D3 would let you delete a kc")


#####################################################################
#                              END MENUS                            #
#####################################################################


def spreadsheet():
    kcs = []
    choice = input(
        "What do you want to get from the spreadsheet? A [L]ist of KCs or a [M]atrix of dependencies?: ").upper()
    if choice == 'L':
        sheet_or_list = input(
            "Do you want to read from [S]preadsheet or a [T]extfile?: ").upper()
        if sheet_or_list == "S":
            local_or_online = input(
                "Do you want to read from .[C]sv file or a [G]oogle spreadheet? ").upper()
            # User chose CSV File
            if local_or_online == "C":
                filepath = input("Enter filepath to .csv file: ")
                column_name = input(
                    "Enter name of column with kcs in csv file: ")
                state.kc_list = ss.read_kcs_from_csv(filepath, column_name)
            # User chose Google Spreadsheet
            elif local_or_online == "G":
                spreadsheet = input("What is the name of the spreadsheet? ")
                worksheet = input("What is the name of the worksheet? ")
                kc_column = int(
                    input("Enter number of column with KC in it: "))
                state.kc_list, _ = ss.get_kcs_and_context(
                    spreadsheet=spreadsheet, worksheet=worksheet, kc_column=kc_column, kc_context_column=kc_column+1)
        elif sheet_or_list == "T":
            try:
                with open(input("Enter the filepath: "), 'r') as f:
                    l = f.readlines()
                    for line in l:
                        line = line.rstrip()
                        if state.kc_list:
                            state.kc_list.append(line)
                        else:
                            state.kc_list = [line]
            except FileNotFoundError:
                print("Could not open file...")
                return
        if state.kc_list:
            print("KCs loaded successfully")

    elif choice == 'M':
        row = int(input("First row of the matrix: "))
        col = int(input("First column of the matrix: "))
        spreadsheet = input("Name of spreadsheet: ")
        worksheet = input("Name of worksheet: ")
        state.kc_matrix = ss.get_professor_matrix(
            row, col, spreadsheet, worksheet)


def database():
    choice = input(
        "Which operation do you wanna do? (Type e or exit to escape) ").upper()
    while True:
        if choice == "I1":
            register_country()
        elif choice == "I2":
            register_university()
        elif choice == "I3":
            register_kc()
        elif choice == "I5":
            register_course()
        elif choice == "I7":
            register_question()
        elif choice == "U1":
            # update_country()
            pass
        elif choice == "U2":
            update_university()
        elif choice == "U3":
            update_kc()
        elif choice == "U4":
            # update_connection()
            pass
        elif choice == "U5":
            update_course()
        elif choice == "D1":
            remove_country()
        elif choice == "D2":
            remove_university()
        elif choice == "D3":
            remove_kc()
        elif choice == "D4":
            remove_connection()
        elif choice == "D5":
            remove_course()
        elif choice == "E" or choice == "EXIT":
            break
        else:
            # TODO: If user inserts "show options" show the database menu
            print("Please insert a valid option")
        database_menu()
        choice = input(
            "Which operation do you wanna do? (Type e or exit to escape) ").upper()


##############################################################
#                            MAIN LOOP                       #
##############################################################


def main():
    print("===== WELCOME TO CONQUER =====")
    try:
        connect(db="KCMap",
                username="developer",
                password="TTK4260",
                host="mongodb+srv://developer:TTK4260@kcbank.lwcpe.mongodb.net/KCMap?retryWrites=true&w=majority")
    except ServerSelectionTimeoutError:
        print("Could not reach server")
        return

    welcome()
    choice = input("What will you do? (Press e or exit to exit) ").upper()
    while True:
        if choice == '1':
            login()
            break
        elif choice == '2':
            created = create_account()
            if created:
                break
        elif choice == "E" or choice == "EXIT":
            print("Goodbye! ")
            return
        else:
            print("Please enter a valid value\n")
            welcome()
            choice = input("What will you do? ")

    # Course

    menu()
    choice = input("Your choice: ")

    while True:
        if choice == '1':
            #database_menu()
            #database()
            register_question()
        elif choice == '2':
            #spreadsheet()
            #register_kcs_from_list()  # TODO: Make sure this works and creates
            _questions_latex()
        elif choice == '3':
            #visualize_map()
            cu_hierarchy_mapping()
        elif choice == '4':
            probability_graph()
        elif choice == '5':
            upload_test()
        elif choice == '6':
            kc_mapping_game()
        elif choice == '7':
            # kc_category_mapping()
            #cu_hierarchy_mapping()
            # vis.map_kc_categories(["alg", "stat", "geo"], ["1", "1.2", "1.3"])
            pass
        elif choice == '8':
            download_questions()
        elif choice == '9':
            #download_questions_latex()
            pass
        elif choice == 'E' or choice == "EXIT":
            print("Goodbye! ")
            break
        else:
            print("Please enter a valid option!")

        menu()
        choice = input(
            "Your choice: (Press E or Exit to close the app)").upper()
    disconnect()


#####################################################################
#                            LOGIN / SIGNUP                         #
#####################################################################


def create_account():
    print(" ************** REGISTER NEW USER **************")

    name = input("What is your name? ")

    user = api.find_user_by_name(name)
    if user:
        print("User already exists")
        return False
    else:
        state.user = register_user()
        print("User is now created!")
        return True


def login():
    """
    You need to login to even start the program
    """
    print("*********** LOGIN ***********")
    name = input("What is your name? ")
    user = api.find_user_by_name(name)
    while True:
        if user:
            state.user = user
            # Need this to be here for now due to Nonetype in state class
            state.user.name = user.first_name + " " + user.last_name
            print(
                f"Welcome back {state.user.first_name} {state.user.last_name}")
            break
        else:
            print("Could not find user in database, try again")
            name = input("What is your name? ")
            user = api.find_user_by_name(name)


def logout():
    # TODO: Find out if we actually need this method
    print(
        f"********* {state.user.first_name} {state.user.last_name} IS NOW LOGGED OUT **********")
    state.user = None


#####################################################################
#                              REGISTER                             #
#####################################################################

def register_user():
    print("********* REGISTER USER *********")
    name = input("Please enter a name: ")
    nationality = find_country()
    position = input(
        "What role in your institution do you have? (STUDENT, PROFESSOR, OTHER)").upper()
    university = input("Pleas enter a university: ")
    uni = api.find_university(university)
    courses = []
    add_to_list(courses, "course", Course)
    new_user = api.add_user(name=name, nationality=nationality,
                            pos=position, university=uni, courses=courses)
    return new_user


def register_country():
    print("********* REGISTER COUNTRY *********")
    name = input("Please enter a name: ")
    universities = []
    choice = input(
        f"Do you want to add any universities to {name} yet? (Y/N) ").upper()
    if choice == 'Y':
        add_to_list(universities, "university", University)
        api.add_country(name=name, universities=universities)
        return
    api.add_country(name=name)


def register_university():
    print("********* REGISTER UNIVERSITY *********")
    name = input("Please enter a name: ")
    country_name = input("Which country is the university sited in? ")
    country = api.find_country(country_name)
    api.add_university(name=name, country=country)


def register_course():
    print("********* REGISTER A COURSE *********")
    code = input("Please enter a course code: ").upper()
    name = input("Please enter a course name: ")
    semester = input("Please enter a semester: ")
    choice = input(
        "Do you want to add KCs to the course right away? (Y/N): ").upper()
    if choice == "Y":
        spreadsheet()
    if state.kc_list:
        api.add_course(name=name, code=code,
                       semester=semester, kcs=state.kc_list)
    else:
        api.add_course(name=name, code=code, semester=semester)


def register_kc():
    print("********* REGISTER A KC *********")
    name = input("Please enter the KC: ").lower()

    courses = []
    while True:
        if name == find_course():
            courses.append(name)
        choice = input("Do you want to add another course? (y/n): ").lower()
        if choice == 'n':
            break
    api.add_kc(name, courses)


def register_question():
    print("********* REGISTER A Question *********")


    author = state.user
    var = input(
        "Do you want to assign the question to a course?\n Press Y for Yes and N for No")
    if var.lower() == 'y':
        state.course = find_course()
        if not state.course:
            register_course()
    elif var.lower() == 'n':
        state.course = None

    file_path = input("Enter file path:")
    tab = parse_tex(file_path)


    for i in range(len(tab)):
        question_number = tab.question_number[i]
        question = tab.question[i]
        kc_list = []
        for kc in tab.KCs[i]:
            kc_l = find_kc(kc)
            if not kc_l:
                kc_l = api.add_kc(kc, state.course)
            kc_list.append(kc_l)

        kc_taxonomy = tab.KCTaxonomies[i]
        correct_answer = tab.correct_answer[i]
        options = tab.options[i]

        author_email = tab.author_mail[i]
        QuestionType = tab.Question_type[i]
        notes_teacher = tab.Notesforteacher[i]
        notes_student = tab.Notesforstudent[i]
        feedback_stud = tab.feedbackforstudent[i]
        question_disclosa = tab.question_disclosability[i]
        solution_disclosa = tab.solution_disclosability[i]

        api.add_question(author=author,
                         question_number=question_number,
                         question=question,
                         course=state.course,
                         kc_list=kc_list,
                         kc_taxonomy=kc_taxonomy,
                         correct_answer=correct_answer,
                         options=options,
                         author_email=author_email,
                         QuestionType=QuestionType,
                         notes_teacher=notes_teacher,
                         notes_student=notes_student,
                         feedback_student=feedback_stud,
                         question_disclosability=question_disclosa,
                         solution_disclosability=solution_disclosa)

def download_questions():
    __alphabet__ = "abcdefghij"

    print("How do you want to download questions?")
    print("1: By KC name")
    print("2: By KC taxonomy")
    print("3: By Course")
    choice = input()

    if choice == "1":
        kc = input("Please enter the KC")
        download = api.get_questions_by_kc(name=kc)

    elif choice == "2":
        taxonomy_level = input("Please enter the taxonomy_level (e.g (1, 1) or  ((1, 1), (1, 1)) )")
        # taxonomy = input("Input taxonomy here (e.g 1,2  2,3 or 1,1) ")
        # tax = [int(num) for num in taxonomy.split(",")]
        download = api.get_questions_by_kc_taxonomy(level=taxonomy_level)

    elif choice == "3":
        course = input("Please enter the course")
        download = api.get_questions_by_course(name = course)

    else: print("Please input a valid choice")

    file_name = input("Please enter output file name:")
    file_name = file_name + '.txt'
    with open(file_name, 'w') as of:
        of.write("Quiz title: " '\n')
        of.write("Quiz description: Hello\n\n")

        ind = 0
        for i in list(range(len(download["Questions"]))):
            ind += 1
            question = download["Questions"][i]
            of.write(str(ind) + ".    " + question + '\n')

            correct_ans = download["answer"][i]
            options = download["Options"][i]
            # print(correct_ans)
            # print(options)

            counter = 0

            if (len(correct_ans) > 1):

                for i, entry in enumerate(options):

                    if any(j.strip() == entry.strip() for j in correct_ans):
                        of.write("[" + '*' + "]" + options[i] + '\n')
                        counter += 1
                    else:
                        of.write("[" + "]" + options[i] + '\n')
                        counter += 1
            else:

                for i, entry in enumerate(options):

                    if any(j.strip() == entry.strip() for j in correct_ans):
                        of.write('*' + __alphabet__[counter] + ")   " + options[i] + '\n')
                        counter += 1
                    else:
                        of.write(__alphabet__[counter] + ")    " + options[i] + '\n')
                        counter += 1



            of.write('\n')

def download_questions_latex():

    print("How do you want to download questions?")
    print("1: By CU name")
    print("2: By CU taxonomy")
    print("3: By Course")
    choice = input()

    if choice == "1":
        cu = input("Please enter the CU: ")
        download = api.get_questions_by_kc(name=cu)

    elif choice == "2":
        taxonomy_level = input("Please enter the taxonomy_level (e.g (1, 1) or  ((1, 1), (1, 1)) ): ")
        # taxonomy = input("Input taxonomy here (e.g 1,2  2,3 or 1,1) ")
        # tax = [int(num) for num in taxonomy.split(",")]
        download = api.get_questions_by_kc_taxonomy(level=taxonomy_level)

    elif choice == "3":
        course = input("Please enter the course")
        download = api.get_questions_by_course(name = course)

    else:
        print("Please input a valid choice")
        return

    file_name = input("Please enter output file name:")
    zip_file_name = file_name +'.zip'
    file_name = file_name + '.tex'


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

            of.write('\t' +  "}" + '\n')

            of.write('\t' + r"\QuestionNotesForTheTeachers{{{}}}".format(download["notes_teacher"][i]) + '\n')
            of.write('\t' + r"\QuestionNotesForTheStudents{{{}}}".format(download["notes_student"][i]) + '\n')
            of.write('\t' + r"\QuestionFeedbackForTheStudents{{{}}}".format(download["feedback_student"][i]) + '\n')
            of.write('\t' + r"\QuestionDisclosability{{{}}}".format(download["question_disclosability"][i]) + '\n')
            of.write('\t' + r"\QuestionSolutionDisclosability{{{}}}".format(download["solution_disclosability"][i]) + '\n')

            of.write(r"\end{IndexedQuestion}")
            of.write('\n')
        of.write(r"\end{document}")

    zipobj = ZipFile(zip_file_name,'w')
    zipobj.write(file_name)
    zipobj.write(r"contentsmapping.tex")
    zipobj.close()



def find_connection(user, course, semester):
    return api.find_map_connection(user=user, course=course, semester=semester)


def register_map_connection(semester):
    print("***** REGISTER CONNECTION *******")

    state.connection = find_connection(state.user, state.course, semester)
    if state.connection:
        print("Connection already exists")
        return
    state.kc_matrix = [
        [0.0 for x in range(len(state.kc_list))] for y in range(len(state.kc_list))]


def register_kcs_from_list():
    if not state.kc_list:
        print("I can't find the list of KCs!")
        return

    while not state.course:
        # TODO: Do we want to ask user to exit here if they want?
        state.course = find_course()

    for kc_name in state.kc_list:  # TODO: Fix this code so that it works
        kc = find_kc(kc_name.strip())
        if kc:
            api.update_kc_course_list(kc, state.course)
        if not kc:
            kc = api.add_kc(kc_name, state.course)
        api.update_course_kc_list(state.course, kc)

def cu_relations_mapping():
    ss = input("Enter the name of the spreadsheet: ")
    ws = input("Enter the name of the worksheet: ")
    cu_rels = ss.read_cu_relations("NTNU-TTK4225-2020", "specification of the content units' relations")
    cus = cu_rels.cus
    # add cus to database
    # this goes here ===========
    vis.map_cu_relations(cu_rels)


def kc_mapping_game():  # REGISTER CONNECTION
    print("********* KC MAPPING GAME *********")

    choice = input(
        "Press [N] to to register new connection, [C] to continue the matrix or [E] to exit the application ").upper()
    if choice == 'E':  # Exits out
        return

    elif choice == 'N':  # Creates a connection before it begins
        semester = input("Please enter a semester (E.g: H20, S20, A20) ")
        register_map_connection(semester)

        if state.connection:
            restart = True
        else:
            restart = False
            try:
                state.connection = api.add_connection(
                    state.user, state.course, semester, state.course.kcs, state.kc_matrix)
                print("Connection added successfully")
            except InvalidDocumentError as e:
                print(f"Error: {e}")

    elif choice == 'C':
        restart = False
        state.connection = get_kc_connection()

    kc_matrix, percentage = vis.kc_mapping(
        state.connection, restart, state.course)

    # Updating kcs
    update_connection(kc_matrix, percentage)
    state.connection = get_kc_connection()
    state.kc_list = [kc.name for kc in state.connection.kc_list]
    choice = input("Do you want to show the map right now? (Y/N): ").upper()
    if choice == "Y":
        vis.map_kcs(np.array(state.kc_list),
                    np.array(state.connection.kc_matrix))


def kc_category_mapping():
    worksheet = input(
        "Enter the name of the spreadhsseet you want to use, remember to share API mail with")
    spreadsheet = input("Enter the name of the worksheet you want to use")
    kc_list, positions = ss.read_kcs_and_position_from_spreadsheet(
        "LA list with categories", "Sheet1", 14, 15)
    try:
        vis.map_kc_categories(kc_list, positions)
    except ValueError as e:
        print(f"Error: {e}")


def cu_hierarchy_mapping():
    # worksheet = input("Enter the name of the spreadhsseet you want to use, remember to share API mail with")
    # spreadsheet = input("Enter the name of the worksheet you want to use")
    spread = input("Please enter name of the spreadsheet: ")
    ws = input("Please enter name of the worksheet: ")
    lists = ss.read_course_category_tree("linear-algebra", "specification of the content units' hierarchies", 4)
    try:
        vis.map_cu_hierarchies(lists)
    except ValueError as e:
        print(f"Error: {e}")


#####################################################################
#                               UPDATE                              #
#####################################################################

def update_user():
    choice = input(
        "Wht do you want to update? ([N]ame/[P]osition/[Nat]ionality)").lower()
    if choice == "n":
        new_name = input("Please enter new name: ")
        api.update_user_name(state.user, new_name)


def update_university():
    old_uni = input("Please enter the old name for the university: ")
    university = api.find_university(old_uni)
    new_uni = input("Please enter new name for university: ")
    api.update_university(university, new_uni)


def update_course():
    """ NAME OR CODE"""
    old_code = input("Please enter old course code: ")
    old_name = input("Please enter old course name: ")
    course = api.find_course(old_code)
    choice = input(
        "What dou you want to update? ([C]ode / [N]ame / [B]oth): ").lower()
    if choice == "c":
        new_code = input("Please enter new course code: ")
        api.update_course_code(course, new_code)
    elif choice == "n":
        new_name = input("Please enter new course name: ")
        api.update_course_name(course, new_name)
    elif choice == "b":
        new_code = input("Please enter new course code: ")
        new_name = input("Please enter new course name: ")
        api.update_course_code(course, new_code)
        api.update_course_name(course, new_name)


def update_kc():
    old_name = input("Please enter name of old kc: ")
    kc = api.find_kc_by_name(old_name)
    new_name = input("Please enter new course code: ")
    api.update_kc(kc, new_name)


def update_connection(new_map, percentage):
    api.update_connection(state.connection, new_map, percentage)


#####################################################################
#                               REMOVE                              #
#####################################################################

def remove_user():
    raise NotImplementedError


def remove_country():
    country = input("Which country do you want to remove: ")
    api.delete_country(country)
    print(f"{country.upper()} is now removed")


def remove_university():
    university = input("Which university do you want to remove: ")
    api.delete_university(university)
    print(f"{university.upper()} is now removed")


def remove_course():
    course = input("Which course do you want to remove: ")
    api.delete_course(course)
    print(f"{course.upper()} is now removed")


def remove_kc():
    kc = input("Which kc do you want to remove: ")
    api.delete_country(kc)
    print(f"{kc.upper()} is now removed")


def remove_connection():
    conn = input("Which map do you want to remove: ")
    api.delete_country(conn)
    print(f"{conn.upper()} is now removed")


#####################################################################
#                           FIND INSTANCES                          #
#####################################################################


def find_user():
    name = input("Please enter your name: ")
    # TODO: find more ways to filter a user on
    return api.find_user_by_name(name)


def find_country(name=None):
    if not name:
        name = input("Please enter the name of the country: ")
    return api.find_country(name)


def find_university():
    name = input("Please enter the name of the university: ")
    return api.find_university(name)


def find_course():
    course_code = input("Please enter a course code: ")
    return api.find_course(course_code)


def find_kc(name=None):
    if not name:
        name = input("Please enter a kc: ")
    return api.find_kc_by_name(name)


def find_kc_list():
    course_code = input("Please enter a course code: ")
    return api.get_kc_list_course(course_code)


def find_kc_matrix():
    user_name = state.user.first_name + " " + state.user.last_name
    if not state.course:  # Do we need this
        state.course = input("Please enter a course name: ")
    return api.get_kc_matrix(user_name, state.course.name)


def get_kc_connection():
    return api.find_map_connection(state.user, state.course, "H20")

#####################################################################
#                             VISUALIZE                             #
#####################################################################


def visualize_map():
    """
    Visualize mapping of whatever course and user you'd like
    """
    semester = input(
        "Which semester do you want to look at? (e.g H20, V20, S20) ")
    if not state.course:
        state.course = find_course()
    if not state.kc_list:
        state.kc_list = api.get_kc_list_course(state.course.code)
    kc_matrix = api.find_map_connection(
        state.user, state.course, semester).kc_matrix
    if kc_matrix:
        kcs = []
        for elem in state.course.kcs:
            if not kcs:
                kcs = [elem.name]
            else:
                kcs.append(elem.name)
        vis.map_kcs(np.array(kcs), np.array(kc_matrix))
    else:
        print("Could not find list of kcs or kc connection matrix")


def probability_graph():
    pass


def avg_for_teacher():
    course = find_course()
    kc_matrices = api.get_kc_matrices_course(course.code, course.name)
    data_handling.get_kc_mapping_average(kc_matrices=kc_matrices)


def upload_teacher_kcs():
    course = find_course()
    row = int(input("In which row does the matrix start"))
    column = int(input("In which column does the matrix start"))
    semester = input("Enter a semester: ").upper()
    kc_matrix = ss.get_professor_matrix(row, column)
    api.add_connection(state.user, course, semester, course.kcs, kc_matrix)


def upload_test():
    #tex_to_txt(r"C:\Users\jaf\Documents\programming\KC_map\sample_data\E3.tex", "E3")
    upload_canvas.upload_to_canvas()


##############################################
#                   HELPERS                  #
##############################################
def add_to_list(collection, item, T):
    run = True
    while run:
        value = None
        if T is Course:
            value = find_course()
        elif T is University:
            value = find_university()
        elif T is Country:
            value = find_country()
        elif T is KC:
            value = find_kc()
        if value:
            if collection:
                collection.append(value)
            else:
                collection = [value]
        add_more = input(f"Add more of type {item} ? (Y/N): ").upper()
        if add_more == 'N':
            run = False


#####################################################################
#                             ENTRY POINT                           #
#####################################################################

if __name__ == '__main__':
    main()
