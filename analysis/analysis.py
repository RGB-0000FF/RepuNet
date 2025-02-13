import json
import networkx as nx
import os
import sys
import matplotlib.pyplot as plt
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from utils import *
from persona.persona import Persona


def get_d_connect(init_persona, G):
    d_connect_list = []
    for edge in G.edges():
        if edge[0] == init_persona.name:
            if G.has_edge(edge[1], init_persona.name):
                d_connect_list.append(edge[1])
    return d_connect_list


def get_gossip_count(ps, persona):
    count = 0
    for _, p in ps.items():
        gossips = p.gossipDB.gossips
        # print(gossips)
        for gossip in gossips:
            full_name = gossip["complained name"]
            if full_name == persona:
                count += 1
    return count


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
            try:
                if "numerical record" in reputation[f"{input}_{target_persona.scratch.ID}"].keys():
                    repu_score = reputation[f"{input}_{target_persona.scratch.ID}"][
                        "numerical record"
                    ]
                elif "numerical_record" in reputation[f"{input}_{target_persona.scratch.ID}"].keys():
                    repu_score = reputation[f"{input}_{target_persona.scratch.ID}"][
                        "numerical_record"
                    ]
                else:
                    repu_score = reputation[f"{input}_{target_persona.scratch.ID}"][
                        " numerical record"
                    ]
            except:
                print(reputation[f"{input}_{target_persona.scratch.ID}"])
                raise KeyError
            
            scores = repu_score.replace("(", "").replace(")", "").split(",")
            try:
                s1 = float(scores[4])
            except:
                s1 = 0
            try:
                s2 = float(scores[3])
            except:
                s2 = 0
            try:
                s3 = float(scores[1])
            except:
                s3 = 0
            try:
                s4 = float(scores[0])
            except:
                s4 = 0
            score = s1 + s2 - s3 - s4
            if score > 1:
                score = 1
            elif score < -1:
                score = -1
            num += score
    if count == 0:
        return 0
    return round((num / count), 3)


