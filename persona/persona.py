from .memory_structures.scratch import Scratch
from reputation.gossip_database import GossipDB
from reputation.reputation_database import ReputationDB
from .memory_structures.associative_memory import AssociativeMemory


class Persona:
    name: str
    scratch: Scratch
    reputationDB: ReputationDB
    gossipDB: GossipDB
    associativeMemory: AssociativeMemory

    def __init__(self, name, folder_mem_saved=False, with_reputation=False):
        self.name = name

        scratch_saved = f"{folder_mem_saved}/memory/scratch.json"
        self.scratch = Scratch(scratch_saved)

        gossip_saved = f"{folder_mem_saved}/reputation"
        self.gossipDB = GossipDB(gossip_saved)
        if with_reputation:
            reputation_saved = f"{folder_mem_saved}/reputation"
            self.reputationDB = ReputationDB(reputation_saved)
        else:
            self.reputationDB = None

        associative_memory_saved = f"{folder_mem_saved}/memory/associative_memory"
        self.associativeMemory = AssociativeMemory(
            associative_memory_saved, do_load=True
        )
        self.interaction_memory={"investor":[],"trustee":[]}

    def save(self, save_folder):
        scratch_folder = f"{save_folder}/memory/scratch.json"
        self.scratch.save(scratch_folder)
        self.associativeMemory.save()
        reputation_folder = f"{save_folder}/reputation"
        if self.reputationDB:
            self.reputationDB.save(reputation_folder)
        self.gossipDB.save(reputation_folder)
        
    def get_latest_memory_list(self):
        id_list=list(self.associativeMemory.event_id_to_node.keys())
        sorted_id_list=sorted(id_list,reverse=False)
        memory_list_investor=[]
        memory_list_trustee=[]
        for id in sorted_id_list:
            # if self.event_id_to_node[id]["description"].split("investor is")[-1].split("trustee is")[0].strip().strip(",")
            ob=self.associativeMemory.event_id_to_node[id]
            if type(ob) is dict:
                des_str=ob["description"]
            else:
                des_str=ob.description
                
            if "Failed" in des_str:
                if des_str.split("Investor is")[1].split("and")[0].strip()==self.name:
                    memory_list_investor.append(des_str)
                else:
                    memory_list_trustee.append(des_str)
            elif "Success" in des_str:
                if des_str.split("investor is")[1].split("trustee is")[0].strip().strip(",")==self.name:
                    memory_list_investor.append(des_str)
                else:
                    memory_list_trustee.append(des_str)
        if len(memory_list_investor)>=5:
            memory_list_investor=memory_list_investor[-5:]
        if len(memory_list_trustee)>=5:
            memory_list_trustee=memory_list_trustee[-5:]
        return memory_list_investor,memory_list_trustee
    def update_interaction_memory(self,role,memory):
        if len(self.interaction_memory[role])>=1:
            self.interaction_memory[role].pop(0)
        self.interaction_memory[role].append(memory)
        
    def get_interaction_memory(self,role):
        return self.interaction_memory[role]
        
