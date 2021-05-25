from ..models.models import Course

def get_course_names_and_id():
    course_names = []
    course_ids = []
    for course in Course.objects():
        if course:
            course_names.append(course.name)
            course_ids.append(course.id)

    return course_names, course_ids

def get_graph_as_json_from_id():
    raise NotImplementedError

def insert_graph(graph_as_json, graph_type):
    raise NotImplementedError


def delete_graph(graph_id):
    raise NotImplementedError

