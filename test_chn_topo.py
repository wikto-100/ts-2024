import matplotlib.pyplot as plt
import matplotlib.cm as cm
from netsim_utils import *


def inc_topo_sim(p: float, T_max: np.float64):
    stats = []
    stat_edges = []
    s_G = gen_graph()
    _N = gen_matx(MAX_PCK_NO, N_NODES)
    pos = nx.spring_layout(s_G)
    reset_flows(s_G)
    set_flows(s_G, _N)
    start_flow = get_avg_flow(s_G)
    set_caps(s_G)
    for epoch in range(N_TESTCASES):
        stat: int = 1
        it_ctr: int = 1
        broken = False
        overloaded = False
        _G = s_G.copy()
        print("Macierz przepływów: \n", _N)
        print("Średnie opóźnienie początkowe (T): ", T(_G, _N))
        while not broken and not overloaded:
            plt.clf()
            if _G.edges:
                broken, overloaded, s, i = net_status(_G, _N, p, T_max)
                stat += s
                it_ctr += i
                edges, weights = zip(*nx.get_edge_attributes(_G, 'a').items())

                nx.draw(_G, pos, edge_color=weights, edge_cmap=cm.Blues, width=10, with_labels=True,
                        node_color='lightblue',
                        node_size=500, font_size=12, font_weight='bold')

                nx.draw_networkx_edge_labels(_G, pos, font_size=5, font_color='r', bbox=dict(alpha=0))

                # zwiekszaj N i badaj jak sie zmienia niezawodnosc
                reset_flows(_G)
                mod_topo(_G, start_flow)
                set_flows(_G, _N)
            plt.pause(TIME_INTERVAL)
            plt.draw()
        stats.append(stat/it_ctr)
        stat_edges.append(_G.number_of_edges())

    return np.average(stat_edges),np.average(stats)

def vis_inc_nodes():
    reliabilities = []
    n_edges = []
    for i in range(10):
        cnt, r = inc_topo_sim(p=0.95, T_max=np.float64(0.00157))
        n_edges.append(cnt)
        reliabilities.append(r)
    plt.clf()
    plt.xlabel('srednia l. krawedzi')
    plt.ylabel('Niezawodnosc: P(T<T_max)')
    return sorted(n_edges), reliabilities
def main():
    reliabilities = []
    fig = plt.figure()
    fig.canvas.mpl_connect('close_event', on_close)
    plt.clf()
    plt.title("Start symulacji...")
    plt.pause(2)
    arg, reliabilities = vis_inc_nodes()
    plt.plot(arg, reliabilities)
    plt.show()
    return


if __name__ == "__main__":
    main()
