"""A game where one match """
from pyvis.network import Network
import matplotlib.pyplot as plt
import numpy as np
import random as rnd
from graphviz import Digraph
from .cu_rel import CU_Relations
import json
from itertools import zip_longest


def get_nodes_and_edges_cu_relations(CU_REL):
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

    cus, necessary, useful, generalize, synonym, dlc = CU_REL.cus, CU_REL.necessary, CU_REL.useful, CU_REL.generalize, CU_REL.synonym, CU_REL.dlc

    for cu, nec, usef, gen, syn, dlc in zip_longest(cus, necessary, useful, generalize, synonym, dlc):
        cu = cu.split("(")[0].strip().lower()
        if nec:
            nec = remove_text_inside_parantheses(nec).split(",")
            for n in nec:
                n = n.strip().lower()
                g.add_node(n)
                g.add_edge(n, cu)
        if usef:
            usef = remove_text_inside_parantheses(usef).split(",")
            for u in usef:
                u = u.strip().lower()
                g.add_node(u)
                g.add_edge(u, cu)
        if gen:
            gen = remove_text_inside_parantheses(gen).split(",")
            for ge in gen:
                ge = ge.strip().lower()
                g.add_node(ge)
                g.add_edge(ge, cu)
        if syn:
            syn = remove_text_inside_parantheses(syn).split(",")
            for sy in syn:
                sy = sy.strip().lower()
                g.add_node(sy)
                g.add_edge(sy, cu)
        if dlc:
            dlc = remove_text_inside_parantheses(dlc).split(",")
            for dl in dlc:
                dl = dl.strip().lower()
                g.add_node(dl)
                g.add_edge(dl, cu)

    for iterate, node in enumerate(g.get_nodes()):
        length = len(g.neighbors(node))
        if length == 0:
            g.nodes[iterate]['color'] = "#829FD9"
        if length == 1:
            g.nodes[iterate]['color'] = "#027368"
        if length == 2:
            g.nodes[iterate]['color'] = "#BABF2A"
        if length > 3:
            g.nodes[iterate]['color'] = "#735702"
        print(length)
    #print("Done rumbeling")
    node, edge, _, _, _ = g.get_network_data()
    #print("Nodes:", node)
    #print("Edges:", edge)

    print("Setup for a test", remove_text_inside_parantheses(
        "ODEs (e2), linearity (e2, u1), time invariance (e2, u1), causality (e2)"))
    # g.show('cu_relations.html')
    return json.dumps(node), json.dumps(edge)


def remove_text_inside_parantheses(text):
    result = ""
    add_letter = True
    for char in text:
        if char == "(":
            add_letter = False

        if add_letter:
            result += char
        if char == ")":
            add_letter = True
    return result


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
    g.add_node(n_id="Linear Algebra", label="Linear Algebra",
               color="FF0000", shape="ellipse", value=6)

    for elem in trans_mat:
        c += 1
        if c != 1 and c != col_size:
            # TODO: Make this into a better algorithm
            # Algorithm for determening parents and all that kind of good jazz
            if elem[0] and not (elem[1] or elem[2] or elem[3]):
                p0 = elem[0]
                g.add_node(n_id=p0, label=p0, color="#735702",
                           shape="ellipse", value=4)
                g.add_edge("Linear Algebra", p0)
            elif elem[1] and not (elem[0] or elem[2] or elem[3]):
                p1 = elem[1]
                g.add_node(n_id=p1, label=p1, color="#BABF2A",
                           shape="ellipse", value=3)
                g.add_edge(p0, elem[1])
            elif elem[2] and not (elem[1] or elem[0] or elem[3]):
                p2 = elem[2]
                g.add_node(n_id=p2, label=p2, color="#027368",
                           shape="ellipse", value=2)
                g.add_edge(p1, elem[2])
            elif elem[3] and not (elem[1] or elem[2] or elem[0]):
                g.add_node(n_id=elem[3], label=elem[3],
                           color="#829FD9", shape="ellipse", value=1)
                g.add_edge(p2, elem[3])

    node, edge, _, _, _ = g.get_network_data()

    return json.dumps(node), json.dumps(edge)
