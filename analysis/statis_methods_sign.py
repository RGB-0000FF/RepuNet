import seaborn as sns
import numpy as np
import pandas as pd
import datetime
import os
from PIL import Image
import statsmodels.api as sm
from analysis import *
from statis_methods import *
import matplotlib.pyplot as plt
import matplotlib as mpl
import community as community_louvain
from infomap import Infomap


def load_images(folder_path):
    """
    从文件夹加载图片并按文件名排序。
    :param folder_path: 图片所在文件夹路径
    :return: 图片路径列表（按文件名排序）
    """
    image_files = sorted(
        [
            os.path.join(folder_path, f)
            for f in os.listdir(folder_path)
            if f.lower().endswith(("png", "jpg", "jpeg"))
            and f.split("_")[-1].split(".")[0] in ["1", "50", "100"]
        ]
    )
    return image_files


def plot_image_grid(image_paths, row_titles, col_titles):
    """
    Display images in a grid with row and column titles.
    :param image_paths: List of image paths, arranged by grid order.
    :param row_titles: List of row titles.
    :param col_titles: List of column titles.
    """
    num_rows = len(row_titles)
    num_cols = len(col_titles)

    # Create grid layout
    fig, axes = plt.subplots(num_rows, num_cols, figsize=(10, 10))
    axes = axes if isinstance(axes, (list, np.ndarray)) else [axes]

    # Add images to the grid
    for i in range(num_rows):
        for j in range(num_cols):
            ax = axes[i, j]
            idx = i * num_cols + j
            if idx < len(image_paths):
                img = Image.open(image_paths[idx])
                ax.imshow(img)
            ax.axis("off")

            # Add column titles
            if i == 0:
                ax.set_title(col_titles[j], fontsize=14, pad=20)

            # Add row titles
            if j == 0:
                ax.annotate(
                    row_titles[i],
                    xy=(0, 0.5),
                    xytext=(-ax.yaxis.labelpad - 20, 0),
                    textcoords="offset points",
                    ha="center",
                    va="center",
                    # rotation=90,
                    fontsize=14,
                )

    # Adjust layout
    plt.tight_layout()
    plt.subplots_adjust(top=0.85, wspace=0.3, hspace=0.3)
    plt.show()


def plot_image_grid_t(image_paths, row_titles, col_titles):
    """
    将图片按网格形式展示，并添加行标题和列标题。
    :param image_paths: 图片路径列表（按顺序填入网格）
    :param row_titles: 行标题列表
    :param col_titles: 列标题列表
    """
    num_rows = len(row_titles)
    num_cols = len(col_titles)

    # 创建网格布局
    fig, axes = plt.subplots(num_rows, num_cols, figsize=(16, 12))

    # 遍历每个子图
    for i, row_title in enumerate(row_titles):
        for j, col_title in enumerate(col_titles):
            ax = axes[i, j]
            idx = i * num_cols + j
            if idx < len(image_paths):
                # 加载图片
                img = Image.open(image_paths[idx])
                ax.imshow(img)

            # 隐藏坐标轴
            ax.axis("off")

            # 设置标题
            if i == 0:
                ax.set_title(col_title, fontsize=12)
            if j == 0:
                ax.set_ylabel(row_title, fontsize=12, rotation=0, labelpad=40)

    # 调整布局以确保标题显示
    plt.tight_layout()
    plt.show()


class DataAnalysis:
    def __init__(self, data=None):
        self.data = data

    def line_plot(self, title, xlabel, ylabel, additional_data=None):
        plt.figure(figsize=(10, 6))
        # plt.plot(self.data["x"], self.data["y"], label="Line plot")
        if additional_data is not None:
            for label, data in additional_data.items():
                plt.plot(data["x"], data["y"], label=label)
        # plt.ylim([0, 1])  # Customize the y-axis limits as needed
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.title(title)
        plt.grid(True, which="both", linestyle="--", linewidth=0.5)
        plt.legend()
        plt.show()

    def bar_plot_single(
        self, bar_data, labels, xlabel, ylabel, title, xtick_labels, bar_errors
    ):
        """
        绘制单柱状图，每个柱用不同颜色表示类别
        :param bar_data: 一维列表，包含柱状图数据
        :param labels: 每个柱的标签
        :param xlabel: x轴标签
        :param ylabel: y轴标签
        :param title: 图表标题
        :param xtick_labels: x轴刻度标签
        """
        n = len(bar_data)  # 柱子的数量
        bar_width = 0.15  # 每个柱的宽度（适当缩小以避免重叠）

        # 通过 linspace 生成均匀分布的 x 轴位置
        x_positions = np.linspace(
            0.2, 0.8, n
        )  # 在 0.2 到 0.8 之间生成 n 个位置，避免靠边

        fig, ax = plt.subplots(figsize=(8, 6))

        # 绘制每个柱子，并添加误差棒
        colors = plt.cm.tab10.colors  # 使用 matplotlib 提供的配色方案
        for i, (value, error, label) in enumerate(zip(bar_data, bar_errors, labels)):
            ax.bar(
                x_positions[i],
                value,
                width=bar_width,
                color=colors[i % len(colors)],
                label=label,
                yerr=error,
                capsize=5,
            )

        # 设置x轴
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.set_title(title)

        # 设置刻度位置和标签
        ax.set_xticks(x_positions)
        ax.set_xticklabels(xtick_labels)

        # 添加图例（避免重复）
        handles, unique_labels = [], []
        for i, label in enumerate(labels):
            if label not in unique_labels:
                handles.append(
                    plt.Line2D([0], [0], color=colors[i % len(colors)], lw=4)
                )
                unique_labels.append(label)
        ax.legend(handles, unique_labels)

        # 显示网格
        plt.grid(True, which="both", linestyle="--", linewidth=0.5)
        # Highlight y=0 line
        # ax.axhline(0, color='black', linewidth=1.3, linestyle='--')
        # plt.ylim([-1, 1])  # 自定义 y 轴限制

        # 自动调整布局
        plt.tight_layout()

        # 显示图形
        plt.show()

    def heatmap(self, heatmap_data):
        plt.figure(figsize=(10, 6))
        sns.heatmap(heatmap_data, annot=True, cmap="coolwarm")
        plt.title("Heatmap")
        plt.show()

    def line_plot_with_error_bars(self, y_err):
        plt.figure(figsize=(10, 6))
        plt.errorbar(
            self.data["x"],
            self.data["y"],
            yerr=y_err,
            fmt="-o",
            label="Line plot with error bars",
        )
        plt.xlabel("X-axis")
        plt.ylabel("Y-axis")
        plt.title("Line Plot with Error Bars")
        plt.legend()
        plt.show()


