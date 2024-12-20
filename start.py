import json
import shutil
import traceback
import errno
import networkx as nx

from task.investment.investment import *
from utils import *

from persona.persona import Persona


class Creation:
    def __init__(self, sim_code):
        self.sim_code = f"{sim_code}"
        sim_folder = sim_folder = f"{fs_storage}/{self.sim_code}"

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

    def save(self):
        sim_folder = f"{fs_storage}/{self.sim_code}"
        reverie_meta = dict()
        reverie_meta["persona_names"] = list(self.personas.keys())
        reverie_meta["step"] = self.step
        reverie_meta_f = f"{sim_folder}/reverie/meta.json"
        with open(reverie_meta_f, "w") as outfile:
            outfile.write(json.dumps(reverie_meta, indent=2))

        # Save the personas.
        for persona_name, persona in self.personas.items():
            save_folder = f"{sim_folder}/personas/{persona_name}"
            persona.associativeMemory.base_path = (
                f"{save_folder}/memory/associative_memory"
            )
            persona.scratch.curr_step += 1
            persona.save(save_folder)
            # save reputation and gossip
            reputation_folder = f"{sim_folder}/personas/{persona_name}/reputation"
            persona.reputationDB.save(reputation_folder)
            gossip_folder = f"{sim_folder}/personas/{persona_name}/reputation"
            persona.gossipDB.save(gossip_folder)

    def start_server(self, int_counter):
        while True:
            # Done with this iteration if <int_counter> reaches 0.
            if int_counter == 0:
                break

            self.set_graph()
            origin_sim_folder = f"{fs_storage}/{self.sim_code}"
            if os.path.exists(f"{origin_sim_folder}/investment results"):
                shutil.rmtree(f"{origin_sim_folder}/investment results")


            print(f"sim_code: {self.sim_code}-----------------------------------------------")
            pairs = pair_each(self.personas, self.G)

            for pair in pairs:
                start_investment(
                    pair,
                    self.personas,
                    self.G,
                    f"{fs_storage}/{self.sim_code}/investment results",
                )

            self.step += 1
            origin_sim_folder = f"{fs_storage}/{self.sim_code}"
            new_sim_code = self.sim_code.split("/")[0] + f"/step_{self.step}"
            new_sim_folder = f"{fs_storage}/{new_sim_code}"
            self.sim_code = new_sim_code
            # copy the investment results to the new simulation folder
            shutil.copytree(
                f"{origin_sim_folder}",
                f"{new_sim_folder}",
            )
            shutil.rmtree(f"{new_sim_folder}/investment results")

            self.save()
            int_counter -= 1

    def open_server(self):
        """
        Open up an interactive terminal prompt that lets you run the simulation
        step by step and probe agent state.

        INPUT
          None
        OUTPUT
          None
        """
        print("Note: The agents in this simulation package are computational")
        print("constructs powered by generative agents architecture and LLM. We")
        print("clarify that these agents lack human-like agency, consciousness,")
        print("and independent decision-making.\n---")

        # <sim_folder> points to the current simulation folder.
        sim_folder = f"{fs_storage}/{self.sim_code}"

        while True:
            sim_folder = f"{fs_storage}/{self.sim_code}"
            sim_command = input("Enter option: ")
            sim_command = sim_command.strip()
            ret_str = ""

            try:
                if sim_command.lower() in ["f", "fin", "finish", "save and finish"]:
                    # Finishes the simulation environment and saves the progress.
                    # Example: fin
                    # self.save()
                    print("Simulation finished.")
                    break

                elif sim_command.lower() == "exit":
                    # Finishes the simulation environment but does not save the progress
                    # and erases all saved data from current simulation.
                    # Example: exit
                    shutil.rmtree(sim_folder)
                    break

                elif sim_command.lower() == "save":
                    # Saves the current simulation progress.
                    # Example: save
                    self.save()

                elif sim_command[:3].lower() == "run":
                    # Runs the number of steps specified in the prompt.
                    # Example: run 1000
                    int_count = int(sim_command.split()[-1])
                    server.start_server(int_count)

                print(ret_str)

            except Exception as e:
                print(e)
                traceback.print_exc()
                print("Error.")
                pass


if __name__ == "__main__":
    origin = input("Enter the name of the forked simulation: ").strip()
    # cwd = os.getcwd()
    server = Creation(origin)
    server.open_server()
