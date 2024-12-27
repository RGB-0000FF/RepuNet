import json
import networkx as nx
import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from persona.persona import Persona
from utils import *


class Analysis:
    def __init__(self, sim_code, with_reputation=True):
        self.sim_code = f"{sim_code}"
        sim_folder = f"{fs_storage}/{self.sim_code}"
        self.with_reputation = with_reputation

        with open(f"{sim_folder}/reverie/meta.json") as json_file:
            reverie_meta = json.load(json_file)

        self.step = reverie_meta["step"]
        self.personas = dict()
        self.analysis_dict = dict()

        for persona_name in reverie_meta["persona_names"]:
            persona_folder = f"{sim_folder}/personas/{persona_name}"
            curr_persona = Persona(persona_name, persona_folder, self.with_reputation)
            self.personas[persona_name] = curr_persona
        self.G = self._set_graph()
        self._set_analysis_dict()

    def _save_temp_invest_s2(self, name1, name2):
        with open(
            f"{fs_storage}/{self.sim_code}/investment results/investment_results_{self.step}.txt",
            "r",
        ) as f:
            curr_all_investment_results = f.read()
            curr_all_investment_results = curr_all_investment_results.split(
                "End of Investment"
            )
            for investment_result in curr_all_investment_results:
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

    def _set_analysis_dict(self):
        for persona_name, persona in self.personas.items():
            self.analysis_dict[persona_name] = dict()
            if self.with_reputation:
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
                i_gossip_willing, t_gossip_willing = self._save_gossip_willing(
                    investor, trustee
                )
                self.analysis_dict[persona_name]["gossip_willing"] = {
                    "investor": i_gossip_willing,
                    "trustee": t_gossip_willing,
                }

    def _set_graph(self):
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
        return G


def get_all_sim_info(sim_folder):
    sim_steps = []
    sims = []
    for sim_code in os.listdir(f"{fs_storage}/{sim_folder}"):
        if sim_code == "step_0":
            continue
        sim_steps.append(sim_code)
        sim_steps.sort(key=lambda x: int(x.split("_")[1]))
    for sim_step in sim_steps:
        sims.append(Analysis(f"{sim_folder}/{sim_step}"))
    return sims


if __name__ == "__main__":
    sims1 = get_all_sim_info("investment_s2")
    # count = 0
    # for sim in sims1:
    #     count += 1
    #     with open(f"with_repu/analysis_{count}.json", "w") as f:
    #         json.dump(sim.analysis_dict, f, indent=4)
    # sims2 = get_all_sim_info("investment_s2")
    # count = 0
    # for sim in sims2:
    #     count += 1
    #     with open(f"without_repu/analysis_{count}.json", "w") as f:
    #         json.dump(sim.analysis_dict, f, indent=4)