# def draw_line():
#     sim1 = get_all_sim_info("sign_s18_without_gossip", "sign", True, (1, 201))
#     sim2 = get_all_sim_info("sign_s14_without_all", "sign", False, (1, 201))
#     sim3 = get_all_sim_info(
#         "sign_s19_without_repu_with_gossip", "sign", False, (1, 201)
#     )
#     sim4 = get_all_sim_info("sign_s22_with_all", "sign", True, (1, 201))
#     # Sample data
#     x1 = np.arange(1, 202, 5)
#     x2 = np.arange(1, 202, 5)
#     x3 = np.arange(1, 202, 5)
#     x4 = np.arange(1, 202, 5)
#     y1 = []
#     for sim in sim1:
#         if (sim.step - 1) % 5 == 0:
#             count = 0
#             anal_d = sim.analysis_dict
#             for k, v in anal_d.items():
#                 if v["sign up"].lower() == "yes":
#                     count += 1
#             y1.append(round(count / 20, 3))
#     # data1 = pd.DataFrame({"x": x, "y": y1})
#     y2 = []
#     for sim in sim2:
#         if (sim.step - 1) % 5 == 0:
#             count = 0
#             anal_d = sim.analysis_dict
#             for k, v in anal_d.items():
#                 if v["sign up"].lower() == "yes":
#                     count += 1
#             y2.append(round(count / 20, 3))
#     y3 = []
#     for sim in sim3:
#         if (sim.step - 1) % 5 == 0:
#             count = 0
#             anal_d = sim.analysis_dict
#             for k, v in anal_d.items():
#                 if v["sign up"].lower() == "yes":
#                     count += 1
#             y3.append(round(count / 20, 3))
#     y4 = []
#     for sim in sim4:
#         if (sim.step - 1) % 5 == 0:
#             count = 0
#             anal_d = sim.analysis_dict
#             for k, v in anal_d.items():
#                 if v["sign up"].lower() == "yes":
#                     count += 1
#             y4.append(round(count / 20, 3))
#     data2 = {
#         "without gossip": pd.DataFrame({"x": x1, "y": y1}),
#         "without all": pd.DataFrame({"x": x2, "y": y2}),
#         "without repu with gossip": pd.DataFrame({"x": x3, "y": y3}),
#         "with all": pd.DataFrame({"x": x4, "y": y4}),
#     }

#     analysis = DataAnalysis()

#     # Generate plots
#     analysis.line_plot(
#         "The sign-up rate varies with the step", "step", "sign up rate", data2
#     )


from scipy.interpolate import make_interp_spline


def data_test_2():
    sim1_group = [
        get_all_sim_info("sign_s1_with_all", "sign", True, (191, 201)),
        get_all_sim_info("sign_s22_with_all", "sign", True, (191, 201)),
        get_all_sim_info("sign_s5_with_all", "sign", True, (191, 201)),
        get_all_sim_info("sign_s9_with_all", "sign", True, (191, 201)),
        # get_all_sim_info("sign_s24_with_all", "sign", True, (191, 201)),
    ]
    sim2_group = [
        get_all_sim_info("sign_s18_without_gossip", "sign", True, (191, 201)),
        get_all_sim_info("sign_s2_without_gossip", "sign", True, (191, 201)),
        get_all_sim_info("sign_s25_without_gossip", "sign", True, (191, 201)),
        get_all_sim_info("sign_s6_without_gossip", "sign", True, (191, 201)),
        # get_all_sim_info("sign_s10_without_gossip", "sign", True, (191, 201)),
    ]
    sim3_group = [
        get_all_sim_info(
            "sign_s19_without_repu_with_gossip", "sign", False, (191, 201)
        ),
        get_all_sim_info("sign_s4_without_repu_with_gossip", "sign", False, (191, 201)),
        get_all_sim_info("sign_s7_without_repu_with_gossip", "sign", False, (191, 201)),
        get_all_sim_info(
            "sign_s11_without_repu_with_gossip", "sign", False, (191, 201)
        ),
        # get_all_sim_info(
        #     "sign_s26_without_repu_with_gossip", "sign", False, (191, 201)
        # ),
    ]
    sim4_group = [
        get_all_sim_info("sign_s14_without_all", "sign", False, (191, 201)),
        get_all_sim_info("sign_s3_without_repu_gossip", "sign", False, (191, 201)),
        get_all_sim_info("sign_s8_without_all", "sign", False, (191, 201)),
        get_all_sim_info("sign_s14_without_all", "sign", False, (191, 201)),
        # get_all_sim_info("sign_s27_without_all", "sign", False, (191, 201)),
    ]

    def positive_connect(persona, anal_d):
        count = 0
        connections = anal_d.get(persona, {}).get("d_connect", [])
        # return len(connections)
        for connect_persona in connections:
            if anal_d.get(connect_persona, {}).get("sign up", "").lower() == "yes":
                count += 1
        return count

    def calculate_y(sim_data):
        y = []
        for sim in sim_data:
            anal_d = sim.analysis_dict
            total_positive = 0
            total_users = 0

            for persona, data in anal_d.items():
                if data.get("sign up", "").lower() == "yes":
                    total_positive += positive_connect(persona, anal_d)
                    total_users += 1

            if not sim.with_reputation:
                total_users = 20
            avg_positive = total_positive / total_users if total_users > 0 else 0
            y.append(round(avg_positive, 3))

        return y

    def calculate_group_y(sim_group):
        return np.array([calculate_y(sim) for sim in sim_group])

    # 处理所有组
    groups = [sim1_group, sim2_group, sim3_group, sim4_group]
    results = {}
    for idx, group in enumerate(groups, 1):
        y_group = calculate_group_y(group)
        mean = np.mean(y_group, axis=0)
        std = np.std(y_group, axis=0)
        results[f"group_{idx}"] = {"mean": mean, "std": std}

    # 打印结果
    labels = [
        "With Reputation System",
        "Ablation Without Gossip",
        "Ablation Without Reputation",
        "Without Reputation System",
    ]
    for label, key in zip(labels, results.keys()):
        print(f"{label}: Mean={results[key]['mean']}, Std={results[key]['std']}")


import numpy as np


def data_test_3():
    sim1_group = [
        get_all_sim_info("sign_s1_with_all", "sign", True, (191, 201)),
        get_all_sim_info("sign_s22_with_all", "sign", True, (191, 201)),
        get_all_sim_info("sign_s5_with_all", "sign", True, (191, 201)),
        get_all_sim_info("sign_s9_with_all", "sign", True, (191, 201)),
    ]
    sim2_group = [
        get_all_sim_info("sign_s18_without_gossip", "sign", True, (191, 201)),
        get_all_sim_info("sign_s2_without_gossip", "sign", True, (191, 201)),
        get_all_sim_info("sign_s25_without_gossip", "sign", True, (191, 201)),
        get_all_sim_info("sign_s6_without_gossip", "sign", True, (191, 201)),
    ]
    sim3_group = [
        get_all_sim_info(
            "sign_s19_without_repu_with_gossip", "sign", False, (191, 201)
        ),
        get_all_sim_info("sign_s4_without_repu_with_gossip", "sign", False, (191, 201)),
        get_all_sim_info("sign_s7_without_repu_with_gossip", "sign", False, (191, 201)),
        get_all_sim_info(
            "sign_s11_without_repu_with_gossip", "sign", False, (191, 201)
        ),
    ]
    sim4_group = [
        get_all_sim_info("sign_s14_without_all", "sign", False, (191, 201)),
        get_all_sim_info("sign_s3_without_repu_gossip", "sign", False, (191, 201)),
        get_all_sim_info("sign_s8_without_all", "sign", False, (191, 201)),
        get_all_sim_info("sign_s14_without_all", "sign", False, (191, 201)),
    ]

    def positive_connect(persona, anal_d):
        count = 0
        connections = anal_d.get(persona, {}).get("d_connect", [])
        for connect_persona in connections:
            if anal_d.get(connect_persona, {}).get("sign up", "").lower() == "yes":
                count += 1
        return count

    def calculate_y(sim_data):
        y = []
        for sim in sim_data:
            anal_d = sim.analysis_dict
            total_positive = 0
            total_users = 0

            for persona, data in anal_d.items():
                if data.get("sign up", "").lower() == "yes":
                    total_positive += positive_connect(persona, anal_d)
                    total_users += 1
            if not sim.with_reputation:
                total_users = 20

            avg_positive = total_positive / total_users if total_users > 0 else 0
            y.append(round(avg_positive, 3))

        return y

    def calculate_group_y(sim_group):
        return np.array([calculate_y(sim) for sim in sim_group]).flatten()  # 展平数据

    # 处理所有组
    groups = [sim1_group, sim2_group, sim3_group, sim4_group]
    results = {}
    for idx, group in enumerate(groups, 1):
        y_group = calculate_group_y(group)  # 获取所有数据点
        mean_total = np.mean(y_group)  # 计算整个数据集的均值
        std_total = np.std(y_group)  # 计算整个数据集的标准差
        results[f"group_{idx}"] = {"mean": mean_total, "std": std_total}

    # 打印结果
    labels = [
        "With Reputation System",
        "Ablation Without Gossip",
        "Ablation Without Reputation",
        "Without Reputation System",
    ]
    for label, key in zip(labels, results.keys()):
        print(
            f"{label}: Mean={results[key]['mean']:.3f}, Std={results[key]['std']:.3f}"
        )


