import networkx as nx
import numpy as np
from math import log10
from random import choice
from config import *


def gen_graph():
    g = nx.Graph()
    nodes = [i for i in range(1, 21)]
    edges = []
    for i in range(1, 5):
        edges.append((i, (i % 4) + 1))
    for i in range(5, 14, 4):
        edges.append((i, i + 1))
        edges.append((i, i + 2))
        edges.append((i, i + 3))
    edges += [z for z in zip([1, 2, 3, 4], [20, 19, 18, 17])]
    edges += [z for z in zip([17, 18, 19], [5, 9, 13])]
    assert len(edges) < 30
    assert len(nodes) == 20
    g.add_nodes_from(nodes)
    g.add_edges_from(edges)
    return g


def mod_topo(G: nx.Graph, avg_flow: float):
    failsafe: int = 0
    while True:
        failsafe += 1
        if failsafe >= 10000:
            break
        # Select two random nodes
        u = choice(list(G.nodes))
        v = choice(list(G.nodes))
        # Check if edge already exists
        if not G.has_edge(u, v) and not u == v:
            # Add the edge if it doesn't exist
            G.add_edge(u, v)
            G[u][v]['a'] = avg_flow
            G[u][v]['c'] = cap5x_b(avg_flow)
            break
    return


def gen_matx(pck_max: int, s: int):
    n = np.random.randint(pck_max, size=(s, s))
    np.fill_diagonal(n, 0)
    return n


def incr_matx(N: np.array):
    return N + np.random.randint(MAX_PCK_NO, size=N.shape)


def cap5x_b(val):
    # Ograniczenie górne na sumaryczny rozmiar pakietów przechodzący przez łącze
    # w 1s. Stanowi 5-krotność sufitu rzędu 10 s. r. pakietów
    pow_10 = 10 ** int(log10(val))
    return np.uint64(((pow_10 * (val // pow_10)) + pow_10)) * np.uint64(5 * MAX_PCK_SIZE)


def set_caps(G: nx.Graph):
    flows = nx.get_edge_attributes(G, 'a')
    if flows:
        caps = {key: cap5x_b(val) for key, val in flows.items()}
        nx.set_edge_attributes(G, caps, 'c')
    return


def incr_caps(G: nx.Graph):
    new_caps = nx.get_edge_attributes(G, 'c')
    new_caps = {key: 1000 + val for key, val in new_caps.items()}
    nx.set_edge_attributes(G, new_caps, 'c')
    return


def reset_flows(G: nx.Graph):
    nx.set_edge_attributes(G, 0, 'a')


def set_flows(G: nx.Graph, N: np.array):
    n_nodes = G.number_of_nodes()
    for i in range(1, n_nodes + 1):
        for j in range(1, n_nodes + 1):
            if i != j:
                if nx.has_path(G, i, j):
                    path = nx.shortest_path(G, i, j)
                    # print("Propagacja {:d} --> {:d}: {}".format(i, j, path))
                    for _ in range(len(path) - 1):
                        u, v = path[_], path[_ + 1]
                        G[u][v]['a'] += N[i - 1][j - 1]
    return


def get_avg_flow(G: nx.Graph):
    attr = nx.get_edge_attributes(G, 'a')
    s = np.int64(sum([np.int64(attr[e]) for e in G.edges]))
    return s / G.number_of_edges()


def get_avg_cap(G: nx.Graph):
    attr = nx.get_edge_attributes(G, 'c')
    s = np.int64(sum([np.int64(attr[e]) for e in G.edges]))
    return s / G.number_of_edges()


def T(G: nx.Graph, N: np.array):
    s: np.int64 = np.sum(N)
    t: np.float64 = np.float64(0)
    m = AVG_PCK_SIZE
    for e in G.edges:
        a_e = G[e[0]][e[1]]['a']
        c_e = G[e[0]][e[1]]['c']
        div = (c_e / m) - a_e
        if div != 0:
            t += a_e / div
        else:
            t += 0
    return np.float64(t / s)


def net_status(G: nx.Graph, N: np.array, p: float, T_max: np.float64):
    # pr. ze T < T_max?
    # p = pr. że każda krawędź nie uszkodzona
    # dla kazdej krawedzi z pr. 1-p zerwij ja
    # po zerwaniu jakiejs krawedzi, przelicz T() ponownie
    # i porownaj z Tmax
    broken = False
    overloaded = False
    stat = 0
    it = 1
    t_s: np.float64 = np.float64(0)
    br_edge = choice(list(G.edges))
    if np.random.uniform(0, 1) > p:
        G.remove_edge(br_edge[0], br_edge[1])
        broken = True
        it = 0
    else:
        # ujemne t_s znaczy ze jest przeciążenie na jakiejś gałęzi
        t_s = T(G, N)  # T sie zwiekszy dla wiekszych wart. 'a'
        if t_s < 0:
            overloaded = True
            it = 0
        elif t_s < T_max:
            stat = 1
    print("T: ", t_s)
    return broken, overloaded, stat, it


def on_close(event):
    exit("USER_EXIT")
