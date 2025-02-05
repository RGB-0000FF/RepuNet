from analysis import *
import matplotlib.pyplot as plt
import seaborn as sns
import statsmodels.api as sm
import pandas as pd
import json
from scipy.stats import sem, t
import numpy as np
import networkx as nx

class Linear_Regression:
    def __init__(self, x, y, xlabel, ylabel, title) -> None:
        data = {xlabel: x, ylabel: y}
        self.data = pd.DataFrame(data)
        self.model = None
        self.result = None
        self.xlabel = xlabel
        self.ylabel = ylabel
        self.title = title

    def OLS(self):
        X = self.data[self.xlabel]
        Y = self.data[self.ylabel]
        X = sm.add_constant(X)
        self.model = sm.OLS(Y.astype(float), X.astype(float)).fit()
        self.result = self.model.summary()

    def return_result(self):
        return self.result

    def Logistic(self):
        X = self.data[self.xlabel]
        Y = self.data[self.ylabel]
        X = sm.add_constant(X)
        self.model = sm.Logit(Y, X).fit()
        self.result = self.model.summary()

    def visualization(self, color_list=[], color=None, label=None):
        if color_list:
            data = dict(self.data)
            data1 = {}
            data2 = {}
            x1 = []
            x2 = []
            y1 = []
            y2 = []
            for i in range(len(color_list)):
                if color_list[i] == "red":
                    x1.append(data[self.xlabel][i])
                    y1.append(data[self.ylabel][i])
                elif color_list[i] == "blue":
                    x2.append(data[self.xlabel][i])
                    y2.append(data[self.ylabel][i])
            data1[self.xlabel] = x1
            data1[self.ylabel] = y1
            data2[self.xlabel] = x2
            data2[self.ylabel] = y2

        # plt.figure(figsize=(10, 6))
        if color_list:
            sns.scatterplot(
                x=self.xlabel,
                y=self.ylabel,
                data=data1,
                color="red",
                label="Sign-up",
            )
            sns.scatterplot(
                x=self.xlabel,
                y=self.ylabel,
                data=data2,
                color="blue",
                label="Not Sign-up",
            )
        else:
            sns.scatterplot(x=self.xlabel, y=self.ylabel, data=self.data, color=color)
        x1_vals = self.data[self.xlabel]
        predicted_y = self.model.predict(sm.add_constant(x1_vals))
        plt.plot(x1_vals, predicted_y, color=color, label=label, linewidth=2)
        # plt.title('Trial 1: Linear regression of the Number of Double Positive Connect and reputation')
        # plt.title(self.title)
        # plt.xlabel(self.xlabel)
        # plt.ylabel(self.ylabel)
        # plt.legend()
        # plt.show()


def Gini_coef(analysis_dict):
    resource_list = [i["resources_unit"] for i in analysis_dict.values()]
    if not resource_list:
        return 0

    sorted_values = sorted(resource_list)
    n = len(resource_list)
    cumulative_values = [sum(sorted_values[: i + 1]) for i in range(n)]
    total = cumulative_values[-1]

    gini_sum = sum((i + 1) * value for i, value in enumerate(sorted_values))
    gini_index = (2 * gini_sum) / (n * total) - (n + 1) / n

    return gini_index


def persona_invest_willingness(analysis_dict):
    invest_list = {}
    for i, j in list(analysis_dict.items()):
        if i == j["investor"]:
            if j["investment_status"] == "success":
                deno = (
                    float(j["resources_unit"])
                    - float(j["trustee_allocation"]["Final Allocation"].split("receives")[-1].split("%")[0].strip())/100*float(j["investor_invests_unit"])*2
                    + float(j["investor_invests_unit"])
                )
                if deno:
                    invest_list[i] = float(j["investor_invests_unit"]) / deno
                else:
                    invest_list[i] = 0
            elif j["investment_status"] == "failed":
                invest_list[i] = 0
    return invest_list


def invest_willingness(analysis_dict):
    total_investment = 0
    total_investor_units = 0
    for i, j in list(analysis_dict.items()):
        if i == j["investor"]:
            if j["investment_status"] == "success":
                total_investment += float(j["investor_invests_unit"])
                total_investor_units += (
                    float(j["resources_unit"])
                    - float(j["trustee_allocation"]["Final Allocation"].split("receives")[-1].split("%")[0].strip())/100*float(j["investor_invests_unit"])*2
                    + float(j["investor_invests_unit"])
                )
            elif j["investment_status"] == "failed":
                total_investment += 0
                total_investor_units += float(j["resources_unit"])
    return total_investment / total_investor_units