def data_test():
    sim4 = get_all_sim_info("sign_s22_with_all", "sign", True, (192, 201))
    sim2 = get_all_sim_info("sign_s14_without_all", "sign", False, (192, 201))
    names = ["Liam OConnor", "James Wang", "Nadia Novak", "Sergey Petrov"]
    ava_sign_up = []
    a_bid_UP = []
    a_bid_DOWN = []
    a_bid_NONE = []
    for sim in sim4:
        count = 0
        a_bid_u = 0
        a_bid_d = 0
        anal_d = sim.analysis_dict
        for k, v in anal_d.items():
            if v["sign up"].lower() == "yes":
                count += 1
            if k not in names:
                a_bid_u += len(v["d_connect"])
            else:
                a_bid_d += len(v["d_connect"])
        a_bid_UP.append(a_bid_u / 16)
        a_bid_DOWN.append(a_bid_d / 4)
        ava_sign_up.append(count / 20)

    for sim in sim2:
        a_bid_n = 0
        anal_d = sim.analysis_dict
        for k, v in anal_d.items():
            a_bid_n += len(v["d_connect"])
        a_bid_NONE.append(a_bid_n / 20)

    mean_a_bid_UP = np.mean(a_bid_UP)
    mean_a_bid_DOWN = np.mean(a_bid_DOWN)
    mean_a_bid_NONE = np.mean(a_bid_NONE)
    mean_a_bid_sign = np.mean(ava_sign_up)
    std_a_bid_UP = np.std(a_bid_UP)
    std_a_bid_DOWN = np.std(a_bid_DOWN)
    std_a_bid_NONE = np.std(a_bid_NONE)
    std_a_bid_sign = np.std(ava_sign_up)
    print(f"MeanWith_bad: {mean_a_bid_DOWN}, Standard Deviation: {std_a_bid_DOWN}")
    print(f"MeanWith_good: {mean_a_bid_UP}, Standard Deviation: {std_a_bid_UP}")
    print(f"MeanWithout: {mean_a_bid_NONE}, Standard Deviation: {std_a_bid_NONE}")
    print(f"MeanSign: {mean_a_bid_sign}, Standard Deviation: {std_a_bid_sign}")


import numpy as np
import json
from collections import defaultdict


def calculate_last_sim_data(sim_data):
    """计算每个step的mean和std"""
    step_values = defaultdict(list)
    for sim in sim_data:
        if (sim.step - 1) % 10 == 0:
            count = 0
            anal_d = sim.analysis_dict
            for k, v in anal_d.items():
                if v["sign up"].lower() == "yes":
                    count += 1
            step_values[sim.step].append(round(count / 20, 3))

    # 按step顺序排序并计算统计量
    sorted_steps = sorted(step_values.keys())
    means = [np.mean(step_values[step]) for step in sorted_steps]
    stds = [np.std(step_values[step]) for step in sorted_steps]

    return means, stds


def combine_mean_std(mean1, std1, N1, mean2, std2, N2):
    """合并两个数据集的统计量"""
    combined_mean = (N1 * mean1 + N2 * mean2) / (N1 + N2)
    combined_std = np.sqrt(
        (
            (N1 - 1) * std1**2
            + (N2 - 1) * std2**2
            + N1 * (mean1 - combined_mean) ** 2
            + N2 * (mean2 - combined_mean) ** 2
        )
        / (N1 + N2 - 1)
    )
    return combined_mean, combined_std


def merge_last_sim_data_and_save(
    file_path="data_dict_4.json",
    output_path="data_dict_full.json",
    existing_N=4,  # 假设原有数据基于20次实验
):
    # 加载现有数据
    data_dict_ablation, data_dict, x_original = load_data_dict(file_path)

    # 实验组配置
    sim_groups = {
        "With Reputation System": [
            get_all_sim_info("sign_s24_with_all", "sign", True, (1, 201)),
        ],
        "Ablation Without Gossip": [
            get_all_sim_info("sign_s10_without_gossip", "sign", True, (1, 201)),
        ],
        "Ablation Without Reputation": [
            get_all_sim_info(
                "sign_s26_without_repu_with_gossip", "sign", False, (1, 201)
            ),
        ],
        "Without Reputation System": [
            get_all_sim_info("sign_s27_without_all", "sign", False, (1, 201)),
        ],
    }

    # 合并每个组的统计量
    for group_name, sim_group in sim_groups.items():
        last_sim = sim_group[-1]

        # 获取新实验数据
        new_means, new_stds = calculate_last_sim_data(last_sim)

        # 确定数据存储位置（ablation或data）
        if group_name in data_dict_ablation:
            target_dict = data_dict_ablation
        elif group_name in data_dict:
            target_dict = data_dict
        else:
            print(f"Warning: {group_name} not found in data structures")
            continue

        # 对每个step进行合并
        original_means = target_dict[group_name]["mean"]
        original_stds = target_dict[group_name]["std"]

        # 确保数据长度一致
        if len(original_means) != len(new_means):
            print(f"Error: Data length mismatch in {group_name}")
            continue

        # 合并每个时间步
        combined_means = []
        combined_stds = []
        for om, os, nm, ns in zip(original_means, original_stds, new_means, new_stds):
            cm, cs = combine_mean_std(om, os, existing_N, nm, ns, 1)
            combined_means.append(round(cm, 3))
            combined_stds.append(round(cs, 3))

        # 更新数据
        target_dict[group_name]["mean"] = combined_means
        target_dict[group_name]["std"] = combined_stds

    # 构建合并后的数据结构
    # merged_data_dict = {
    #     "ablation": data_dict_ablation,
    #     "data": data_dict,
    #     "x_original": x_original.tolist(),
    # }
    # 自定义处理函数，支持 np.float64、np.int64 和 np.ndarray
    def np_float64_default(obj):
        if isinstance(obj, np.float64):
            return float(obj)  # 转换为 Python float
        elif isinstance(obj, np.int64):
            return int(obj)  # 转换为 Python int
        elif isinstance(obj, np.ndarray):
            return obj.tolist()  # 转换为 Python 列表
        raise TypeError(f"Type {type(obj)} not serializable")  # 处理其他类型

    # 保存文件
    with open(output_path, "w") as f:
        json.dump(
            {
                "ablation": {
                    key: {"mean": value["mean"], "std": value["std"]}
                    for key, value in data_dict_ablation.items()
                },
                "data": {
                    key: {"mean": value["mean"], "std": value["std"]}
                    for key, value in data_dict.items()
                },
                "x_original": x_original.tolist(),
            },
            f,
            default=np_float64_default,
        )
        # json.dump(merged_data_dict, f, indent=4)
    print(f"数据已成功保存至 {output_path}")


