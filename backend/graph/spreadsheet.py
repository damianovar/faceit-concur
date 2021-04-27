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
    data_json = basedir / "faceit-concur" / "backend" / \
        "graph" / "services" / "client_secret.json"
    # use creds to create a client to interact with the Google Drive API
    scope = ['https://spreadsheets.google.com/feeds',
             'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name(data_json, scope)
    client = gspread.authorize(creds)

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

    # Find the largest column
    desired_size = 0
    for col in topic_cols:
        desired_size = max(desired_size, len(col))

    for iterator in range(len(topic_cols)):
        topic_cols[iterator] = augment_column(
            topic_cols[iterator], desired_size)

    return topic_cols


def augment_column(column, desired_size):
    for i in range(desired_size - len(column)):
        column.append('')
    return column


def read_cu_relations(spreadsheet: str, worksheet: str):
    ws = connect_to_spreadsheet(spreadsheet, worksheet)
    # There are 6 columns to care about and store
    cu_rel = CU_Relations(ws.col_values(1), ws.col_values(2), ws.col_values(
        3), ws.col_values(4), ws.col_values(5), ws.col_values(6))
    cu_rel.cus = cu_rel.cus[1:-1]
    cu_rel.necessary = cu_rel.necessary[1:-1]
    cu_rel.useful = cu_rel.useful[1:-1]
    cu_rel.generalize = cu_rel.generalize[1:-1]
    cu_rel.synonym = cu_rel.synonym[1:-1]
    cu_rel.dlc = cu_rel.dlc[1:-1]
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


def connect_to_CU_database():
    basedir = Path().absolute()
    data_json = basedir / "faceit-concur" / "backend" / \
        "graph" / "services" / "client_secret.json"
    scope = ['https://spreadsheets.google.com/feeds',
             'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name(data_json, scope)
    return gspread.authorize(creds)


def delete_CU_file(CU_name) -> None:
    client = connect_to_CU_database()

    for spreadsheet in client.list_spreadsheet_files():
        if spreadsheet['name'] == CU_name:
            client.del_spreadsheet(spreadsheet['id'])


def get_available_CU_files() -> list:
    client = connect_to_CU_database()
    spreadsheets_json_files = client.list_spreadsheet_files()
    spreadsheet_list = []
    for sheet in spreadsheets_json_files:
        # TODO: Ensure that "LA list with categories" and "list of knowledge contents"
        if sheet["id"] != '1ZTHiio5bn6PcVHZqALLdJgJlestfXfcZluF0QqCkEWA' and sheet["id"] != '1VMea_KUaqwY2bHJylP3NjdPenekWuzkaK_iXD7hxFTQ':
            spreadsheet_list.append(sheet["name"])

    return spreadsheet_list


def upload_CU_file(file) -> None:

    client = connect_to_CU_database()

    data_excel = file
    delete_CU_file(file.filename[:-5])
    onlineSheet = client.create(file.filename[:-5])

    excelFile = pd.ExcelFile(data_excel, engine='openpyxl')
    for name_of_sheet in excelFile.sheet_names:
        dataframe = excelFile.parse(name_of_sheet)
        worksheet = onlineSheet.add_worksheet(title=name_of_sheet, rows=str(
            dataframe.shape[0]), cols=str(dataframe.shape[1]))
        print("Created a worksheet:", name_of_sheet)
        print("Shape:", dataframe.shape[0], dataframe.shape[1])
        dataframe.fillna('', inplace=True)
        worksheet.update([dataframe.columns.values.tolist()
                          ] + dataframe.values.tolist())
        # print(worksheet.get_all_values())

    print("Upload complete")


def delete_all_files():
    client = connect_to_CU_database()
    # delete_CU_file("temp")