def persona_income(analysis_dict):
    result = {}
    for i, j in list(analysis_dict.items()):
        result[i] = j["resources_unit"]
    return result


def cheat_coef(analysis_dict):
    cheat_list = {}
    for i, j in list(analysis_dict.items()):
        # if j["investment_status"]=="failed":
        #     if i==j["trustee"]:
        #         cheat_list[i]=0
        if j["investment_status"] == "success":
            if i == j["trustee"]:
                try:
                    p = (
                        float(
                            j["trustee_plan"].split("retains")[-1].split("%")[0].strip()
                        )
                        / 100
                    )
                    p = 1.0 - p
                    cheat_list[i] = max(
                        0,
                        1
                        - (
                            float(j["trustee_allocation"]["Final Allocation"].split("receives")[-1].split("%")[0].strip())/100
                            / (p)
                        ),
                    )
                except:
                    cheat_list[i] = 0
            elif j["investment_status"] == "failed":
                cheat_list[i] = 0
    return cheat_list


def plot(x, y, title, xlabel, ylabel):
    plt.plot(x, y)
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.xlim(0, len(x))
    plt.show()


def plot_distribution(data_list, label, color):
    data = []
    for year, wealth_dict in enumerate(data_list, start=1):
        for person, wealth in wealth_dict.items():
            data.append({"year": year, "person": person, "wealth": wealth})

    df = pd.DataFrame(data)
    # 平均值和95%置信区间
    stats = df.groupby("year")["wealth"].agg(["mean", "count", "std"]).reset_index()
    confidence = 0.95
    h = (
        stats["std"]
        * t.ppf((1 + confidence) / 2, stats["count"] - 1)
        / np.sqrt(stats["count"])
    )

    # plt.figure(figsize=(14, 7))

    plt.plot(stats["year"], stats["mean"], label=label, color=color)

    plt.fill_between(
        stats["year"], stats["mean"] - h, stats["mean"] + h, color=color, alpha=0.5
    )
    # plt.title(title)
    # plt.xlabel(xlabel)
    # plt.ylabel(ylabel)
    # plt.legend()
    # plt.show()


def success_rate_v1(analysis_dict):#计划和实际匹配
    total=0
    satisfy=0
    for i,j in list(analysis_dict.items()):
        if i==j["trustee"]:
            total+=1
            if j["investment_status"]=="success":
                p=float(j["trustee_plan"].split("receives")[-1].split("%")[0].strip())/100
                rate=float(j["trustee_allocation"]["Final Allocation"].split("receives")[-1].split("%")[0].strip())/(float(j['trustee_allocation']["Final Allocation"].split("receives")[-1].split("%")[0].strip())
                                                                                                                     +float(j['trustee_allocation']["Final Allocation"].split("receives")[1].split("%")[0].strip()))
                satisfy+=(rate>=p)
            elif j["investment_status"]=="failed":
                pass
    return satisfy/total if total else 0


# def Satisfaction_rate_v2(analysis_dict):
#     total = 0
#     satisfy = 0
#     for i, j in list(analysis_dict.items()):
#         if j["investment_status"] == "success":
#             if i == j["trustee"]:
#                 total += 1
#                 if (
#                     j["gossip_willing"]["investor"].split(",")[0].lower() == "no"
#                     and j["gossip_willing"]["trustee"].split(",")[0].lower() == "no"
#                 ):
#                     satisfy += 1
#     return satisfy / total if total else 0


def success_rate_v2(analysis_dict):
    total = 0
    success = 0
    for i, j in list(analysis_dict.items()):
        if j["investor"] == i:
            total += 1
            if j["investment_status"] == "success":
                success += 1
    return success / total if total else 0


def get_disconnected_subgraphs(graph):
    # 获取连通分量（无向图）或强连通分量（有向图）
    if isinstance(graph, nx.DiGraph):
        connected_components = nx.strongly_connected_components(graph)
    else:
        connected_components = nx.connected_components(graph)

    # 构造子图列表
    subgraphs = []
    for component in connected_components:
        # 使用节点集合创建子图，并保留节点和边的属性
        subgraph = graph.subgraph(component).copy()
        subgraphs.append(subgraph)
    subgraphs=sorted(subgraphs, key=lambda x: x.number_of_nodes(), reverse=True)
    return subgraphs

def get_node_degrees(graph):
    # 使用 networkx 的 degree 方法获取节点的度
    degree_dict = {node: degree for node, degree in graph.degree()}
    return degree_dict

