from typing import Any

import matplotlib.cm as cm
import matplotlib.pyplot as plt

from netsim_utils import *


def inc_topo_sim(p: float, T_max: np.float64):
    stats = []
    n_edges = []
    s_G = gen_graph()
    _N = gen_matx(MAX_PCK_NO, N_NODES)
    pos = nx.spring_layout(s_G)
    reset_flows(s_G)
    set_flows(s_G, _N)
    start_flow = get_avg_flow(s_G)
    set_caps(s_G)
    for _ in range(N_TESTCASES):
        stat: int = 1
        it_ctr: int = 1
        broken = False
        overloaded = False
        _G = s_G.copy()
        testcase_T = T(_G, _N)
        print("Macierz przepływów: \n", _N)
        print("Średnie opóźnienie początkowe (T): ", testcase_T)
        while not broken and not overloaded:
            plt.clf()
            if _G.edges:
                broken, overloaded, s, i = net_status(_G, _N, p, testcase_T)
                stat += s
                it_ctr += i
                _, weights = zip(*nx.get_edge_attributes(_G, "a").items())

                nx.draw(
                    _G,
                    pos,
                    edge_color=weights,
                    edge_cmap=cm.Blues,
                    width=10,
                    with_labels=True,
                    node_color="lightblue",
                    node_size=500,
                    font_size=12,
                    font_weight="bold",
                )

                nx.draw_networkx_edge_labels(
                    _G, pos, font_size=5, font_color="r", bbox={"alpha": 0}
                )

                # zwiekszaj N i badaj jak sie zmienia niezawodnosc
                reset_flows(_G)
                mod_topo(_G, start_flow)
                set_flows(_G, _N)
            plt.pause(TIME_INTERVAL)
            plt.draw()
        stats.append(stat / it_ctr)
        n_edges.append(_G.number_of_edges())

    return np.average(stats), np.average(n_edges)


def vis_inc_nodes():
    reliabilities = []
    iterations = []
    n_edges = []
    for i in range(20):
        r, ed = inc_topo_sim(p=0.95, T_max=np.float64(1))
        iterations.append(i)
        reliabilities.append(r)
        n_edges.append(ed)
    plt.clf()
    plt.xlabel("czas w interwalach")
    plt.ylabel("Niezawodnosc: P(T<T_max), #krawedzi (srednia)")
    return iterations, reliabilities, n_edges


def normalize(l: list[float]):
    return l / np.linalg.norm(l)


def main():
    reliabilities = []
    fig = plt.figure()
    fig.canvas.mpl_connect("close_event", on_close)
    plt.clf()
    plt.title("Start symulacji...")
    plt.pause(2)
    arg, reliabilities, n_edges = vis_inc_nodes()
    reliabilities = normalize(reliabilities)
    n_edges = normalize(n_edges)
    plt.plot(arg, reliabilities, label="norm(P(T < T_max))")
    plt.plot(arg, n_edges, label="norm(avg(#krawedzi))")
    plt.show()


if __name__ == "__main__":
    main()
