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

        for persona_name in reverie_meta["persona_names"]:
            persona_folder = f"{sim_folder}/personas/{persona_name}"
            curr_persona = Persona(persona_name, persona_folder)
            self.personas[persona_name] = curr_persona
        self.G = self.set_graph()

    def set_graph(self):
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
