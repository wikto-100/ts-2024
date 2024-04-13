import re
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from netsim_utils import *


def inc_n_sim(p: float, T_max: np.float64, s_N: np.array):
    stats = []
    stats_N = []
    s_G = gen_graph()
    pos = nx.spring_layout(s_G)
    reset_flows(s_G)
    set_flows(s_G, s_N)
    set_caps(s_G)
    for _ in range(N_TESTCASES):
        stat: int = 1
        it_ctr: int = 1
        broken = False
        overloaded = False
        _G = s_G.copy()
        _N = np.array(s_N, copy=True)
        testcase_T = T(_G, _N)
        print("Macierz przepływów: \n", _N)
        print("Średnie opóźnienie początkowe: ", testcase_T)
        while not broken and not overloaded:
            plt.clf()
            if _G.edges:
                broken, overloaded, s, i = net_status(_G, _N, p,testcase_T)
                stat += s
                it_ctr += i
                _, weights = zip(*nx.get_edge_attributes(_G, 'a').items())
                nx.draw(_G, pos, edge_color=weights, edge_cmap=cm.Blues, width=10, with_labels=True,
                        node_color='lightblue',
                        node_size=500, font_size=12, font_weight='bold')
                nx.draw_networkx_edge_labels(_G, pos, font_size=5, font_color='r', bbox={"alpha": 0})
                # zwiekszaj N i badaj jak sie zmienia niezawodnosc
                reset_flows(_G)
                _N = incr_matx(_N)
                set_flows(_G, _N)
            plt.pause(TIME_INTERVAL)
            plt.draw()
        stats.append(stat / it_ctr)
        stats_N.append(np.average(_N))
    return np.average(stats), np.average(stats_N)


def vis_inc_N():
    reliabilities = []
    avg_N = []
    iterations = []
    s_N = gen_matx(MAX_PCK_NO, N_NODES)
    for i in range(100):
        (r, mn) = inc_n_sim(p=0.95, T_max=np.float64(1), s_N=s_N)
        reliabilities.append(r)
        avg_N.append(mn)
        iterations.append(i)
    plt.clf()
    plt.xlabel('czas w interwalach')
    plt.ylabel('norm(P(T<T_max)), norm(avg(N))')
    return iterations, reliabilities, avg_N

def normalize(l: list[float]):
    return l/np.linalg.norm(l)

def main():
    fig = plt.figure()
    fig.canvas.mpl_connect('close_event', on_close)
    plt.clf()
    plt.title("Start symulacji...")
    plt.pause(2)
    arg, reliabilities, avg_N = vis_inc_N()
    reliabilities = normalize(reliabilities)
    avg_N = normalize(avg_N)
    plt.plot(arg, reliabilities, label="norm(P(T < T_max))")
    plt.plot(arg, avg_N, label="norm(avg(N))")
    plt.legend()
    plt.show()
    return


if __name__ == "__main__":
    main()