def get_data_dict():
    # sim1_1 = get_all_sim_info("sign_s1_with_all", "sign", True, (1, 201))
    # sim1_2 = get_all_sim_info("sign_s22_with_all", "sign", True, (1, 201))
    # sim2_1 = get_all_sim_info("sign_s18_without_gossip", "sign", True, (1, 201))
    # sim2_2 = get_all_sim_info("sign_s2_without_gossip", "sign", True, (1, 201))
    # sim2_3 = get_all_sim_info("sign_s23_without_gossip", "sign", True, (1, 201))
    # sim3_1 = get_all_sim_info(
    #     "sign_s19_without_repu_with_gossip", "sign", False, (1, 201)
    # )
    # sim3_2 = get_all_sim_info(
    #     "sign_s4_without_repu_with_gossip", "sign", False, (1, 201)
    # )
    # sim4_1 = get_all_sim_info("sign_s14_without_all", "sign", False, (1, 201))
    # sim4_2 = get_all_sim_info("sign_s3_without_repu_gossip", "sign", False, (1, 201))

    # 获取数据
    sim1_group = [
        # sim1_1,
        # sim1_2,
        get_all_sim_info("sign_s1_with_all", "sign", True, (1, 201)),
        get_all_sim_info("sign_s22_with_all", "sign", True, (1, 201)),
        get_all_sim_info("sign_s5_with_all", "sign", True, (1, 201)),
        get_all_sim_info("sign_s9_with_all", "sign", True, (1, 201)),
        get_all_sim_info("sign_s24_with_all", "sign", True, (1, 201)),
    ]
    sim2_group = [
        # sim2_1,
        # sim2_2,
        # sim2_3,
        get_all_sim_info("sign_s18_without_gossip", "sign", True, (1, 201)),
        get_all_sim_info("sign_s2_without_gossip", "sign", True, (1, 201)),
        get_all_sim_info("sign_s25_without_gossip", "sign", True, (1, 201)),
        get_all_sim_info("sign_s6_without_gossip", "sign", True, (1, 201)),
        get_all_sim_info("sign_s10_without_gossip", "sign", True, (1, 201)),
    ]
    sim3_group = [
        # sim3_1,
        # sim3_2,
        get_all_sim_info("sign_s19_without_repu_with_gossip", "sign", False, (1, 201)),
        get_all_sim_info("sign_s4_without_repu_with_gossip", "sign", False, (1, 201)),
        get_all_sim_info("sign_s7_without_repu_with_gossip", "sign", False, (1, 201)),
        get_all_sim_info("sign_s11_without_repu_with_gossip", "sign", False, (1, 201)),
        get_all_sim_info("sign_s26_without_repu_with_gossip", "sign", False, (1, 201)),
    ]
    sim4_group = [
        # sim4_1,
        # sim4_2,
        get_all_sim_info("sign_s14_without_all", "sign", False, (1, 201)),
        get_all_sim_info("sign_s3_without_repu_gossip", "sign", False, (1, 201)),
        get_all_sim_info("sign_s8_without_all", "sign", False, (1, 201)),
        get_all_sim_info("sign_s14_without_all", "sign", False, (1, 201)),
        get_all_sim_info("sign_s27_without_all", "sign", False, (1, 201)),
    ]

    # 采样数据
    x_original = np.arange(1, 202, 10)

    def calculate_y(sim_data):
        y = []
        for sim in sim_data:
            if (sim.step - 1) % 10 == 0:
                count = 0
                anal_d = sim.analysis_dict
                for k, v in anal_d.items():
                    if v["sign up"].lower() == "yes":
                        count += 1
                y.append(round(count / 20, 3))
        return y

    def calculate_group_y(sim_group):
        group_y = []
        for sim in sim_group:
            y = calculate_y(sim)
            group_y.append(y)
        return np.array(group_y)

    y1_group = calculate_group_y(sim1_group)
    y2_group = calculate_group_y(sim2_group)
    y3_group = calculate_group_y(sim3_group)
    y4_group = calculate_group_y(sim4_group)

    # 计算每个类别的均值和标准差
    y1_mean, y1_std = np.mean(y1_group, axis=0), np.std(y1_group, axis=0)
    y2_mean, y2_std = np.mean(y2_group, axis=0), np.std(y2_group, axis=0)
    y3_mean, y3_std = np.mean(y3_group, axis=0), np.std(y3_group, axis=0)
    y4_mean, y4_std = np.mean(y4_group, axis=0), np.std(y4_group, axis=0)

    # 将数据存储为 DataFrame

    data_dict_ablation = {
        "With Reputation System": {"mean": y1_mean, "std": y1_std},
        "Ablation Without Gossip": {"mean": y2_mean, "std": y2_std},
        "Ablation Without Reputation": {"mean": y3_mean, "std": y3_std},
        "Without Reputation System": {"mean": y4_mean, "std": y4_std},
    }
    data_dict = {
        "With Reputation System": {"mean": y1_mean, "std": y1_std},
        "Without Reputation System": {"mean": y4_mean, "std": y4_std},
    }
    # Save data to a file
    with open("data_dict_full.json", "w") as f:
        json.dump(
            {
                "ablation": {
                    key: {"mean": value["mean"].tolist(), "std": value["std"].tolist()}
                    for key, value in data_dict_ablation.items()
                },
                "data": {
                    key: {"mean": value["mean"].tolist(), "std": value["std"].tolist()}
                    for key, value in data_dict.items()
                },
                "x_original": x_original.tolist(),
            },
            f,
        )

    # return data_dict_ablation, data_dict, x_original


def load_data_dict(file_path="data_dict_full.json"):
    with open(file_path, "r") as f:
        data = json.load(f)

    # 将列表转换回 numpy 数组
    data_dict_ablation = {
        key: {"mean": np.array(value["mean"]), "std": np.array(value["std"])}
        for key, value in data["ablation"].items()
    }

    data_dict = {
        key: {"mean": np.array(value["mean"]), "std": np.array(value["std"])}
        for key, value in data["data"].items()
    }

    x_original = np.array(data["x_original"])

    return data_dict_ablation, data_dict, x_original


