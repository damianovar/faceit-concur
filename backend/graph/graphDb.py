from ..models.models import Course, Institution, User, CU
from flask import session

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
    else:
        print("Graph is empty")
    

def create_course(course_name, course_code, course_institution, relationship_graph, hierarchy_graph):
    creator = User.objects(email="iverau@stud.ntnu.no").first()
    taught_cus_list = [CU.objects(name="time constant").first()]
    prerequisite_cus_list = [CU.objects(name="time constant").first()]
    Course(name=course_name, creator=creator, course_code=course_code, institution=course_institution, relations_graph=relationship_graph, prerequisite_cus_list=prerequisite_cus_list, taught_cus_list=taught_cus_list).save()

def delete_graph(graph_id):
    raise NotImplementedError

