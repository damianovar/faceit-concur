"""A game where one match """
from pyvis.network import Network
import matplotlib.pyplot as plt
import numpy as np
import random as rnd
from graphviz import Digraph
from .cu_rel import CU_Relations
import json

#############
# CONSTANTS #
#############

#  ALPHABET = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
QUESTIONS = []  # TODO: Fill with start of a question
MIDDLE_PART = []  # TODO: Fill with middle part of a question


def map_algs(g, alg="barnes"):
    """

    :param g: Graph, network
    :param alg: string, algorithm chosen to visualize nodes and edges
    """
    if alg == "barnes":
        g.barnes_hut()
    elif alg == "forced":
        g.force_atlas_2based()
    elif alg == "hr":
        g.hrepulsion()
    else:
        print("Please choose a valid algorithm.")

# TODO: Check if these mapping functions are necessary


def map_smoothenes(graph, smooth):
    """

    :param graph: object, graph we want to map to
    :param smooth: string, how the edges should be smoothened
    :return:
    """
    if smooth.lower() == "dynamic":
        graph.set_edge_smooth("dynamic")
    elif smooth.lower() == "discrete":
        graph.set_edge_smooth("discrete")
    elif smooth.lower() == "diagonalcross":
        graph.set_edge_smooth("diagonalCross")
    elif smooth.lower() == "straightcross":
        graph.set_edge_smooth("straightCross")
    elif smooth.lower() == "horizontal":
        graph.set_edge_smooth("horizontal")
    elif smooth.lower() == "vertical":
        graph.set_edge_smooth("vertical")
    elif smooth.lower() == "curvedcw":
        graph.set_edge_smooth("curvedCW")
    elif smooth.lower() == "curvedccw":
        graph.set_edge_smooth("curwedCCW")
    elif smooth.lower() == "cubicbezier":
        graph.set_edge_smooth("cubicBezier")


def get_prerequisite_nodes(graph, node):
    """
    DFS search which nodes you need to learn a certain KC
    :param graph: obj, graph we are looking into
    :param node: obj, node we want to study
    :return: string
    """
    raise NotImplementedError


def kc_mapping(connection, restart, course):
    """

    :param connection:
    :param new: boolean, is this a new map or not
    :return: tuple(2D list, float): kc matrix and percentage done
    """
    #kc_list = [kc.name for kc in connection.kc_list]
    kc_list = course.kcs

    kc_matrix = connection.kc_matrix
    percentage = connection.percentage

    n = len(kc_matrix)
    tot_size = n * n

    if restart:
        kc_matrix = [[0.0 for i in range(n)] for j in range(n)]
        percentage = 0.0
        r, c = 0, 0

    else:
        # Find starting cell in matrix
        cell_start = int(percentage * tot_size)
        r = int(cell_start / n)  # row start
        c = cell_start - r

    q1 = "How important is "
    q2 = " for learning "
    qinfo = "(Over 5: important, Over 7: necessary, over 9: directly logically connected) "
    # Synonym
    qi1 = "Is "
    qi2 = " a synonom of "

    print("P.S: Answer these questions on a scale from 1-10 where 1 is the lowest value and 10 is the highest value")
    print("Enter -1 if you don't know, or press anything else to exit")

    # To loop through reminder of a row
    if c != 0:
        for k, dest in enumerate(kc_list[c:], start=c):
            src = kc_list[r]
            ask_questions(r, k, src, dest, kc_matrix, n, (q1, q2))
        r += 1  # To start from the next row

    # Start form next row and then iterate through rest of
    for i, src in enumerate(kc_list[r:], start=r):
        for j, dest in enumerate(kc_list):
            ask_questions(i, j, src, dest, kc_matrix, n, (q1, q2))

    return kc_matrix, 1.00


def get_questions(filename):
    """
    Reads every single line of a textfile as if they all were questions
    :param filename:
    :return:
    """
    try:
        with open(filename, 'r') as f:
            return f.readlines()
    except FileNotFoundError as e:
        print(f"Error: {e}")