def get_local_clustering_coefficients(graph):
    return nx.clustering(graph)

def count_bidirectional_edges(graph):
    bidirectional_count = 0
    for node1, node2 in graph.edges():
        if graph.has_edge(node2, node1):  # 检查反向边是否存在
            bidirectional_count += 1
    return bidirectional_count

if __name__ == "__main__":
    sims1 = get_all_sim_info("invest_s27_with_all", "invest",limit=(1,21))
    # sims2 = get_all_sim_info("investment_s12_with_repu_without_gossip", "invest")
    # sims3 = get_all_sim_info("investment_s13_without_repu_with_gossip", "invest", False)
    # sims4 = get_all_sim_info("invest_s26_without_all", "invest", False,limit=(1,101))

    data1 = [cheat_coef(i.analysis_dict) for i in sims1]
    # data2 = [success_rate(i.analysis_dict) for i in sims2]
    # data3 = [success_rate(i.analysis_dict) for i in sims3]
    # data4 = [Satisfaction_rate_v1(i.analysis_dict) for i in sims4]
    # plt.figure(figsize=(14, 7))
    # plt.plot(
    #     range(1, len(data1) + 1),
    #     data1,
    #     label="with reputation and gossip",
    #     color="blue",
    # )
    # plt.scatter(range(1, len(data1) + 1), data1, color="blue")
    # plt.plot(
    #     range(1, len(data2) + 1),
    #     data2,
    #     label="without reputation but with gossip",
    #     color="red",
    # )
    # plt.scatter(range(1, len(data2) + 1), data2, color="red")
    # plt.plot(
    #     range(1, len(data3) + 1),
    #     data3,
    #     label="with repuation but without gossip",
    #     color="orange",
    # )
    # plt.scatter(range(1, len(data3) + 1), data3, color="orange")
    # plt.plot(
    #     range(1, len(data4) + 1),
    #     data4,
    #     label="without reputation and gossip",
    #     color="cyan",
    # )
    # plt.scatter(range(1, len(data4) + 1), data4, color="cyan")
    # plt.title("success rate()".title())
    # plt.xlabel("Round")
    # plt.ylabel("Success rate".capitalize())
    # plt.axis([0,len(data1),0,1])
    # plt.legend()
    # plt.show()

    # l1=Linear_Regression(range(1,len(data1)+1),data1,"Round","Invest willingness","")
    # # # l2=Linear_Regression(range(1,len(data2)+1),data2,"Round","Invest willingness","")
    # # # l3=Linear_Regression(range(1,len(data3)+1),data3,"Round","Invest willingness","")
    # # l4=Linear_Regression(range(1,len(data4)+1),data4,"Round","Invest willingness","")
    # l1.OLS()
    # # # l2.OLS()
    # # # l3.OLS()
    # # l4.OLS()
    # l1.visualization(color="blue",label="With reputation and gossip")
    # # # l2.visualization(color="red",label="Without reputation but with gossip")
    # # # l3.visualization(color="orange",label="With reputation but without gossip")
    # # l4.visualization(color="cyan",label="Without reputation and gossip")
    # plt.title('Overall Invest willingness'.title())
    # plt.xlabel("Round")
    # plt.ylabel("invest willingness".capitalize())
    # plt.axis([0,len(data1),0,1])
    # plt.legend()
    # plt.show()
    # ————————————————————————————————————————
    # ————————————————————————————————————————
    plt.figure(figsize=(14, 7))
    plot_distribution(data1,"with reputation and gossip","blue")
    # plot_distribution(data2,"without reputation but with gossip","red")
    # plot_distribution(data3,"with reputation but without gossip","orange")
    # plot_distribution(data4,"without reputation and gossip","cyan")
    plt.title("cheat coefficient".title())
    plt.xlabel("Round")
    plt.ylabel("cheat coefficient".capitalize())
    plt.legend()
    plt.show()
