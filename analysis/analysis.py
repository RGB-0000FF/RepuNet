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
    def __init__(self, sim_code):
        self.sim_code = f"{sim_code}"
        sim_folder = f"{fs_storage}/{self.sim_code}"

        with open(f"{sim_folder}/reverie/meta.json") as json_file:
            reverie_meta = json.load(json_file)

        self.step = reverie_meta["step"]
        self.personas = dict()
        self.analysis_dict = dict()

        for persona_name in reverie_meta["persona_names"]:
            persona_folder = f"{sim_folder}/personas/{persona_name}"
            curr_persona = Persona(persona_name, persona_folder)
            self.personas[persona_name] = curr_persona
        self.G = self._set_graph()
        self._set_analysis_dict()

    def _save_temp_invest_s2(self, investor, trustee):
        with open(
            f"{fs_storage}/{self.sim_code}/investment results/investment_results_{self.step}.txt",
            "w",
        ) as f:
            curr_all_investment_results = f.read()
            curr_all_investment_results = curr_all_investment_results.split(
                "End of Investment"
            )
            for investment_result in curr_all_investment_results:
                if (
                    investor in investment_result
                    and trustee in investment_result
                    and "because they are in black list" not in investment_result
                    and "decided Refuse" not in investment_result
                ):
                    a_unit = (
                        investment_result.split(
                            f"Investor: {investor}: investor decided Accept. Allocation "
                        )[-1]
                        .split(" units")[0]
                        .strip()
                    )
                    return a_unit

    def _set_analysis_dict(self):
        for persona_name, persona in self.personas.items():
            self.analysis_dict[persona_name] = dict()
            self.analysis_dict[persona_name]["resources_unit"] = (
                persona.scratch.resources_unit
            )
            investment_event = persona.associativeMemory.get_latest_event()
            if "failed" in investment_event.description.lower():
                self.analysis_dict[persona_name]["investment_status"] = "failed"
            else:
                self.analysis_dict[persona_name]["investment_status"] = "success"
                investor = (
                    investment_event.split("investor is ")[-1].split(",")[0].strip()
                )
                trustee = (
                    investment_event.split(", trustee is ")[-1]
                    .split("stage 1")[0]
                    .strip()
                )
                self.analysis_dict[persona_name]["investor"] = investor
                self.analysis_dict[persona_name]["trustee"] = trustee
                if "stage 2" in investment_event.description:
                    a_unit = (
                        investment_event.description.split(
                            "stage 2: investor invests "
                        )[-1]
                        .split(" units")[0]
                        .strip()
                    )
                else:
                    a_unit = self._save_temp_invest_s2(investor, trustee)
                self.analysis_dict[persona_name]["investor_invests_unit"] = a_unit
                self.analysis_dict[persona_name]["trustee_allocation"] = json.dumps(
                    investment_event.description.split(
                        "stage 3: trustee_allocation is "
                    )[-1]
                    .split(", and reported_investment_outcome is")[0]
                    .strip()
                )

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
        sim_steps.append(sim_code)
        sim_steps.sort(key=lambda x: int(x.split("_")[1]))
    for sim_step in sim_steps:
        sims.append(Analysis(f"{sim_folder}/{sim_step}"))
    return sims


sims = get_all_sim_info("investment_s1")
