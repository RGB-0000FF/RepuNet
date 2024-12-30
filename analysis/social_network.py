import networkx as nx
import matplotlib.pyplot as plt
import os
from analysis import get_all_sim_info


def get_d_connect(init_persona, G):
    d_connect_list = []
    for edge in G.edges():
        if edge[0] == init_persona.name:
            if G.has_edge(edge[1], init_persona.name):
                d_connect_list.append(edge[1])
    return d_connect_list


def get_reputation_score(target_persona, target_persona_role, personas):
    count = 0
    num = 0
    for _, persona in personas.items():
        reputation = persona.reputationDB.get_targets_individual_reputation(
            target_persona.scratch.ID, target_persona_role
        )
        if target_persona_role == "investor":
            input = "Investor"
        elif target_persona_role == "trustee":
            input = "Trustee"
        if reputation:
            count += 1
            repu_score = reputation[f"{input}_{target_persona.scratch.ID}"][
                "numerical record"
            ]
            scores = repu_score.replace("(", "").replace(")", "").split(",")
            score = (
                float(scores[4])
                + float(scores[3])
                - float(scores[1])
                - float(scores[0])
            )
            if score > 1:
                score = 1
            elif score < -1:
                score = -1
            num += score
    if count == 0:
        return 0
    return num / count


class SocialNetworkAnalysis:
    def __init__(self, sim_folder, with_repu):
        self.sim_folder = sim_folder
        self.sims = get_all_sim_info(sim_folder)
        self.with_repu = with_repu

    def draw_social_network(self, save_folder):
        for sim in self.sims:
            G = sim.G
            plt.figure(figsize=(20, 20))
            pos = nx.spring_layout(G, k=1.5, iterations=150)
            if self.with_repu:
                node_sizes, node_colors, inner_colors = self._set_nodes_reputation(
                    G, sim.personas
                )
            else:
                node_sizes, node_colors = self._set_nodes_without_reputation(
                    G, sim.personas
                )
            edge_colors, edge_styles = self._set_edges(G, sim.personas)

            # Draw outer circles first
            # investor reputation color
            for i, node in enumerate(G.nodes()):
                nx.draw_networkx_nodes(
                    G,
                    pos,
                    nodelist=[node],
                    node_size=node_sizes[i],
                    node_color=[node_colors[i]],
                    node_shape="o",
                    alpha=0.5,
                )
                if self.with_repu:
                    # Draw inner circles
                    # trustee reputation color
                    nx.draw_networkx_nodes(
                        G,
                        pos,
                        nodelist=[node],
                        node_size=node_sizes[i]
                        * 0.6,  # Inner circle is 60% of outer circle
                        node_color=[inner_colors[i]],
                        node_shape="o",
                        alpha=0.7,
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
            self._save_social_network(sim, plt, save_folder)
            plt.close()

    def _save_social_network(self, sim, plt, save_folder):
        # Convert to absolute path if save_folder is relative
        if not os.path.isabs(save_folder):
            save_folder = os.path.abspath(save_folder)

        # Create full path including sim_code subdirectory
        save_path = os.path.join(save_folder, "social_network")
        os.makedirs(save_path, exist_ok=True)

        file_path = os.path.join(save_path, f"{sim.step}.png")
        plt.savefig(file_path)
        # plt.show()

    def _set_nodes_reputation(self, G, ps):
        node_size = []
        outer_color = []  # investor reputation color
        inner_color = []  # trustee reputation color
        for n in G.nodes():
            p = ps[n]
            d_connect = get_d_connect(p, G)
            node_size.append(len(d_connect) * 1000)

            # Get reputation scores for both roles
            repu_score_i = get_reputation_score(p, "investor", ps)
            repu_score_t = get_reputation_score(p, "trustee", ps)

            # Set outer color (investor reputation)
            if repu_score_i > 0:
                outer_color.append((0.663, 0.820, 0.557))  # Light green
            elif repu_score_i < 0:
                outer_color.append((0.788, 0.494, 0.506))  # Light red
            else:
                outer_color.append((0.5, 0.5, 0.5))  # Light gray

            # Set inner color (trustee reputation)
            if repu_score_t > 0:
                inner_color.append((0.4, 0.7, 0.4))  # Dark green
            elif repu_score_t < 0:
                inner_color.append((0.7, 0.4, 0.4))  # Dark red
            else:
                inner_color.append((0.3, 0.3, 0.3))  # Dark gray

        return node_size, outer_color, inner_color

    def _set_nodes_without_reputation(self, G, ps):
        node_size = []
        outer_color = []  # investor reputation color
        for n in G.nodes():
            p = ps[n]
            d_connect = get_d_connect(p, G)
            node_size.append(len(d_connect) * 1000)
            outer_color.append((0.663, 0.820, 0.557))  # Light green

        return node_size, outer_color

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
    with_repu = input("With reputation? (y/n)")
    # sims = get_all_sim_info(sim_folder)
    with_repu = "y" in with_repu.lower() and "n" not in with_repu.lower()
    sa = SocialNetworkAnalysis(sim_folder, with_repu)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(current_dir)
    if not os.path.exists(f"./{sim_folder}_result"):
        os.makedirs(f"./{sim_folder}_result")
    sa.draw_social_network(f"./{sim_folder}_result")
