import networkx as nx
import matplotlib.pyplot as plt
import os
from analysis.analysis import get_all_sim_info


def get_d_connect(init_persona, G):
    d_connect_list = []
    for edge in G.edges():
        if edge[0] == init_persona.name:
            if G.has_edge(edge[1], init_persona.name):
                d_connect_list.append(edge[1])
    return d_connect_list


class SocialNetworkAnalysis:
    def __init__(self, sim_folder):
        self.sim_folder = sim_folder
        self.sims = get_all_sim_info(sim_folder)

    def draw_social_network(self):
        for sim in self.sims:
            G = sim.G
            plt.figure(figsize=(20, 20))
            pos = nx.spring_layout(G, k=1.5, iterations=150)

            node_sizes, node_colors, node_shapes = self._set_nodes(G, sim.personas)
            edge_colors, edge_styles = self._set_edges(G, sim.personas)

            for i, node in enumerate(G.nodes()):
                nx.draw_networkx_nodes(
                    G,
                    pos,
                    nodelist=[node],
                    node_size=node_sizes[i],
                    node_color=[node_colors[i]],
                    node_shape=node_shapes[i],
                    alpha=0.5,
                )

            for i, (u, v) in enumerate(G.edges()):
                if edge_colors[i] == "red":
                    alpha = 1
                elif edge_colors[i] == "blue":
                    alpha = 0.5
                else:
                    alpha = 0.3
                nx.draw_networkx_edges(
                    G,
                    pos,
                    edgelist=[(u, v)],  # 只绘制当前的边
                    edge_color=[edge_colors[i]],  # 设置边的颜色为 RGB
                    connectionstyle=edge_styles[i],  # 设置连接样式
                    arrowstyle="->",
                    arrowsize=15,
                    alpha=alpha,
                )

            nx.draw_networkx_labels(G, pos, font_size=10)
            self._save_social_network(G, sim, plt)
            plt.close()

    def _save_social_network(self, sim, plt):
        if not os.path.exists(f"{self.sim_folder}/social_network"):
            os.makedirs(f"{self.sim_folder}/social_network")
        plt.savefig(f"{self.sim_folder}/social_network/{sim.sim_code}.png")

    def _set_nodes(self, G, ps):
        node_size = []
        node_color = []
        node_shape = []
        for n in G.nodes():
            p = ps[n]
            d_connect = get_d_connect(p, G)
            node_size.append(len(d_connect) * 1000)
            node_color.append((0.663, 0.820, 0.557))
            node_shape.append("o")
        return node_size, node_color, node_shape

    def _set_edges(self, G, ps):
        set_dict = dict()
        edge_color = []
        connection_style = []
        for edge in G.edges():
            if set_dict.get((edge[0], edge[1]), None) is not None:
                edge_color.append(set_dict[(edge[0], edge[1])]["color"])
                connection_style.append(set_dict[(edge[0], edge[1])]["style"])
                continue

            edge_color.append("gray")
            connection_style.append("arc3,rad=0.2")
            set_dict[(edge[1], edge[0])] = {
                    "color": "gray",
                    "style": "arc3,rad=-0.2",
                }
        return edge_color, connection_style


if __name__ == "__main__":
    sim_folder = input("Please input the analysis sim folder: ")
    sims = get_all_sim_info(sim_folder)
    sa = SocialNetworkAnalysis(sims)
    if os.path.exists(f"{sim_folder}_result"):
        os.makedirs(f"{sim_folder}_result")
    sa.draw_social_network()
