import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.colors as mcolors
import matplotlib.cm as cm
import os
import json
from analysis import get_all_sim_info


def replace_easy_name(name):
    # TODO change to the actual sim persona names
    personas = {
        "Liam OConnor": "LOC",
        "Hiroshi Tanaka": "HT",
        "David Johnson": "DJ",
        "Maria Rossi": "MR",
        "Sofia Hernandez": "SH",
        "James Wang": "JW",
        "Sergey Petrov": "SP",
        "Hannah Muller": "HM",
        "Nadia Novak": "NN",
        "Elena Ivanova": "EI",
        "Mohammed Al-Farsi": "MA",
        "Aisha Ibrahim": "AI",
        "Akiko Sato": "AS",
        "Emma Dubois": "ED",
        "Juan Carlos Reyes": "JCR",
        "Ahmed Hassan": "AH",
        "Robert Miller": "RM",
        "Fatima Ali": "FA",
        "Isabella Costa": "IC",
        "Mateo Garcia": "MG",
    }
    return personas[name]


def get_d_connect(init_persona, G):
    d_connect_list = []
    for edge in G.edges():
        if edge[0] == init_persona.name:
            if G.has_edge(edge[1], init_persona.name):
                d_connect_list.append(edge[1])
    return d_connect_list


def get_data(G, ps, key):
    data = {}
    for node in G.nodes():
        p = ps[node]
        data[node] = get_reputation_score(p, key, ps)

    return data


def calculate_positions(
    data, spread=0.8, central_radius=0.5, outer_radius=1.2, iterations=20
):
    sorted_data = sorted(data.items(), key=lambda x: x[1])  # 按分数升序排序

    # 将数据分为两部分：score > 0 和 score <= 0
    positive_nodes = [(node, score) for node, score in sorted_data if score > 0]
    negative_nodes = [(node, score) for node, score in sorted_data if score <= 0]

    # 计算画布比例
    total_nodes = len(positive_nodes) + len(negative_nodes)
    right_ratio = len(positive_nodes) / total_nodes if total_nodes > 0 else 0.5

    positions = {}

    # 右半画布范围 (score > 0)
    right_x_min, right_x_max = -1 + 2 * (1 - right_ratio), 1
    # 左半画布范围 (score <= 0)
    left_x_min, left_x_max = -1, -1 + 2 * (1 - right_ratio)

    def place_nodes_in_region(nodes, x_min, x_max, y_min, y_max):
        region_positions = {}
        used_positions = []
        for i, (node, score) in enumerate(nodes):
            best_position = None
            best_score = float("inf")
            local_spread = spread
            for _ in range(iterations):
                x = np.random.uniform(x_min, x_max)
                y = np.random.uniform(y_min, y_max)  # 随机选择垂直位置
                dist_to_others = (
                    min(
                        np.linalg.norm(np.array((x, y)) - np.array(pos))
                        for pos in used_positions
                    )
                    if used_positions
                    else float("inf")
                )

                # 如果找到一个更好的位置
                if dist_to_others >= local_spread and dist_to_others < best_score:
                    best_position = (x, y)
                    best_score = dist_to_others

                # 动态调整 spread，增加尝试范围
                if dist_to_others < local_spread:
                    local_spread *= 0.9

            if best_position:
                region_positions[node] = best_position
                used_positions.append(best_position)
            else:
                # Fallback: 强制放置节点
                print(f"Fallback: Placing node {node} in region with reduced spacing.")
                region_positions[node] = (
                    np.random.uniform(x_min, x_max),
                    np.random.uniform(y_min, y_max),
                )
                used_positions.append(region_positions[node])
        return region_positions

    # 布局右半部分的节点 (score > 0)
    right_positions = place_nodes_in_region(
        positive_nodes, right_x_min, right_x_max, -1, 1
    )
    positions.update(right_positions)

    # 布局左半部分的节点 (score <= 0)
    left_positions = place_nodes_in_region(
        negative_nodes, left_x_min, left_x_max, -1, 1
    )
    positions.update(left_positions)

    return positions


