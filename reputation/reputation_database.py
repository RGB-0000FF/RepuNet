import json
import sys
from .global_methods import *


class ReputationDB:
    individual_reputations: dict
    out_of_date_reputations: dict
    reputations_count: int

    def __init__(self, f_saved) -> None:
        self.individual_reputations = dict()
        self.out_of_date_reputations = dict()
        self.reputations_count = 0

        print(f"INIT ReputationDB: {f_saved}")

        if check_if_file_exists(f"{f_saved}/reputation_database.json"):
            print("GNS FUNCTION: <ReputationDB__init__>")

            individual_reputations_load = json.load(
                open(f"{f_saved}/reputation_database.json")
            )
            self.reputations_count = len(individual_reputations_load)
            self.individual_reputations = individual_reputations_load
        else:
            with open(f"{f_saved}/reputation_database.json", "w") as f:
                json.dump({}, f)

        if check_if_file_exists(f"{f_saved}/out_of_date_reputation_database.json"):
            print("GNS FUNCTION: <out_of_date_ReputationDB__init__>")

            out_of_date_reputations = json.load(
                open(f"{f_saved}/out_of_date_reputation_database.json")
            )
            self.out_of_date_reputations = out_of_date_reputations
        else:
            with open(f"{f_saved}/out_of_date_reputation_database.json", "w") as f:
                json.dump({}, f)

    def save(self, reputation_folder):
        with open(reputation_folder + "/reputation_database.json", "w") as f:
            json.dump(self.individual_reputations, f, indent=4)

        with open(
            reputation_folder + "/out_of_date_reputation_database.json", "w"
        ) as f:
            json.dump(self.out_of_date_reputations, f, indent=4)

    def get_targets_individual_reputation(self, target_index, role):
        target_reputation = dict()
        for key, reputation in self.individual_reputations.items():
            if role.lower() in key.lower():
                if (
                    target_index == reputation["ID"]
                    or target_index == reputation["name"]
                ):
                    target_reputation[key] = reputation
        return target_reputation

    def update_individual_reputation(self, reputation, curr_step, reason):
        print("UPDATING INDIVIDUAL REPUTATION")
        for key in reputation.keys():
            if key in self.individual_reputations.keys():
                pre_reputation = self.individual_reputations[key]
                pre_reputation["reason"] = reason
                self.out_of_date_reputations[key + f"_pre_{curr_step}"] = pre_reputation
                self.individual_reputations[key] = reputation[key]
            else:
                self.individual_reputations[key] = reputation[key]
                self.reputations_count += 1

    def get_all_reputations(self, role, self_id, with_self=False):
        all_reputations = dict()
        if role.lower() == "investor":
            input = "Investor"
        elif role.lower() == "trustee":
            input = "Trustee"
        elif role.lower() == "resident":
            input = "Resident"
        for key, reputation in self.individual_reputations.items():
            if with_self and input in key:
                all_reputations[key] = reputation
                continue
            # get all reputation except self reputation
            if f"{input}_{self_id}" != key and input in key:
                all_reputations[key] = reputation
        return all_reputations
