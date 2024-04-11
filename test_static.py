import matplotlib.pyplot as plt
import matplotlib.cm as cm
from netsim_utils import *


def static_sim(p: float, T_max: np.float64):
    stats = []
    s_G = gen_graph()
    _N = gen_matx(MAX_PCK_NO, N_NODES)
    pos = nx.spring_layout(s_G)
    reset_flows(s_G)
    set_flows(s_G, _N)
    set_caps(s_G)
    for epoch in range(N_TESTCASES):
        stat: int = 1
        it_ctr: int = 1
        broken = False
        overloaded = False
        _G = s_G.copy()
        _N = gen_matx(MAX_PCK_NO, N_NODES)
        print("Macierz przepływów: \n", _N)
        print("Średnie opóźnienie początkowe: ", T(_G, _N))
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
                # zwiekszaj N i badaj jak sie zmienia niezawodnosc ktorej jeszcze nie mam
                reset_flows(_G)
                set_flows(_G, _N)

            plt.draw()
            plt.pause(TIME_INTERVAL)
        stats.append(stat / it_ctr)

    return np.average(stats)


def vis_p():
    reliabilities = []
    P = np.arange(0.9, 1.0, 0.05)
    for p in P:
        reliabilities.append(static_sim(p=p, T_max=np.float64(0.00165)))
    plt.clf()
    plt.xlabel('p - Prawdopodobieństwo rozspojenia')
    plt.ylabel('Niezawodnosc: P(T<T_max)')
    return P, reliabilities


def vis_Tmax():
    reliabilities = []
    t_maxes = np.arange(0.0001, 0.002, 0.0001)
    for t in t_maxes:
        reliabilities.append(static_sim(p=0.95, T_max=np.float64(t)))
    plt.clf()
    plt.xlabel('T_max')
    plt.ylabel('Niezawodnosc: P(T<T_max)')
    return t_maxes, reliabilities


def main():
    fig = plt.figure()
    fig.canvas.mpl_connect('close_event', on_close)
    plt.clf()
    plt.title("Start symulacji...")
    plt.pause(2)
    arg, reliabilities = vis_Tmax()
    plt.plot(arg, reliabilities)
    plt.show()
    return


if __name__ == "__main__":
    main()