# 获取节点颜色
# def get_color_for_score(score, min_score, max_score):
#     normalized_score = (score - min_score) / (max_score - min_score)
#     return plt.cm.Reds(normalized_score)
def get_color_for_score(score, min_score=-1, max_score=1):
    # 自定义颜色段，从蓝色到橙色再到红色
    colors = ["#1f78b4", "#d62728"]  # 蓝色，橙色，红色
    cmap = mcolors.LinearSegmentedColormap.from_list("custom_cmap", colors, N=256)

    # 将分数标准化到 [0, 1] 范围
    normalized_score = (score - min_score) / (max_score - min_score)
    normalized_score = max(0, min(normalized_score, 1))  # 确保在 [0, 1] 范围内

    # 返回对应颜色
    return cmap(normalized_score)


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
    def __init__(self, sim_folder, sim, with_repu, limit):
        self.sim_folder = sim_folder
        self.sims = get_all_sim_info(sim_folder, sim, with_repu, limit)
        self.with_repu = with_repu
        self.sim = sim

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
                    # if "sign" in self.sim:

                with open(save_path + f"/{key}_{sim.step}.json", "w") as f:
                    json.dump(result, f, indent=4)

    def draw_social_network(self, save_folder):
        for sim in self.sims:
            Gs = sim.G
            for key, G in Gs.items():
                plt.figure(figsize=(5, 5))
                if self.with_repu and sim.step != 0:
                    data = get_data(G, sim.personas, key)
                    pos = calculate_positions(data)
                    node_sizes, node_colors = self._set_nodes_reputation(
                        G, sim.personas, key
                    )
                    color_map = {
                        node: get_color_for_score(score, -1, 1)
                        for node, score in data.items()
                    }
                elif self.with_repu and sim.step == 0:
                    data = get_data(G, sim.personas, key)
                    pos = nx.spring_layout(G, k=1.5, iterations=150)
                    node_sizes, _ = self._set_nodes_reputation(
                        G, sim.personas, key
                    )
                    color_map = {
                        node: get_color_for_score(score, -1, 1)
                        for node, score in data.items()
                    }
                else:
                    pos = nx.spring_layout(G, k=1.5, iterations=150)
                    node_sizes, color_map = self._set_nodes_without_reputation(
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
                        node_color=[color_map[node]],
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
                        arrowsize=5,
                        alpha=alpha,
                    )
                labels = {node: replace_easy_name(node) for node in G.nodes()}
                nx.draw_networkx_labels(G, pos, labels=labels, font_size=6)
                plt.axis("off")
                # # 创建颜色条 (Colorbar)
                # fig, ax = plt.subplots(figsize=(12, 8))

                # # 自定义三段式颜色条
                # cmap_list = [
                #     (plt.cm.Purples, -1, 0),   # 蓝色到紫色
                #     (plt.cm.Oranges, 0, 0.5),  # 浅橙色
                #     (plt.cm.Reds, 0.5, 1),     # 红色
                # ]

                # for cmap, vmin, vmax in cmap_list:
                #     norm = mcolors.Normalize(vmin=vmin, vmax=vmax)
                #     sm = cm.ScalarMappable(cmap=cmap, norm=norm)
                #     sm.set_array([])
                #     cbar = plt.colorbar(sm, ax=ax, orientation="vertical", fraction=0.05, pad=0.05)
                #     cbar.set_label(f"Scores in range [{vmin}, {vmax}]", rotation=90)
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
        plt.savefig(file_path, bbox_inches="tight", dpi=600)
        # plt.show()

    def _set_nodes_reputation(self, G, ps, key):
        node_size = []
        outer_color = []  # investor reputation color
        for n in G.nodes():
            p = ps[n]
            d_connect = get_d_connect(p, G)
            if len(d_connect) == 0:
                node_size.append(100)
            else:
                node_size.append(len(d_connect) * 100)

            # Get reputation scores for both roles
            repu_score = get_reputation_score(p, key, ps)

            if repu_score > 0:
                outer_color.append((0.663, 0.820, 0.557))  # Light green
            elif repu_score < 0:
                outer_color.append((0.788, 0.494, 0.506))  # Light red
            else:
                outer_color.append((0.5, 0.5, 0.5))  # Light gray

        return node_size, outer_color

    def _set_nodes_without_reputation(self, G, ps):
        node_size = []
        color_map = dict()
        for n in G.nodes():
            p = ps[n]
            d_connect = get_d_connect(p, G)
            if len(d_connect) == 0:
                node_size.append(100)
            else:
                node_size.append(len(d_connect) * 100)
            color_map[n] = "green"  # Light blue

        return node_size, color_map

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
                "style": "arc3,rad=0.2",
            }
        return edge_color, connection_style


if __name__ == "__main__":
    # init set
    sim_folders = [
        "sign_s14_without_all",
        "sign_s22_with_all",
        "sign_s18_without_gossip",
        "sign_s19_without_repu_with_gossip",
        # "sign_s14_without_all",
        # "sign_s22_with_all",
        # "sign_s18_without_gossip",
        # "sign_s19_without_repu_with_gossip",
        # "sign_s14_without_all",
        # "sign_s22_with_all",
        # "sign_s18_without_gossip",
        # "sign_s19_without_repu_with_gossip",
        # "investment_s2",
        # "investment_s8_without_repu_gossip",
        # "investment_s9_without_repu_with_gossip",
    ]
    with_repu = [
        False,
        True,
        True,
        False,
        False,
        True,
        True,
        False,
        False,
        True,
        True,
        False,
    ]
    limit = [
        (100, 151),
        (100, 151),
        (100, 151),
        (100, 151),
        # (50, 51),
        # (50, 51),
        # (50, 51),
        # (50, 51),
        # (100, 101),
        # (100, 101),
        # (100, 101),
        # (100, 101),
    ]
    for i, sim_folder in enumerate(sim_folders):
        if i != 0:
            os.chdir("../")
        sa = SocialNetworkAnalysis(sim_folder, "sign", with_repu[i], limit[i])
        current_dir = os.path.dirname(os.path.abspath(__file__))
        os.chdir(current_dir)
        if not os.path.exists(f"./{sim_folder}_result"):
            os.makedirs(f"./{sim_folder}_result")
        sa.draw_social_network(f"./{sim_folder}_result")
        sa.save_social_network_detail(f"./{sim_folder}_result")
    