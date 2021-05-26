from ..models.models import Course, Institution, User, CU
from flask import session
from .cu_rel import CU_Relations
import pandas as pd

def get_course_names_and_id():
    course_names = []
    course_ids = []
    for course in Course.objects():
        if course:
            course_names.append(course.name)
            course_ids.append(course.id)

    return course_names, course_ids

def get_graph_from_id(id, graph_type):
    if graph_type == "hierarchies":
        return Course.objects(id=id).first().hierarchies_graph
    elif graph_type == "relations":
        return Course.objects(id=id).first().relations_graph
    

def insert_graph_into_course(graph_dict, graph_type, course_id):
    if graph_dict:
        course_obj = Course.objects(id = str(course_id)).first()
        if graph_type == "hierarchies":
            course_obj.hierarchies_graph = graph_dict
        elif graph_type == "relations":
            course_obj.relations_graph = graph_dict
        course_obj.save()

    

def create_course(course_name, course_code, course_institution, relationship_graph, hierarchy_graph):
    creator = User.objects(email="iverau@stud.ntnu.no").first()
    taught_cus_list = [CU.objects(name="time constant").first()]
    prerequisite_cus_list = [CU.objects(name="time constant").first()]
    Course(name=course_name, creator=creator, course_code=course_code, institution=course_institution, relations_graph=relationship_graph, hierarchies_graph=hierarchy_graph, prerequisite_cus_list=prerequisite_cus_list, taught_cus_list=taught_cus_list).save()

def delete_course(id):
    Course.objects(id=id).delete()


def extract_CU_file(file) -> None:
    excelFile = pd.ExcelFile(file, engine='openpyxl')

    relationDataframe = excelFile.parse("content units relations")
    hierarchiesDataframe = excelFile.parse("content units hierarchies")
    
    hiearchy_list = read_cu_hierarchies(hierarchiesDataframe)
    relation_cu = read_cu_realtions(relationDataframe)
    return relation_cu, hiearchy_list

def read_cu_realtions(relationDataframe):
    relationDataframe.fillna('', inplace=True)
    cu_rel_names = ['Content Unit (CU)','which other CUs are necessary for the CU in column A?', 'which other CUs are useful for the CU in column A?', 'which CUs contain / generalize the CU in column A?', 'which CUs are a synonym of the CU in column A?', 'which CUs are directly logically connected to the CU in column A?']
    cu_rel = CU_Relations(relationDataframe[cu_rel_names[0]].tolist(), relationDataframe[cu_rel_names[1]].tolist(), relationDataframe[cu_rel_names[2]].tolist(), relationDataframe[cu_rel_names[3]].tolist(), relationDataframe[cu_rel_names[4]].tolist(), relationDataframe[cu_rel_names[5]].tolist())
    return cu_rel

def read_cu_hierarchies(hierarchiesDataframe):
    hierarchiesDataframe.fillna('', inplace=True)

    column_names = hierarchiesDataframe.columns
    
    # Find amount of rows in document
    largest_row = 0
    for index in range(hierarchiesDataframe.shape[0]):
        if all(x == '' for x in hierarchiesDataframe.iloc[index]):
            largest_row = index
            break

    # Save all the relevant columns 
    topic_cols = []
    for name in column_names:
        col = hierarchiesDataframe[name].tolist()[:largest_row]
        if all(x=='' for x in col):
            break
        topic_cols.append([name, *col])

    return topic_cols