def ask_questions(i, j, src, dest, kc_matrix, n, questions):
    acceptable_answers = [i for i in range(-1, 11)]

    q1, q2 = questions  # need questions to be a list or something, use get_questions
    if src != dest:
        print(
            "P.S: Answer these questions on a scale from 1-10 where 1 is the lowest value and 10 is the highest value")
        print("Enter -1 if you don't know, or press anything else to exit")
        inp = input(q1 + " " + src.name + " " + q2 + " " + dest.name).upper()

        if inp == "E" or inp == "EXIT":
            percentage = round(float((i + 1) * (j + 1) / n ** 2) * 100, 2)
            print(f"You are {percentage * 100}% done with the mapping")
            return kc_matrix, percentage

        while float(inp) not in acceptable_answers:
            print("Please enter a valid value!")
            inp = input(q1 + " " + src.name + " " +
                        q2 + " " + dest.name).upper()

        if 0 <= float(inp) <= 10:
            kc_matrix[i][j] = (float(inp) / 10)

        elif float(inp) == -1:  # Don't know
            kc_matrix[i][j] = -1

    percentage = round(float((i + 1) * (j + 1) / n**2) * 100, 2)
    print(f"Current progress: {percentage}%")


def map_cu_relations(CU_REL):
    """
    1: Go through spreadsheet, add every single one of the kcs in first column to kcs in database
    2: Map along with the others 
    3: Store this map as a connection
    """
    g = Network(height="1500px", width="75%", bgcolor="#222222",
                font_color="white", directed=True)

    # if buttons:
    g.width = "75%"
    # nodes, layout, interaction, selection, renderer, physics
    g.show_buttons(filter_=["edges", "physics"])


    for cu in CU_REL.cus:
        cu = cu.split("(")[0].strip().lower()
        g.add_node(n_id=cu, label=cu, shape='ellipse')

    cus, necessary, useful, generalize, synonym, dlc = CU_REL.cus, CU_REL.necessary, CU_REL.generalize, CU_REL.synonym, CU_REL.dlc
    for cu, nec, usef, gen, syn, dlc in zip(cus, necessary, useful, generalize, synonym, dlc):

        if nec:
            nec = nec.split("(")[0].strip().lower()
            g.add_edge(nec, cu)
        if usef:
            usef = usef.split("(")[0].strip().lower()
            g.add_edge(usef, cu)
        if gen:
            gen = gen.split("(")[0].strip().lower()
            g.add_edge(gen, cu)
        if syn:
            syn = syn.split("(")[0].strip().lower()
            g.add_edge(syn, cu)
        if dlc:
            dlc = dlc.split("(")[0].strip().lower()
            g.add_edge(dlc, cu)

    g.show('cu_relations.html')


