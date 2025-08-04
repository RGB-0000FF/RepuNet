from collections import deque
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

    def __init__(self, name, folder_mem_saved=False, with_reputation=False, investment=None):
        self.name = name

        scratch_saved = f"{folder_mem_saved}/memory/scratch.json"
        self.scratch = Scratch(scratch_saved, investment)

        gossip_saved = f"{folder_mem_saved}/reputation"
        self.gossipDB = GossipDB(gossip_saved)
        if with_reputation:
            reputation_saved = f"{folder_mem_saved}/reputation"
            self.reputationDB = ReputationDB(reputation_saved)
        else:
            self.reputationDB = None

        associative_memory_saved = f"{folder_mem_saved}/memory/associative_memory"
        self.associativeMemory = AssociativeMemory(associative_memory_saved, do_load=True)
        self.interaction_memory = {"investor": [], "trustee": []}

    def save(self, save_folder):
        scratch_folder = f"{save_folder}/memory/scratch.json"
        self.scratch.save(scratch_folder)
        self.associativeMemory.save()
        reputation_folder = f"{save_folder}/reputation"
        if self.reputationDB:
            self.reputationDB.save(reputation_folder)
        self.gossipDB.save(reputation_folder)