# #---------------------------------------------------
    # sims1=get_all_sim_info("sign_s22_with_all","sign",limit=(192,201))
    # G_component=[]
    # mean_repu_1=[]
    # mean_repu_2=[]
    # for sim in sims1:
    #     G_component.append(get_disconnected_subgraphs(sim.G["resident"]))
    # # for g in G_component:
    # #     print(len(g))
    # lcc_with_good_repu=[]
    # degree_with_good_repu=[]
    # lcc_with_bad_repu=[]
    # degree_with_bad_repu=[]
    # mean_bid_con_1=[]
    # mean_bid_con_2=[]
    # list_sign_up_rate_1=[]
    # list_sign_up_rate_2=[]
    # for sim in G_component:
    #     cc1=np.mean(list(get_local_clustering_coefficients(sim[0]).values()))
    #     lcc_with_good_repu.append(cc1)
    #     de1=np.mean(list(get_node_degrees(sim[0]).values()))
    #     degree_with_good_repu.append(de1)
    #     sim_copy=sim[1:]
    #     g=nx.DiGraph()
    #     for i in sim_copy:
    #         g=nx.compose(g,i)
    #     cc2=np.mean(list(get_local_clustering_coefficients(g).values()))
    #     de2=np.mean(list(get_node_degrees(g).values()))
    #     lcc_with_bad_repu.append(cc2)
    #     degree_with_bad_repu.append(de2)
    # for i in range(len(sims1)):
    #     list_cluster_1=list(G_component[i][0].nodes())
    #     sim_copy=sim[1:]
    #     g=nx.DiGraph()
    #     for j in sim_copy:
    #         g=nx.compose(g,j)
    #     mean_bid_con_1.append(count_bidirectional_edges(G_component[i][0]))
    #     mean_bid_con_2.append(count_bidirectional_edges(g))
    #     list_cluster_2=list(g.nodes())
    #     repu_cluster_1=[]
    #     repu_cluster_2=[]
    #     sign_up_count_1=0
    #     sign_up_count_2=0
    #     for name in list_cluster_1:
    #         repu_cluster_1.append(sims1[i].analysis_dict[name]["reputation score"])
    #         sign_up_count_1+=(sims1[i].analysis_dict[name]["sign up"]=="Yes")
    #     for name in list_cluster_2:
    #         repu_cluster_2.append(sims1[i].analysis_dict[name]["reputation score"])
    #         sign_up_count_2+=(sims1[i].analysis_dict[name]["sign up"]=="Yes")
    #     mean_repu_1.append(np.mean(repu_cluster_1))
    #     mean_repu_2.append(np.mean(repu_cluster_2))
    #     list_sign_up_rate_1.append(sign_up_count_1)
    #     list_sign_up_rate_2.append(sign_up_count_2)
    # print("good_repu:",np.mean(mean_repu_1),np.std(mean_repu_1))
    # print("good_lcc:",np.mean(lcc_with_good_repu),np.std(lcc_with_good_repu))
    # print("good_degree:",np.mean(degree_with_good_repu),np.std(degree_with_good_repu))
    # print("repu:",np.mean(mean_repu_2),np.std(mean_repu_2))
    # print("lcc:",np.mean(lcc_with_bad_repu),np.std(lcc_with_bad_repu))
    # print("degree:",np.mean(degree_with_bad_repu),np.std(degree_with_bad_repu))
    # print("bidirectional edges(good):",np.mean(mean_bid_con_1),np.std(mean_bid_con_1))
    # print("bidirectional edges:",np.mean(mean_bid_con_2),np.std(mean_bid_con_2))
    # print("sign up rate(good):",np.mean(list_sign_up_rate_1),np.std(list_sign_up_rate_1))
    # print("sign up rate:",np.mean(list_sign_up_rate_2),np.std(list_sign_up_rate_2))
    #-----------------------------
    # mean_degree=[]
    # bid_con=[]
    # mean_cluster_coef=[]
    # sign_up_rate=[]        
    # sims2=get_all_sim_info(sim_folder="sign_s14_without_all",sim="sign",with_reputation=False,limit=(192,201))
    # for sim in sims2:
    #     sign_up_count=0
    #     total_count=0
    #     analysis_dict=sim.analysis_dict
    #     for i,j in analysis_dict.items():
    #         total_count+=1
    #         if j["sign up"]=="Yes":
    #             sign_up_count+=1
    #     sign_up_rate.append(sign_up_count/total_count)
    #     g=sim.G["without_repu"]
    #     mean_degree.append(np.mean(list(get_node_degrees(g).values())))
    #     mean_cluster_coef.append(np.mean(list(get_local_clustering_coefficients(g).values())))
    #     bid_con.append(count_bidirectional_edges(g))
    # print("mean degree:",np.mean(mean_degree),np.std(mean_degree))
    # print("mean cluster coef:",np.mean(mean_cluster_coef),np.std(mean_cluster_coef))
    # print("bidirectional edges:",np.mean(bid_con)/20,np.std(bid_con)/20)
    # print("sign up rate:",np.mean(sign_up_rate),np.std(sign_up_rate))
        
        
    
    