def map_kcs(
        kc_list,
        kc_matrix,
        node_color="#8B008B",
        edge_color="#03DAC6",
        node_shape="ellipse",
        alg="barnes",
        edge_smooth=None,
        buttons=False,
        treshold=0.5):
    """
    Use this on  a test that has less than 26 KCs, or else there will be problems with
    relations between the edges due to name conflict

    :param threshold: float,
    :param kc_list: np.array, list of all kcs
    :param edge_smooth: string, How the user wants the edges to be, default is continuous
    :param buttons: bool, buttons to edit graph with
    :param node_shape: string, shape of node
    :param edge_color: string, shape of edge
    :param node_color: string, hexvalue of color for node
    :param kc_matrix: 2D np array, mapping of kcs
    :param alg: string, algorithm for graph
    :return: renders a graph in which you can see the relations between nodes and their edges

    """
    g = Network(height="1500px", width="75%", bgcolor="#222222",
                font_color="white", directed=True)

    # if buttons:
    g.width = "75%"
    # nodes, layout, interaction, selection, renderer, physics
    g.show_buttons(filter_=["edges", "physics"])

    # Create the nodes
    for kc_node in kc_list:
        g.add_node(n_id=kc_node, label=kc_node,
                   color=node_color, shape=node_shape)

    # Creates edges between nodes if they're connected (if the value is true in the database)
    n = len(kc_matrix)
    for r in range(n):
        for c in range(n):
            if r != c:
                # Directly logically connnected edge
                if 0.9 <= kc_matrix[r, c] <= 1.0:
                    g.add_edge(kc_list[r], kc_list[c],
                               color="#42cc14")  # green
                # Necessary edge
                elif 0.7 <= kc_matrix[r, c] < 0.9:
                    g.add_edge(kc_list[r], kc_list[c],
                               color="#ff8c00")  # orange
                # Important edge
                elif 0.5 <= kc_matrix[r, c] < 0.7:
                    g.add_edge(kc_list[r], kc_list[c],
                               color="#ffd900")  # orange
                elif kc_matrix[r, c] == -1.0:
                    g.add_edge(kc_list[r], kc_list[c],
                               color="#56f0eb")

    map_algs(g, alg)

    if edge_smooth is not None:
        map_smoothenes(graph=g, smooth=edge_smooth)

    node_list = g.get_nodes()
    for node in g.nodes:
        neighbors = g.neighbors(node_list[node_list.index(node['id'])])
        if neighbors is None:
            title = "Endpoint KC"
        else:
            title = "What to learn next:<br>"
            for neighbor in neighbors:
                title += f"{neighbor}<br>"
        node["title"] = title

    # g.save_graph("../../kc.html")
    g.show("kc_map.html")


#######################
#   KC CATEGORIES     #
#######################

# Todo: find out if we'll actually end up using this
def map_kc_categories(kcs, positions):
    """
    Map Kcs based on categories
    COURSE - MAIN TOPICS - CATEGORIES - OPERATIONS

    This function requires a list of kcs and a list of positions as well as they have to be of same size

    :param kcs: List, list of kcs
    :param positions: List, list of position/indention level of a kc in the tree
    :return: None
    """
    g = Digraph('G', filename='categories.gv', format='pdf',
                node_attr={'color': 'lightblue2', 'style': 'filled'})
    g.attr(size='6,6')

    if len(kcs) != len(positions):
        print("Sorry, Not every kc in the list has a corresponding position")
        return

    for kc, pos in zip(kcs, positions):
        if pos.count('.'):

            # get all levels until the last one and select this kc, this is the parent
            last_dot = len(pos) - pos[::-1].index('.') - 1
            parent_pos = pos[:last_dot]

            # Check whether or not a kc has a parent
            if positions.count(parent_pos):
                parent_kc = positions.index(parent_pos)
                g.edge(kcs[parent_kc], kc)

    g.render('categories.gv', view=True)


def get_nodes_and_edges_cu_hierarchies(lists):
    """
    Left right mapping of indented category mapping
    :param lists:
    :return:
    """
    trans_mat = tuple(zip(*lists))
    col_size = len(trans_mat)
    num_of_cols = len(trans_mat[0])

    g = Network(height="1500px", width="75%", bgcolor="#222222",
                font_color="white", directed=True)

    # if buttons:
    g.width = "75%"
    # nodes, layout, interaction, selection, renderer, physics
    g.show_buttons(filter_=["edges", "physics"])

    c = 0
    p0, p1, p2 = None, None, None
    color = "#FFFFFF"
    g.add_node(n_id="Linear Algebra", label="Linear Algebra", color="FF0000", shape="ellipse", value=6)

    for elem in trans_mat:
        c += 1
        if c != 1 and c != col_size:
            # TODO: Make this into a better algorithm
            # Algorithm for determening parents and all that kind of good jazz
            if elem[0] and not (elem[1] or elem[2] or elem[3]):
                p0 = elem[0]
                g.add_node(n_id=p0, label=p0, color="#735702", shape="ellipse", value=4)
                g.add_edge("Linear Algebra", p0)
            elif elem[1] and not (elem[0] or elem[2] or elem[3]):
                p1 = elem[1]
                g.add_node(n_id=p1, label=p1, color="#BABF2A", shape="ellipse", value=3)
                g.add_edge(p0, elem[1])
            elif elem[2] and not (elem[1] or elem[0] or elem[3]):
                p2 = elem[2]
                g.add_node(n_id=p2, label=p2, color="#027368", shape="ellipse", value=2)
                g.add_edge(p1, elem[2])
            elif elem[3] and not (elem[1] or elem[2] or elem[0]):
                g.add_node(n_id=elem[3], label=elem[3], color="#829FD9", shape="ellipse", value=1)
                g.add_edge(p2, elem[3])

    node, edge, _, _, _ = g.get_network_data()

    return json.dumps(node), json.dumps(edge)

