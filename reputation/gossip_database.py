import datetime
import json
import sys
from .global_methods import *

sys.path.append("../")


def check_if_gossip_sign_up(persona):
    if (
        persona.scratch.gossip_chat
        and persona.scratch.curr_complain_info["after_sign_up"]
    ):
        return True
    return False


class GossipDB:
    gossips: list
    gossips_count: int
    gossips_incredible_count: int

    def __init__(self, f_saved) -> None:
        self.gossips = []
        self.gossips_count = 0
        self.gossips_incredible_count = 0
        print(f"INIT GossipDB: {f_saved}")

        if check_if_file_exists(f"{f_saved}/gossip_database.json"):
            print("GNS FUNCTION: <GossipDB__init__>")

            gossips_load = json.load(open(f"{f_saved}/gossip_database.json"))
            self.gossips_count = len(gossips_load)
            self.gossips = gossips_load

            for gossip in self.gossips:
                if gossip["credibility level"] in ["very uncredible", "uncredible"]:
                    self.gossips_incredible_count += 1

        else:
            print(
                f"INIT GossipDB: {f_saved}/gossip_database.json could not find")

    def save(self, gossip_folder):
        with open(gossip_folder + "/gossip_database.json", "w") as f:
            json.dump(self.gossips, f, indent=4)

    def add_gossip(self, gossips, curr_step):
        print("GossipDB.add_gossip()")
        for gossip in gossips:
            gossip["created_at"] = curr_step
            self.gossips.append(gossip)

    def get_target_gossips_info(self, target_persona):
        infos = ""
        weight = ""
        print("GossipDB.get_target_gossips_info()")
        for _, gossip in self.gossips.items():
            # find
            # And only use the gossip that active time is in 30min scope
            active_time = datetime.datetime.strptime(
                gossip["active_time"], "%B %d, %Y, %H:%M:%S"
            )
            if (target_persona.scratch.curr_time - active_time) <= datetime.timedelta(
                minutes=30
            ):
                if gossip["complained ID"] == target_persona.scratch.ID:
                    infos = gossip["gossip info"]
                    weight = gossip["credibility level"]
                    break
        return infos, weight