def draw_line_with_error_bands(data_dict, x_original, ablation=True):
    plt.rcParams["font.family"] = "Times New Roman"
    # 设置颜色
    if ablation:
        colors = ["blue", "orange", "green", "red"]
    else:
        colors = ["blue", "red"]
    plt.figure(figsize=(10, 6))

    for (label, stats), color in zip(data_dict.items(), colors):
        y_mean = stats["mean"]
        y_std = stats["std"]

        # 计算误差带
        y_upper = y_mean + y_std
        y_lower = y_mean - y_std

        # 绘制折线
        plt.plot(x_original, y_mean, label=label, color=color, marker="o")

        # 绘制误差带
        plt.fill_between(x_original, y_lower, y_upper, alpha=0.2, color=color)

        # 标注原始点
        plt.scatter(x_original, y_mean, alpha=0.7, color=color)

    # 图表设置
    plt.xlabel("Rounds", fontsize=28, fontname="Times New Roman")
    plt.ylabel("Proportion of participation", fontsize=28, fontname="Times New Roman")
    plt.ylim([0, 1])
    plt.xlim([0, 202])
    plt.xticks(fontname="Times New Roman", fontsize=25)
    plt.yticks(fontname="Times New Roman", fontsize=25)
    plt.legend(
        prop={"size": 25, "family": "Times New Roman"},
        loc="best",
    )
    # if ablation:
    #     plt.legend(
    #         loc="upper center",  # 让图例位于图形的上方中心位置
    #         bbox_to_anchor=(0.5, -0.2),  # 让图例向下移动到图表外
    #         ncol=2,  # 设置图例为两列
    #         # ncol=len(data_dict),
    #         prop={"size": 25, "family": "Times New Roman"},
    #         frameon=False,
    #     )
    # else:
    #     plt.legend(
    #         loc="upper center",  # 让图例位于图形的上方中心位置
    #         bbox_to_anchor=(0.5, -0.2),  # 让图例向下移动到图表外
    #         ncol=1,  # 设置图例为两列
    #         # ncol=len(data_dict),
    #         prop={"size": 25, "family": "Times New Roman"},
    #         frameon=False,
    #     )

    plt.grid(True)
    plt.savefig(
        f"sign-up_with_error_bands_lines_{datetime.datetime.now().second}.png",
        bbox_inches="tight",
        dpi=600,
    )


def draw_line_smooth(data_dict, x_original, ablation=True):
    plt.rcParams["font.family"] = "Times New Roman"
    # 设置颜色
    if ablation:
        colors = ["blue", "orange", "green", "red"]
    else:
        colors = ["blue", "red"]
    plt.figure(figsize=(10, 6))

    for (label, stats), color in zip(data_dict.items(), colors):
        y_mean = stats["mean"]
        y_std = stats["std"]

        # 使用 Cubic Spline 进行插值
        x_smooth = np.linspace(x_original.min(), x_original.max(), 300)
        spline = make_interp_spline(x_original, y_mean)
        y_smooth = spline(x_smooth)

        # 平滑后的误差带
        y_std_smooth = make_interp_spline(x_original, y_std)(x_smooth)
        y_upper = y_smooth + y_std_smooth
        y_lower = y_smooth - y_std_smooth

        # 绘制平滑曲线
        plt.plot(x_smooth, y_smooth, label=label, color=color)

        # 绘制误差带
        plt.fill_between(x_smooth, y_lower, y_upper, alpha=0.2, color=color)

        # 标注原始点
        plt.scatter(x_original, y_mean, alpha=0.7, color=color)

    # 图表设置
    plt.xlabel("Rounds", fontsize=28, fontname="Times New Roman")
    plt.ylabel("Proportion of Collaboration", fontsize=28, fontname="Times New Roman")
    plt.ylim([0, 1])
    plt.xlim([0, 202])
    plt.xticks(fontname="Times New Roman", fontsize=25)
    plt.yticks(fontname="Times New Roman", fontsize=25)
    plt.legend(
        prop={"size": 25, "family": "Times New Roman"},
        loc="upper left",  # 选择大致方向，如 upper left、upper right、lower left 等
        bbox_to_anchor=(0.3, 0.72),  # (x, y) 坐标，调整数值找到合适的位置
    )
    # if ablation:
    #     plt.legend(
    #         loc="upper center",  # 让图例位于图形的上方中心位置
    #         bbox_to_anchor=(0.5, -0.2),  # 让图例向下移动到图表外
    #         ncol=2,  # 设置图例为两列
    #         # ncol=len(data_dict),
    #         prop={"size": 25, "family": "Times New Roman"},
    #         frameon=False,
    #     )
    # else:
    #     plt.legend(
    #         loc="upper center",  # 让图例位于图形的上方中心位置
    #         bbox_to_anchor=(0.5, -0.2),  # 让图例向下移动到图表外
    #         ncol=1,  # 设置图例为两列
    #         # ncol=len(data_dict),
    #         prop={"size": 25, "family": "Times New Roman"},
    #         frameon=False,
    #     )
    # plt.tight_layout()
    plt.grid(True)
    plt.savefig(
        f"sign-up_with_error_bands_smooth_{datetime.datetime.now().second}.png",
        bbox_inches="tight",
        dpi=600,
    )

    # # 平滑曲线并绘图
    # plt.figure(figsize=(10, 6))
    # for label, df in data_dict.items():
    #     x = df["x"]
    #     y = df["y"]

    #     # 使用 Cubic Spline 进行插值
    #     x_smooth = np.linspace(x.min(), x.max(), 300)
    #     spline = make_interp_spline(x, y)
    #     y_smooth = spline(x_smooth)

    #     # 绘制平滑曲线
    #     plt.plot(x_smooth, y_smooth, label=label)

    #     # 标注原始点
    #     plt.scatter(x, y, alpha=0.7)

    # # plt.title("The sign-up rate varies with the step")
    # plt.xlabel("Rounds", fontsize=14, fontname="Times New Roman")
    # plt.ylabel("Proportion of participation", fontsize=14, fontname="Times New Roman")
    # plt.ylim([0, 1])
    # plt.xlim([0, 200])
    # plt.legend()
    # plt.grid(True)
    # plt.savefig("sign-up s.png", bbox_inches="tight", dpi=600)


def draw_network():
    # Load images
    image_folder = [
        "analysis/sign_s14_without_all_result/social_network",
        "analysis/sign_s19_without_repu_with_gossip_result/social_network",
        "analysis/sign_s18_without_gossip_result/social_network",
        "analysis/sign_s20_with_all_result/social_network",
    ]
    image_paths = []
    for folder_path in image_folder:
        image_paths += load_images(folder_path)

    row_titles = [
        "without all",
        "without repu with gossip",
        "without gossip",
        "with all",
    ]
    col_titles = [
        "round = 1",
        "round = 50",
        "round = 100",
    ]

    # Display images
    plot_image_grid(image_paths, row_titles, col_titles)


def draw_line2():
    """
    Draw the relationship between reputation and the number of bidirectional connections
    """
    sim1 = get_all_sim_info("sign_s18_without_gossip", "sign", True, (80, 101))
    # sim2 = get_all_sim_info("sign_s14_without_all", "sign", False, 201)
    # sim3 = get_all_sim_info("sign_s19_without_repu_with_gossip", "sign", False, 101)
    sim4 = get_all_sim_info("sign_s20_with_all", "sign", True, (80, 101))

    x = []
    y = []
    colors = []
    for sim in sim1 + sim4:
        anal_d = sim.analysis_dict
        for k, v in anal_d.items():
            if v["sign up"].lower() == "yes":
                x.append(v["reputation score"])
                y.append(len(v["d_connect"]))
                colors.append("red")
            else:
                x.append(v["reputation score"])
                y.append(len(v["d_connect"]))
                colors.append("blue")

    l1 = Linear_Regression(
        x, y, "reputation score", "d_connect", "reputation score vs d_connect"
    )
    l1.OLS()
    l1.visualization(colors, "gray", "Linear Regression")
    print(l1.return_result())
    plt.title(
        "Relationship Between Reputation and the Number of Bidirectional Connections"
    )
    plt.xlabel("Reputation Score")
    plt.ylabel("Bidirectional Connect")
    plt.xlim([-1, 1])
    plt.ylim([-3, 20])
    plt.grid(True, which="both", linestyle="--", linewidth=0.5)
    plt.legend()
    plt.show()


