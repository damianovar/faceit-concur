from ..models.models import Course

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
    


def delete_graph(graph_id):
    raise NotImplementedError
