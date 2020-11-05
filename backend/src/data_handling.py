# data_handling.py
"""
This file contains methods that processes data from the database and makes it useable for mapping
"""
import numpy as np


def get_kc_mapping_average(kc_matrices):
    """
    Gets average result of kc matrices for professor to use
    :param kc_matrices: Numpy array, list of all kc matrices for a given course
    :return:

    >>> input: [[[0.1 0.2] [0.0 0.1]] [[0.0 0.0] [0.0 0.0]]]
    >>> output: [[0 0.5] [1 0]]
    """
    l, n, _ = kc_matrices.shape
    average_kc_matrix = np.zeroes(shape=(n, n), dtype='float16')

    for matrix in kc_matrices:
        average_kc_matrix += matrix.astype(float)

    average_kc_matrix /= l  #
    return average_kc_matrix

    # TODO: in the map_kcs function, let teacher decide treshholds, colors of edges based of weight and so on
    # This can easily be done via numpy. filedata > treshhold (file > 50)