def map_cu_hierarchies(lists):
    """
    Left right mapping of indented category mapping
    :param lists:
    :return:
    """
    trans_mat = tuple(zip(*lists))
    col_size = len(trans_mat)
    num_of_cols = len(trans_mat[0])

    g = Network(height="1500px", width="75%", bgcolor="#222222",
                font_color="white", directed=True)

    # if buttons:
    g.width = "75%"
    # nodes, layout, interaction, selection, renderer, physics
    g.show_buttons(filter_=["edges", "physics"])

    c = 0
    p0, p1, p2 = None, None, None
    color = "#FFFFFF"
    g.add_node(n_id="Linear Algebra", label="Linear Algebra", color="FF0000", shape="ellipse", value=6)

    for elem in trans_mat:
        c += 1
        if c != 1 and c != col_size:
            # TODO: Make this into a better algorithm
            # Algorithm for determening parents and all that kind of good jazz
            if elem[0] and not (elem[1] or elem[2] or elem[3]):
                p0 = elem[0]
                g.add_node(n_id=p0, label=p0, color="#735702", shape="ellipse", value=4)
                g.add_edge("Linear Algebra", p0)
            elif elem[1] and not (elem[0] or elem[2] or elem[3]):
                p1 = elem[1]
                g.add_node(n_id=p1, label=p1, color="#BABF2A", shape="ellipse", value=3)
                g.add_edge(p0, elem[1])
            elif elem[2] and not (elem[1] or elem[0] or elem[3]):
                p2 = elem[2]
                g.add_node(n_id=p2, label=p2, color="#027368", shape="ellipse", value=2)
                g.add_edge(p1, elem[2])
            elif elem[3] and not (elem[1] or elem[2] or elem[0]):
                g.add_node(n_id=elem[3], label=elem[3], color="#829FD9", shape="ellipse", value=1)
                g.add_edge(p2, elem[3])

    print(g.get_network_data()[0])
    g.show("cu_hierarchy.html")




##########################
#   MATPLOTLIB CHARTS    #
##########################


def draw_graph_for_kc(kcs, row_values, kc, course, code):
    """

    :param kcs: kcs for x axis
    :param row_values: which row to look at
    :param kc: to know which kc we are mapping from
    :param course: name of course
    :param code: coursecode
    :return:
    """

    ind = kcs.index(kc)  # Finds index of kc we want to map from
    kcs.remove(kc)
    # Removes label of kc since we don't need this either
    x_axis = np.array(kcs)
    # Removes this item since it's useless in graph
    row_values = np.delete(row_values, ind)

    fig, ax = plt.subplots()

    ax.bar(x_axis, row_values)
    ax.set_ylabel('Probability')
    ax.set_title(
        f'Probability for {kc} connection to other KCs\n {code} - {course}')

    plt.show()


def draw_cumulative_graph(kc_matrix, kc, course, code):
    """
    Draws
    :param code:
    :param course:
    :param kc_matrix:
    :param kc:
    """

    fig, ax = plt.subplots()

    plt.show()