# def draw_line3():
#     """
#     Draw the relationship between gossip count and reputation for multiple experiments.
#     Use different colors for data points but only one regression line.
#     Only show legend for "原始数据点" and "回归线".
#     """
#     # Simulate multiple experiments (e.g., sim1, sim2, sim3, ...)
#     experiments = {
#         "sim1": get_all_sim_info("sign_s22_with_all", "sign", True, (200, 201)),
#         "sim2": get_all_sim_info("sign_s1_with_all", "sign", True, (200, 201)),
#         "sim3": get_all_sim_info("sign_s5_with_all", "sign", True, (200, 201)),
#         # Add more experiments as needed
#     }

#     # Process data from all experiments
#     x, y = [], []
#     color_list = []
#     for exp_name, sim_data in experiments.items():
#         for sim in sim_data:
#             anal_d = sim.analysis_dict
#             for k, v in anal_d.items():
#                 if v["gossip_count"] == 0:
#                     continue
#                 x.append(v["gossip_count"])
#                 y.append(v["reputation score"])
#                 color_list.append(
#                     exp_name
#                 )  # Assign experiment identifier to each data point

#     # Create a Linear_Regression instance
#     l1 = Linear_Regression(
#         x, y, "Number of Gossip", "Reputation", "Impact of Gossip on Reputation"
#     )
#     l1.OLS()

#     # Generate colors for each experiment
#     base_color = "blue"
#     colors = Linear_Regression.generate_colors(base_color, len(experiments))

#     # Plot the data
#     plt.figure(figsize=(6.4, 4.8))
#     l1.visualization(
#         color_list=color_list,
#         colors=colors,
#     )

#     # Customize the plot
#     plt.xlabel("Number of Gossip", fontsize=20, fontname="Times New Roman")
#     plt.ylabel("Reputation", fontsize=20, fontname="Times New Roman")
#     plt.xlim([0, 250])
#     plt.ylim([-1, 1])
#     plt.xticks(fontname="Times New Roman", fontsize=18)
#     plt.yticks(fontname="Times New Roman", fontsize=18)
#     plt.grid(True, which="both", linestyle="--", linewidth=0.5)

#     # Save the plot
#     plt.savefig("Gossip-Repu.png", bbox_inches="tight", dpi=600)
#     plt.show()


def draw_line3():
    """
    Draw the relationship between gossip count and reputation for multiple experiments.
    Calculate average reputation for each user across all experiments.
    Use different transparency (alpha) for data points but only one regression line.
    Show legend for "A Singal Agent" and "Linear_Regression".
    """

    def collect_all_data(*sim_lists):
        """
        收集所有实验的数据，返回合并后的 x, y 和颜色标识符
        - sim_lists: 可变参数，可接收多个实验列表（如 sim1, sim2）
        """
        x = []
        y = []
        color_list = []

        # 遍历所有实验组
        for exp_idx, sim_list in enumerate(sim_lists):
            # 遍历单个实验组内的所有模拟运行
            user_reputation_sum = {}
            user_gossip_count = {}  # 记录每个用户的 gossip_count

            for sim in sim_list:
                anal_d = sim.analysis_dict
                for username, user_data in anal_d.items():
                    # 更新 reputation 累计
                    if username in user_reputation_sum:
                        user_reputation_sum[username] += user_data["reputation score"]
                    else:
                        user_reputation_sum[username] = user_data["reputation score"]

                    # 记录每个用户的 gossip_count（最后一次出现的值）
                    user_gossip_count[username] = user_data["gossip_count"]

            # 计算每个用户的平均 reputation 和 gossip_count
            for username in user_gossip_count:
                avg_reputation = user_reputation_sum[username] / len(sim_list)
                x.append(user_gossip_count[username])
                y.append(avg_reputation)
                color_list.append(f"sim{exp_idx + 1}")  # 分配实验标识符

        return x, y, color_list

    # 获取实验数据
    sim1 = get_all_sim_info("sign_s22_with_all", "sign", True, (1, 201))
    sim2 = get_all_sim_info("sign_s1_with_all", "sign", True, (1, 201))
    sim3 = get_all_sim_info("sign_s5_with_all", "sign", True, (1, 201))
    sim4 = get_all_sim_info("sign_s9_with_all", "sign", True, (1, 201))
    sim5 = get_all_sim_info("sign_s24_with_all", "sign", True, (1, 201))
    # 可以继续添加更多实验

    # 合并所有实验数据
    x, y, color_list = collect_all_data(sim1, sim2, sim3, sim4, sim5)

    # 创建 Linear_Regression 实例
    l1 = Linear_Regression(
        x, y, "Number of Gossip", "Reputation", "Impact of Gossip on Reputation"
    )
    l1.OLS()
    print(l1.result)

    # 定义透明度（alpha）值
    alphas = {
        "sim1": 0.1,
        "sim2": 0.3,
        "sim3": 0.5,
        "sim4": 0.7,
        "sim5": 0.9,
    }

    # 绘制数据
    plt.figure(figsize=(6.4, 4.8))
    l1.visualization(
        color_list=color_list,
        alphas=alphas,
    )

    # 图表美化
    plt.xlabel("Number of Gossip", fontsize=20, fontname="Times New Roman")
    plt.ylabel("Reputation", fontsize=20, fontname="Times New Roman")
    plt.xlim([0, 250])
    plt.ylim([-1, 1])
    plt.xticks(fontname="Times New Roman", fontsize=18)
    plt.yticks(fontname="Times New Roman", fontsize=18)
    plt.legend(prop={"size": 18, "family": "Times New Roman"})
    plt.grid(True, which="both", linestyle="--", linewidth=0.5)

    # 保存图表
    plt.savefig("Gossip-Repu-Avg-Alpha.png", bbox_inches="tight", dpi=600)
    # plt.show()


# def draw_line3():
#     """
#     Draw the relationship between gossip count and reputation for multiple experiments.
#     Calculate average reputation for each user across all experiments.
#     Use different colors for data points but only one regression line.
#     Only show legend for "原始数据点" and "回归线".
#     """

#     def collect_all_data(*sim_lists):
#         """
#         收集所有实验的数据，返回合并后的 x 和 y
#         - sim_lists: 可变参数，可接收多个实验列表（如 sim1, sim2）
#         """
#         x = []
#         y = []
#         color_list = []
#         # 遍历所有实验组
#         for exp_idx, sim_list in enumerate(sim_lists):
#             # 遍历单个实验组内的所有模拟运行
#             user_gossip_sum = {}
#             user_reputation_sum = {}
#             user_gossip_count = {}  # 记录每个用户的 gossip_count

#             for sim in sim_list:
#                 anal_d = sim.analysis_dict
#                 for username, user_data in anal_d.items():
#                     # 更新 gossip_count 累计
#                     if username in user_gossip_sum:
#                         user_gossip_sum[username] += user_data["gossip_count"]
#                     else:
#                         user_gossip_sum[username] = user_data["gossip_count"]

