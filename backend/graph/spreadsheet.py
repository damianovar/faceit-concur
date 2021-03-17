# spreadsheet.py
# Using gspread as a google API to access the spreadsheets and oauth 2 to grant access to google account

import gspread
from oauth2client.service_account import ServiceAccountCredentials
from pathlib import Path
import numpy as np
import pandas as pd
from .cu_rel import CU_Relations

KC_COLUMN = 9
KC_CONTEXT_COLUMN = 10
KC_COLUMN_EXCLUDE = "Content Units within the section"
KC_CONTEXT_COLUMN_EXCLUDE = "Context of content Units within the section"


def connect_to_spreadsheet(spreadhseet, worksheet):
    """

    :param document: string, name of spreadsheet, most likely list of knowledge contents
    :param course: string, name of worksheet, or name of course if you will
    :return: google spreadsheet, sheet with overview of the course
    """

    # Get correct filepath to client_secret.json
    #basedir = Path("src/services/")
    basedir = Path().absolute()
    print(basedir)
    data_json = basedir / "faceit-concur" /"backend" / "graph" / "services"/ "client_secret.json"
    # use creds to create a client to interact with the Google Drive API
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name(data_json, scope)
    client = gspread.authorize(creds)
    print("Files")
    variabels = client.list_spreadsheet_files()
    #client.create("testing")
    for thing in variabels:
        print(thing["name"])

    # Find a workbook by name and open the first sheet
    # Make sure you use the right name here.
    ss = client.open(spreadhseet)
    
    try:
        print(ss.worksheets())
        return ss.worksheet(worksheet)
    except gspread.SpreadsheetNotFound as s:
        print(f"Error: {s}")
        return
    except gspread.WorksheetNotFound as w:
        print(f"Error: {w}")
        return


def get_kcs_and_context(spreadsheet: str = "list of knowledge contents",
                        worksheet: str = "TTK4235 - embedded systems",
                        kc_column: int = KC_COLUMN,
                        kc_context_column: int = KC_CONTEXT_COLUMN):
    """
    :param spreadsheet: str, name of spreadsheet
    :param worksheet: str, name of worksheet
    :param kc_context_column: int, column with the context of the kcs
    :param kc_column: int, Column with the kcs
    :return: tuple(list, list), list of kcs and array of contexts
    """
    ws = connect_to_spreadsheet(spreadsheet, worksheet)
    # Filter out unique kcs and contex from the column and store it in a numpy array
    kc_list = np.array(list(set(ws.col_values(kc_column))))
    kc_context_list = np.array(list(set(ws.col_values(kc_context_column))))

    # Removes empty string (empty cell in spreadsheet
    kc_list = np.delete(kc_list, 0)
    kc_context_list = np.delete(kc_context_list, 0)

    return kc_list.tolist(), kc_context_list.tolist()


def read_kcs_and_position_from_spreadsheet(spreadsheet: str = "LA list with categories",
                                           worksheet: str = "Sheet1",
                                           kc_column: int = 14,
                                           kc_position_column: int = 15):

    ws = connect_to_spreadsheet(spreadsheet, worksheet)

    return ws.col_values(kc_column), ws.col_values(kc_position_column)


def read_course_category_tree_3(spreadsheet: str, worksheet: str):
    """
    #works with spreadsheet where you only need 3 columns
    :param spreadsheet:
    :param worksheet:
    :return:
    """
    ws = connect_to_spreadsheet(spreadsheet, worksheet)
    l1 = ws.col_values(1)
    l2 = ws.col_values(2)
    l3 = ws.col_values(3)
    return l1, l2, l3


def read_course_category_tree(spreadsheet, worksheet, num_of_subtopics: int):
    """
    #TODO: make this work with any amount of columns, might wanna use a dictionary
    :param spreadsheet: name of spreadsheet
    :param worksheet: name of worksheet
    :param num_of_subtopics: number of columns with
    :return:
    """
    ws = connect_to_spreadsheet(spreadsheet, worksheet)

    topic_cols = []
    for col in range(num_of_subtopics):
        if not topic_cols:
            topic_cols = [ws.col_values(col+1)]
        else:
            topic_cols.append(ws.col_values(col+1))
    return topic_cols


def read_cu_relations(spreadsheet: str, worksheet: str):
    ws = connect_to_spreadsheet(spreadsheet, worksheet)
    # There are 6 columns to care about and store
    cu_rel = CU_Relations(ws.col_values(1), ws.col_values(2), ws.col_values(3), ws.col_values(4), ws.col_values(5), ws.col_values(6))
    cu_rel.cus = cu_rel.cus[:end]
    cu_rel.necessary = cu_rel.necessary[:end]
    cu_rel.useful = cu_rel.useful[:end]
    cu_rel.generalize = cu_rel.generalize[:end]
    cu_rel.synonym = cu_rel.synonym[:end]
    cu_rel.dlc = cu_rel.dlc[:end]
    return cu_rel


def get_professor_matrix(
        row: int,
        column: int,
        spreadsheet: str = "list of knowledge contents",
        worksheet: str = "TTK4235 - embedded systems"):
    ws = connect_to_spreadsheet(spreadsheet, worksheet)
    return np.array(ws.get_all_values()[row - 1:][column - 1:], dtype='float16').tolist()


def read_kcs_from_csv(filepath, column_name):
    """
    TODO: edit name to read_column_from_csv
    :param filepath: str, name of filepath
    :param column_name: str, name of column with kcs
    :return: list, name of kcs
    """
    try:
        df = pd.read_csv(filepath)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return

    return df[column_name]


def read_kc_matrix_from_csv():
    raise NotImplementedError