class Analysis:
    def __init__(self, sim_code, sim, with_reputation=True, with_gossip=True):
        self.sim_code = f"{sim_code}"
        sim_folder = f"{fs_storage}/{self.sim_code}"
        self.with_reputation = with_reputation
        self.with_gossip = with_gossip

        with open(f"{sim_folder}/reverie/meta.json") as json_file:
            reverie_meta = json.load(json_file)

        self.step = reverie_meta["step"]
        self.personas = dict()
        self.analysis_dict = dict()
        self.G = dict()

        for persona_name in reverie_meta["persona_names"]:
            persona_folder = f"{sim_folder}/personas/{persona_name}"
            curr_persona = Persona(persona_name, persona_folder, self.with_reputation)
            self.personas[persona_name] = curr_persona
        if self.with_reputation and sim and "invest" in sim:
            self.set_graph_invest()
        elif self.with_reputation and sim and "sign" in sim:
            self.set_graph_sign_up()

        if not self.with_reputation:
            self._set_graph_without()

        if "invest" in sim:
            self._set_analysis_dict_invest()
        elif "sign" in sim:
            self._set_analysis_dict_sign_up()

    def set_graph_sign_up(self):
        self._set_graph_r()

    def set_graph_invest(self):
        self._set_graph_i()
        self._set_graph_t()

    def _set_graph_without(self):
        # trustee graph
        G = nx.DiGraph()
        for _, persona in self.personas.items():
            if not G.has_node(persona.name):
                G.add_nodes_from([persona.name])
            black_list = list(persona.scratch.relationship["black_list"])
            bind_list = list(persona.scratch.relationship["bind_list"])
            for bind in bind_list:
                if bind not in black_list:
                    if not G.has_node(bind):
                        G.add_nodes_from([bind])
                    G.add_edges_from([(persona.name, bind)])
        self.G["without_repu"] = G

    def _set_graph_r(self):
        # investor graph
        G = nx.DiGraph()
        for _, persona in self.personas.items():
            if not G.has_node(persona.name):
                G.add_nodes_from([persona.name])
            black_list = list(persona.scratch.relationship["black_list"])
            bind_list = list(persona.scratch.relationship["bind_list"])
            for bind in bind_list:
                if bind[0] not in black_list:
                    if not G.has_node(bind[0]):
                        G.add_nodes_from([bind[0]])
                    G.add_edges_from([(persona.name, bind[0])])
        self.G["resident"] = G

    def _set_graph_i(self):
        # investor graph
        G = nx.DiGraph()
        for _, persona in self.personas.items():
            if not G.has_node(persona.name):
                G.add_nodes_from([persona.name])
            black_list = list(persona.scratch.relationship["black_list"])
            bind_list = list(persona.scratch.relationship["bind_list"])
            for bind in bind_list:
                if bind[0] not in black_list and bind[1] != "trustee":
                    if not G.has_node(bind[0]):
                        G.add_nodes_from([bind[0]])
                    G.add_edges_from([(persona.name, bind[0])])
        self.G["investor"] = G

    def _set_graph_t(self):
        # trustee graph
        G = nx.DiGraph()
        for _, persona in self.personas.items():
            if not G.has_node(persona.name):
                G.add_nodes_from([persona.name])
            black_list = list(persona.scratch.relationship["black_list"])
            bind_list = list(persona.scratch.relationship["bind_list"])
            for bind in bind_list:
                if bind[0] not in black_list and bind[1] != "investor":
                    if not G.has_node(bind[0]):
                        G.add_nodes_from([bind[0]])
                    G.add_edges_from([(persona.name, bind[0])])
        self.G["trustee"] = G

    def _save_temp_invest_s2(self, name1, name2):
        with open(
            f"{fs_storage}/{self.sim_code}/investment results/investment_results_{self.step}.txt",
            "r",
        ) as f:
            curr_all_investment_results = f.read()
            print(self.step)
            curr_all_investment_results = curr_all_investment_results.split(
                "End of Investment"
            )
            for investment_result in curr_all_investment_results:
                investment_results = investment_result.split("Stage  1")
                if len(investment_results) != 2:
                    for investment_result in investment_results:
                        if name1 in investment_result and name2 in investment_result:
                            Trustee = (
                                investment_result.split("| Trustee: ")[-1]
                                .split(":")[0]
                                .strip()
                            )
                            Investor = (
                                investment_result.split("| Investor: ")[-1]
                                .split(":")[0]
                                .strip()
                            )
                            return Trustee, Investor

                if name1 in investment_result and name2 in investment_result:
                    Trustee = (
                        investment_result.split("| Trustee: ")[-1].split(":")[0].strip()
                    )
                    Investor = (
                        investment_result.split("| Investor: ")[-1]
                        .split(":")[0]
                        .strip()
                    )
                    return Trustee, Investor

    def _save_gossip_willing(self, investor, trustee):
        with open(
            f"{fs_storage}/{self.sim_code}/investment results/investment_results_{self.step}.txt",
            "r",
        ) as f:
            curr_all_investment_results = f.read()
            curr_all_investment_results = curr_all_investment_results.split(
                "End of Investment"
            )
            for investment_result in curr_all_investment_results:
                if investor in investment_result and trustee in investment_result:
                    trustee_w = (
                        investment_result.split(
                            f"| Trustee: {trustee}: gossip willing"
                        )[-1]
                        .split(".")[0]
                        .strip()
                        .lower()
                    )
                    investor_w = (
                        investment_result.split(
                            f"| Investor: {investor}: gossip willing"
                        )[-1]
                        .split(".")[0]
                        .strip()
                        .lower()
                    )
                    return trustee_w, investor_w

    def _set_analysis_dict_sign_up(self):
        for persona_name, persona in self.personas.items():
            self.analysis_dict[persona_name] = dict()
            choices = persona.associativeMemory.event_id_to_node
            count = 0
            for _, last_choice in choices.items():
                sign_up = ""
                if type(last_choice) is dict:
                    last_choice = last_choice["description"]
                else:
                    last_choice = last_choice.toJSON()["description"]
                last_choice = last_choice.splitlines()
                for line in last_choice:
                    if persona.name in line:
                        # last choice of the persona in memory
                        sign_up = line.split(":")[-1].strip()
                        if sign_up.lower() == "yes":
                            count += 1

            sign_up = ""
            if choices:
                last_choice = persona.associativeMemory.get_latest_event()
                if type(last_choice) is dict:
                    last_choice = last_choice["description"]
                else:
                    last_choice = last_choice.toJSON()["description"]
                last_choice = last_choice.splitlines()
                for line in last_choice:
                    if persona.name in line:
                        # last choice of the persona in memory
                        sign_up = line.split(":")[-1].strip()
                self.analysis_dict[persona_name]["sign up"] = sign_up
                self.analysis_dict[persona_name]["sign up rate"] = round(
                    (count / len(choices)), 3
                )

            if self.with_gossip:
                # print(self.step, persona.name)
                self.analysis_dict[persona_name]["gossip_count"] = get_gossip_count(
                    self.personas, persona.name
                )

            if self.with_reputation:
                self.analysis_dict[persona_name]["with_reputation"] = True
                d_connect = get_d_connect(persona, self.G["resident"])
                self.analysis_dict[persona_name]["d_connect"] = d_connect
                self.analysis_dict[persona_name]["reputation score"] = (
                    get_reputation_score(persona, "resident", self.personas)
                )
                self.analysis_dict[persona_name]["reputation"] = (
                    persona.reputationDB.get_all_reputations(
                        "Resident", persona.scratch.ID, True
                    )
                )
            else:
                self.analysis_dict[persona_name]["with_reputation"] = False
                d_connect = get_d_connect(persona, self.G["without_repu"])
                self.analysis_dict[persona_name]["d_connect"] = d_connect
            

    def _set_analysis_dict_invest(self):
        for persona_name, persona in self.personas.items():
            self.analysis_dict[persona_name] = dict()
            if self.with_gossip:
                    # print(self.step, persona.name)
                    self.analysis_dict[persona_name]["gossip_count"] = get_gossip_count(
                        self.personas, persona.name
                    )
            if self.with_reputation:
                self.analysis_dict[persona_name]["reputation score"]=dict()
                self.analysis_dict[persona_name]["reputation score"]["trustee"] = (
                    get_reputation_score(persona, "trustee", self.personas)
                )
                self.analysis_dict[persona_name]["reputation score"]["investor"] = (
                    get_reputation_score(persona, "investor", self.personas)
                )
                self.analysis_dict[persona_name]["reputation"] = {
                    "Investor": self.personas[
                        persona_name
                    ].reputationDB.get_all_reputations(
                        "Investor", self.personas[persona_name].scratch.ID, True
                    ),
                    "Trustee": self.personas[
                        persona_name
                    ].reputationDB.get_all_reputations(
                        "Trustee", self.personas[persona_name].scratch.ID, True
                    ),
                }
            self.analysis_dict[persona_name]["resources_unit"] = (
                persona.scratch.resources_unit
            )
            investment_event = persona.associativeMemory.get_latest_event()
            if "failed" in investment_event["description"].lower():
                self.analysis_dict[persona_name]["investment_status"] = "failed"
                if "Investor is " in investment_event["description"]:
                    investor = (
                        investment_event["description"]
                        .split("Investor is ")[-1]
                        .split(" and")[0]
                        .strip()
                    )
                    trustee = (
                        investment_event["description"]
                        .split("Trustee is ")[-1]
                        .split(".")[0]
                        .strip()
                    )
                else:
                    trustee, investor = self._save_temp_invest_s2(
                        investment_event["subject"], investment_event["object"]
                    )
                self.analysis_dict[persona_name]["investor"] = investor
                self.analysis_dict[persona_name]["trustee"] = trustee
            else:
                self.analysis_dict[persona_name]["investment_status"] = "success"
                investor = (
                    investment_event["description"]
                    .split("investor is ")[-1]
                    .split(",")[0]
                    .strip()
                )
                trustee = (
                    investment_event["description"]
                    .split(", trustee is ")[-1]
                    .split("stage 1")[0]
                    .strip()
                )
                self.analysis_dict[persona_name]["investor"] = investor
                self.analysis_dict[persona_name]["trustee"] = trustee
                self.analysis_dict[persona_name]["trustee_plan"] = (
                    investment_event["description"]
                    .split("trustee_plan is ")[-1]
                    .split("stage 2:")[0]
                    .strip()
                )
                if "stage 2" in investment_event["description"]:
                    a_unit = (
                        investment_event["description"]
                        .split("stage 2: investor invests ")[-1]
                        .split(" units")[0]
                        .strip()
                    )
                else:
                    a_unit = self._save_temp_invest_s2(investor, trustee)
                self.analysis_dict[persona_name]["investor_invests_unit"] = a_unit
                self.analysis_dict[persona_name]["trustee_allocation"] = eval(
                    investment_event["description"]
                    .split("stage 3: trustee_allocation is ")[-1]
                    .split(", and reported_investment_outcome is")[0]
                    .strip()
                )
                t_gossip_willing, i_gossip_willing = self._save_gossip_willing(
                    investor, trustee
                )
                self.analysis_dict[persona_name]["gossip_willing"] = {
                    "investor": i_gossip_willing,
                    "trustee": t_gossip_willing,
                }
                