#                     # 更新 reputation 累计
#                     if username in user_reputation_sum:
#                         user_reputation_sum[username] += user_data["reputation score"]
#                     else:
#                         user_reputation_sum[username] = user_data["reputation score"]

#                     # 记录每个用户的 gossip_count（最后一次出现的值）
#                     user_gossip_count[username] = user_data["gossip_count"]

#             # 计算每个用户的平均 reputation 和 gossip_count
#             for username in user_gossip_count:
#                 avg_reputation = user_reputation_sum[username] / len(sim_list)
#                 avg_gossip_count = user_gossip_sum[username] / len(sim_list)
#                 x.append(avg_gossip_count)
#                 y.append(avg_reputation)
#                 color_list.append(f"sim{exp_idx + 1}")  # 分配实验标识符

#         return x, y, color_list

#     # 获取实验数据
#     sim1 = get_all_sim_info("sign_s22_with_all", "sign", True, (1, 201))
#     # sim2 = get_all_sim_info("sign_s1_with_all", "sign", True, (1, 201))
#     # sim3 = get_all_sim_info("sign_s5_with_all", "sign", True, (1, 201))
#     # 可以继续添加更多实验

#     # 合并所有实验数据
#     x, y, color_list = collect_all_data(sim1)

#     # 创建 Linear_Regression 实例
#     l1 = Linear_Regression(
#         x, y, "Number of Gossip", "Reputation", "Impact of Gossip on Reputation"
#     )
#     l1.OLS()

#     # 生成颜色
#     base_color = "blue"
#     colors = Linear_Regression.generate_colors(base_color, 3)  # 3 个实验

#     # 绘制数据
#     plt.figure(figsize=(6.4, 4.8))
#     l1.visualization(
#         color_list=color_list,
#         colors=colors,
#     )

#     # 图表美化
#     plt.xlabel("Number of Gossip", fontsize=20, fontname="Times New Roman")
#     plt.ylabel("Reputation", fontsize=20, fontname="Times New Roman")
#     plt.xlim([0, 250])
#     plt.ylim([-1, 1])
#     plt.xticks(fontname="Times New Roman", fontsize=18)
#     plt.yticks(fontname="Times New Roman", fontsize=18)
#     plt.grid(True, which="both", linestyle="--", linewidth=0.5)

#     # 保存图表
#     plt.savefig("Gossip-Repu-Avg.png", bbox_inches="tight", dpi=600)
#     plt.show()


def draw_line4():
    """
    Draw the relationship between Probability of Participation and reputation
    (所有实验数据合并后进行单次回归)
    """

    def collect_all_data(*sim_lists):
        """
        收集所有实验的数据，返回合并后的 x 和 y
        - sim_lists: 可变参数，可接收多个实验列表（如 sim1, sim2）
        """
        x = []
        y = []
        color_list = []
        # 遍历所有实验组
        for exp_idx, sim_list in enumerate(sim_lists):
            # 遍历单个实验组内的所有模拟运行
            user_reputation_sum = {}
            user_signup_rate = {}  # 只记录最后一次出现的 sign up rate

            for sim in sim_list:
                anal_d = sim.analysis_dict
                for username, user_data in anal_d.items():
                    # 更新 reputation 累计
                    if username in user_reputation_sum:
                        user_reputation_sum[username] += user_data["reputation score"]
                    else:
                        user_reputation_sum[username] = user_data["reputation score"]

                    # 总是更新为最新的 sign up rate（最后一轮）
                    user_signup_rate[username] = user_data["sign up rate"]

            # 计算每个用户的平均 reputation

            for username in user_signup_rate:
                avg_reputation = user_reputation_sum[username] / len(sim_list)
                x.append(user_signup_rate[username])
                y.append(avg_reputation)
                color_list.append(f"sim{exp_idx + 1}")
        return x, y, color_list

    # 获取实验数据
    sim1 = get_all_sim_info("sign_s1_with_all", "sign", True, (1, 201))
    # sim2 = get_all_sim_info("sign_s2_without_gossip", "sign", True, (1, 201))
    sim2 = get_all_sim_info("sign_s22_with_all", "sign", True, (1, 201))
    # sim4 = get_all_sim_info("sign_s18_without_gossip", "sign", True, (1, 201))
    sim3 = get_all_sim_info("sign_s5_with_all", "sign", True, (1, 201))
    # sim6 = get_all_sim_info("sign_s6_without_gossip", "sign", True, (1, 201))
    sim4 = get_all_sim_info("sign_s9_with_all", "sign", True, (1, 201))
    sim5 = get_all_sim_info("sign_s24_with_all", "sign", True, (1, 201))

    # 合并所有实验数据
    x, y, color_list = collect_all_data(sim1, sim2, sim3, sim4, sim5)

    # 执行线性回归
    l1 = Linear_Regression(
        x,
        y,
        "Probability of Collaboration",
        "Reputation",
        "Impact of Sign-up Rate on Reputation",
    )
    l1.OLS()

    # 生成颜色
    # base_color = "blue"
    alphas = {
        "sim1": 0.1,
        "sim2": 0.3,
        "sim3": 0.5,
        "sim4": 0.7,
        "sim5": 0.9,
    }
    # colors = Linear_Regression.generate_colors(base_color, 3)  # 3 个实验

    # 绘制数据
    plt.figure(figsize=(6.4, 4.8))
    l1.visualization(
        color_list=color_list,
        alphas=alphas,
        # colors=colors,
    )
    print(l1.return_result())

    # 图表美化
    plt.xlabel("Probability of Participation", fontname="Times New Roman", fontsize=20)
    plt.ylabel("Reputation", fontname="Times New Roman", fontsize=20)
    plt.ylim([-1, 1])
    plt.xticks(fontname="Times New Roman", fontsize=18)
    plt.yticks(fontname="Times New Roman", fontsize=18)
    plt.grid(True, which="both", linestyle="--", linewidth=0.5)
    plt.legend(prop={"size": 18, "family": "Times New Roman"})
    plt.savefig("Participation-Repu.png", bbox_inches="tight", dpi=600)


def community_map(G):
    node_map = {node: i for i, node in enumerate(G.nodes())}
    infomap = Infomap()
    for u, v in G.edges():
        infomap.addLink(node_map[u], node_map[v])

    # 执行 Infomap 算法
    infomap.run()

    # 获取社区划分
    community_mapping = infomap.getModules()
    communities = {}
    for node, community_id in community_mapping.items():
        original_node = list(node_map.keys())[list(node_map.values()).index(node)]
        if community_id not in communities:
            communities[community_id] = []
        communities[community_id].append(original_node)
    return communities


def draw_cluster_repu_ava():
    sim1 = get_all_sim_info("sign_s22_with_all", "sign", True, (100, 101))
    for sim in sim1:
        communities = community_map(sim.G["resident"])


def draw_cluster_repu_ava_t():
    sim1 = get_all_sim_info("sign_s22_with_all", "sign", True, (101, 101))
    bar_data = []
    errors = []
    for sim in sim1:
        communities = community_map(sim.G["resident"])
        for _, v in communities.items():
            temp = []
            d = 0
            count = 0
            for node in v:
                d += sim.analysis_dict[node]["reputation score"]
                count += 1
                temp.append(sim.analysis_dict[node]["reputation score"])
            errors.append(np.std(temp))
            bar_data.append(round(d / count, 3))

    labels = [f"cluster {i+1}" for i in range(len(bar_data))]
    xlabel = ""
    ylabel = "Reputation Score"
    title = "Cluster Reputation Average"
    # bar_errors = np.std(bar_data)

    # 创建 DataAnalysis 实例并调用 bar_plot 方法
    analysis = DataAnalysis()
    analysis.bar_plot_single(
        bar_data=bar_data,
        labels=labels,
        xlabel=xlabel,
        ylabel=ylabel,
        title=title,
        xtick_labels=labels,
        bar_errors=errors,
    )


