import networkx as nx
import matplotlib.pyplot as plt
import os
import json
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
        elif target_persona_role == "resident":
            input = "Resident"
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
    return round((num / count), 3)


class SocialNetworkAnalysis:
    def __init__(self, sim_folder, sim, with_repu):
        self.sim_folder = sim_folder
        self.sims = get_all_sim_info(sim_folder, sim, with_repu)
        self.with_repu = with_repu

    def save_social_network_detail(self, save_folder):
        save_path = os.path.join(save_folder, "social_network_detail")
        os.makedirs(save_path, exist_ok=True)
        for sim in self.sims:
            result = dict()
            Gs = sim.G
            for key, G in Gs.items():
                for n in G.nodes():
                    p = sim.personas[n]
                    d_connect = get_d_connect(p, G)
                    if self.with_repu:
                        repu_score = get_reputation_score(p, key, sim.personas)
                        repus = p.reputationDB.get_all_reputations(
                            key, p.scratch.ID, True
                        )
                    else:
                        repu_score = None
                        repus = None
                    result[n] = {
                        "d_connect": d_connect,
                        f"repu_score_{key}": repu_score,
                        "reputation_database": repus,
                    }
                with open(save_path + f"/{key}_{sim.step}.json", "w") as f:
                    json.dump(result, f, indent=4)

    def draw_social_network(self, save_folder):
        for sim in self.sims:
            Gs = sim.G
            for key, G in Gs.items():
                plt.figure(figsize=(20, 20))
                pos = nx.spring_layout(G, k=1.5, iterations=150)
                if self.with_repu:
                    node_sizes, node_colors = self._set_nodes_reputation(
                        G, sim.personas, key
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
                self._save_social_network(sim, plt, save_folder, key)
                plt.close()

    def _save_social_network(self, sim, plt, save_folder, key):
        # Convert to absolute path if save_folder is relative
        if not os.path.isabs(save_folder):
            save_folder = os.path.abspath(save_folder)

        # Create full path including sim_code subdirectory
        save_path = os.path.join(save_folder, "social_network")
        os.makedirs(save_path, exist_ok=True)

        file_path = os.path.join(save_path, f"{key}_{sim.step}.png")
        plt.savefig(file_path)
        # plt.show()

    def _set_nodes_reputation(self, G, ps, key):
        node_size = []
        outer_color = []  # investor reputation color
        for n in G.nodes():
            p = ps[n]
            d_connect = get_d_connect(p, G)
            if len(d_connect) == 0:
                node_size.append(500)
            else:
                node_size.append(len(d_connect) * 1000)

            # Get reputation scores for both roles
            repu_score = get_reputation_score(p, key, ps)

            # Set outer color (investor reputation)
            if repu_score > 0:
                outer_color.append((0.663, 0.820, 0.557))  # Light green
            elif repu_score < 0:
                outer_color.append((0.788, 0.494, 0.506))  # Light red
            else:
                outer_color.append((0.5, 0.5, 0.5))  # Light gray

        return node_size, outer_color

    def _set_nodes_without_reputation(self, G, ps):
        node_size = []
        outer_color = []
        for n in G.nodes():
            p = ps[n]
            d_connect = get_d_connect(p, G)
            node_size.append(len(d_connect) * 1000)
            outer_color.append((0.55, 1, 1))  # Light blue

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
    # init set
    sim_folders = [
        # "sign_s7_with_all_r",
        # "sign_s20_with_all",
        # "sign_s18_without_gossip",
        "s20_without_repu_gossip",
        # "investment_s2",
        # "investment_s8_without_repu_gossip",
        # "investment_s9_without_repu_with_gossip",
    ]
    with_repu = [False]
    for i, sim_folder in enumerate(sim_folders):
        if i != 0:
            os.chdir("../")
        sa = SocialNetworkAnalysis(sim_folder, "invest", with_repu[i])
        current_dir = os.path.dirname(os.path.abspath(__file__))
        os.chdir(current_dir)
        if not os.path.exists(f"./{sim_folder}_result"):
            os.makedirs(f"./{sim_folder}_result")
        sa.draw_social_network(f"./{sim_folder}_result")
        sa.save_social_network_detail(f"./{sim_folder}_result")
    