# def get_all_sim_info(sim_folder, sim, with_reputation=True, limit=False):
#     sim_steps = []
#     sims = []
#     for sim_code in os.listdir(f"{fs_storage}/{sim_folder}"):
#         step = int(sim_code.split("_")[-1])
#         if step > limit[1] or step < limit[0]:
#             continue
#         sim_steps.append(sim_code)
#         sim_steps.sort(key=lambda x: int(x.split("_")[1]))
#     for sim_step in sim_steps:
#         print(sim_step)
#         sims.append(Analysis(f"{sim_folder}/{sim_step}", sim, with_reputation))
#     return sims


import os
from concurrent.futures import ProcessPoolExecutor


# ✅ 全局函数，ProcessPoolExecutor 可以 pickle 这个函数
def create_analysis(args):
    sim_folder, sim_step, sim, with_reputation = args
    return Analysis(f"{sim_folder}/{sim_step}", sim, with_reputation)


def get_all_sim_info(sim_folder, sim, with_reputation=True, limit=False):
    sim_steps = []

    with os.scandir(f"{fs_storage}/{sim_folder}") as entries:
        for entry in entries:
            if entry.is_dir():
                parts = entry.name.split("_")
                try:
                    step = int(parts[-1])
                    if limit and (step < limit[0] or step > limit[1]):
                        continue
                    sim_steps.append((entry.name, step))
                except ValueError:
                    print(f"跳过无法解析的文件夹: {entry.name}")

    sim_steps.sort(key=lambda x: x[1])
    sim_steps = [step[0] for step in sim_steps]

    # max_workers = os.cpu_count() * 2  # 🚀 让 CPU 充分利用
    # print(f"使用 {max_workers} 个进程并行加载数据...")

    # ✅ 使用全局函数 create_analysis 进行多进程计算
    with ProcessPoolExecutor(max_workers=24) as executor:
        sims = list(
            executor.map(
                create_analysis,
                [(sim_folder, step, sim, with_reputation) for step in sim_steps],
            )
        )

    return sims