def draw_modularity():
    sim1 = get_all_sim_info("sign_s18_without_gossip", "sign", True, (0, 101))
    sim2 = get_all_sim_info("sign_s14_without_all", "sign", False, (0, 101))
    sim3 = get_all_sim_info(
        "sign_s19_without_repu_with_gossip", "sign", False, (0, 101)
    )
    sim4 = get_all_sim_info("sign_s20_with_all", "sign", True, (0, 101))
    x1 = np.arange(1, 102, 5)
    x2 = np.arange(1, 102, 5)
    x3 = np.arange(1, 102, 5)
    x4 = np.arange(1, 102, 5)
    y1 = []
    print("SIM111")
    for sim in sim1:
        if (sim.step - 1) % 5 == 0:
            y1.append(len(community_map(sim.G["resident"])))
            # g = sim.G["resident"].to_undirected()
            # print(type(g))
            # partition = community_louvain.best_partition(g)
            # y1.append(len(set(partition.values())))
            # modularity = community_louvain.modularity(graph=g, partition=partition)
            # y1.append(round(modularity, 3))
    # data1 = pd.DataFrame({"x": x, "y": y1})
    y2 = []
    print("SIM222")
    for sim in sim2:
        if (sim.step - 1) % 5 == 0:
            # g = sim.G["without_repu"].to_undirected()
            # partition = community_louvain.best_partition(g)
            y2.append(len(community_map(sim.G["without_repu"])))
            # y2.append(len(set(partition.values())))
            # modularity = community_louvain.modularity(graph=g, partition=partition)
            # y2.append(round(modularity, 3))
    y3 = []
    print("SIM333")
    for sim in sim3:
        if (sim.step - 1) % 5 == 0:
            y3.append(len(community_map(sim.G["without_repu"])))
            # g = sim.G["without_repu"].to_undirected()
            # partition = community_louvain.best_partition(g)
            # y3.append(len(set(partition.values())))
            # modularity = community_louvain.modularity(graph=g, partition=partition)
            # y3.append(round(modularity, 3))
    y4 = []
    for sim in sim4:
        if (sim.step - 1) % 5 == 0:
            y4.append(len(community_map(sim.G["resident"])))
            # g = sim.G["resident"].to_undirected()
            # partition = community_louvain.best_partition(g)
            # y4.append(len(set(partition.values())))
            # modularity = community_louvain.modularity(graph=g, partition=partition)
            # y4.append(round(modularity, 3))
    data2 = {
        "without gossip": pd.DataFrame({"x": x1, "y": y1}),
        "without all": pd.DataFrame({"x": x2, "y": y2}),
        "without repu with gossip": pd.DataFrame({"x": x3, "y": y3}),
        "with all": pd.DataFrame({"x": x4, "y": y4}),
    }

    analysis = DataAnalysis()

    # Generate plots
    analysis.line_plot(
        "The modularity rate varies with the step", "step", "modularity", data2
    )


def draw_sign_rate():
    sim1 = get_all_sim_info("sign_s18_without_gossip", "sign", True, (151, 151))
    sim2 = get_all_sim_info("sign_s14_without_all", "sign", False, (151, 151))
    sim3 = get_all_sim_info(
        "sign_s19_without_repu_with_gossip", "sign", False, (151, 151)
    )
    sim4 = get_all_sim_info("sign_s22_with_all", "sign", True, (151, 151))

    res1 = []
    for sim in sim1:
        anal_d = sim.analysis_dict
        yes = 0
        no = 0
        for k, v in anal_d.items():
            if v["sign up"].lower() == "yes":
                yes += 1
            elif v["sign up"].lower() == "no":
                no += 1
        res1.append(yes / (yes + no))
        res1.append(no / (yes + no))

    res2 = []
    for sim in sim2:
        anal_d = sim.analysis_dict
        yes = 0
        no = 0
        for k, v in anal_d.items():
            if v["sign up"].lower() == "yes":
                yes += 1
            elif v["sign up"].lower() == "no":
                no += 1
        res2.append(yes / (yes + no))
        res2.append(no / (yes + no))

    res3 = []
    for sim in sim3:
        anal_d = sim.analysis_dict
        yes = 0
        no = 0
        for k, v in anal_d.items():
            if v["sign up"].lower() == "yes":
                yes += 1
            elif v["sign up"].lower() == "no":
                no += 1
        res3.append(yes / (yes + no))
        res3.append(no / (yes + no))

    res4 = []
    for sim in sim4:
        anal_d = sim.analysis_dict
        yes = 0
        no = 0
        for k, v in anal_d.items():
            if v["sign up"].lower() == "yes":
                yes += 1
            elif v["sign up"].lower() == "no":
                no += 1
        res4.append(yes / (yes + no))
        res4.append(no / (yes + no))

    # 示例数据：每个部分的比例
    proportions = {
        "Without All": res2,  # 红色部分和绿色部分的比例
        "Without Reputation With Gossip": res3,
        "With Reputation Without Gossip": res1,
        "With All": res4,
    }

    # 颜色和标签
    colors = ["red", "green"]
    labels = ["Not Sign Up", "Sign Up"]

    # 创建图形
    fig, ax = plt.subplots(figsize=(12, 6))

    # 纵坐标标签和位置
    y_labels = list(proportions.keys())
    y_pos = np.arange(len(y_labels))

    # 绘制每一部分的柱状图
    for i, (label, data) in enumerate(proportions.items()):
        left = 0  # 起始位置
        for j, proportion in enumerate(data):
            ax.barh(
                y_pos[i],
                proportion,
                alpha=0.5,
                color=colors[j],
                edgecolor="black",
                left=left,
                label=labels[j] if i == 0 else "",
            )
            left += proportion

    # 设置纵轴
    ax.set_yticks(y_pos)
    ax.set_yticklabels(y_labels)

    # 设置横轴
    ax.set_xticks(np.linspace(0, 1, 6))
    ax.set_xlabel("Proportion")

    # 移除上边和右边的边框
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    # 添加图例
    ax.legend()

    # 设置标题
    ax.set_title("Participation Frequency by Category")

    # 显示图形
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    # merge_last_sim_data_and_save()
    # data_test_3()
    # merge_last_sim_data_and_save()
    # get_data_dict()
    # data_dict_ablation, data_dict, x_original = get_data_dict()
    # data_dict_ablation, data_dict, x_original = load_data_dict()
    # print(data_dict_ablation)
    # print(data_dict)
    # # data_test()
    # draw_line_smooth(data_dict, x_original, False)
    # draw_line_with_error_bands(data_dict, x_original, False)

    # draw_line_smooth(data_dict_ablation, x_original)
    # draw_line_with_error_bands(data_dict_ablation, x_original)
    # draw_network()
    # draw_line2()
    draw_line3()
    # draw_line4()
    # draw_modularity()
    # draw_cluster_repu_ava_t()
    # draw_sign_rate()
    pass
