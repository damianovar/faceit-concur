from typing import *
import numpy as np
from math import *

from backend.models.models import Connection, Course, User


def init_matrix(size):
    """Initialize

    size is number of content units
    """

    matrix = np.full((size, size), -1)
    np.fill_diagonal(matrix, 0)

    return matrix


def reshape_for_db(matrix):
    """Reshape current matrix with one that better suits the need of the database."""
    matrix = matrix.reshape(-1)
    return matrix.tolist()


def reshape_for_modification(matrix):
    size = int(sqrt(len(matrix)))
    new_matrix = np.array(matrix)
    new_matrix = new_matrix.reshape(size, size)
    return new_matrix


def get_matrix(user, course, size=None, semester="V21"):
    for elements in Connection.objects(user=user, course=course):
        return reshape_for_modification(np.fromiter(elements.kc_matrix, float))
    return init_matrix(size)