# def get_all_sim_info(sim_folder, sim, with_reputation=True, limit=False):
#     sim_steps = []

#     # 使用 os.scandir() 提高文件遍历性能
#     with os.scandir(f"{fs_storage}/{sim_folder}") as entries:
#         for entry in entries:
#             if entry.is_dir():  # 只处理文件夹
#                 parts = entry.name.split("_")
#                 try:
#                     step = int(parts[-1])  # 确保 step 是数字
#                     if limit and (step < limit[0] or step > limit[1]):
#                         continue
#                     sim_steps.append((entry.name, step))
#                 except ValueError:
#                     print(f"跳过无法解析的文件夹: {entry.name}")

#     # 直接排序，避免重复 split
#     sim_steps.sort(key=lambda x: x[1])
#     sim_steps = [step[0] for step in sim_steps]  # 只保留文件名

#     # 并行创建 Analysis 实例，加大线程池 worker 数量
#     def create_analysis(sim_step):
#         return Analysis(f"{sim_folder}/{sim_step}", sim, with_reputation)

#     max_threads = min(16, os.cpu_count() * 2)  # 选择合理的线程数
#     # print(f"使用 {max_threads} 个线程加载数据...")

#     with ProcessPoolExecutor(max_workers=max_threads) as executor:
#         sims = list(executor.map(create_analysis, sim_steps))

#     return sims


if __name__ == "__main__":
    # sims1 = get_all_sim_info("investment_s7_with_repu_without_gossip")
    # sims2 = get_all_sim_info("investment_s8_without_repu_gossip")
    # sims3 = get_all_sim_info("investment_s9_without_repu_with_gossip")
    sims4 = get_all_sim_info("sign_s22_with_all", "sign",limit=(191,201))
    # count = 0
    # for sim in sims1:
    #     count += 1
    #     with open(f"./with_repu_without_gossip/analysis_{count}.json", "w") as f:
    #         json.dump(sim.analysis_dict, f, indent=4)
    # count = 0
    # for sim in sims2:
    #     count += 1
    #     with open(f"./without_repu_without_gossip/analysis_{count}.json", "w") as f:
    #         json.dump(sim.analysis_dict, f, indent=4)
    # count = 0
    # for sim in sims3:
    #     count += 1
    #     with open(f"./without_repu_with_gossip/analysis_{count}.json", "w") as f:
    #         json.dump(sim.analysis_dict, f, indent=4)
    count = 190
    for sim in sims4:
        count += 1
        with open(f"./analysis_return/sign_all/analysis_{count}.json", "w") as f:
            json.dump(sim.analysis_dict, f, indent=4)   
    