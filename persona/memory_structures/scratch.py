"""
Author: Joon Sung Park (joonspk@stanford.edu)

File: scratch.py
Description: Defines the short-term memory module for generative agents.
"""

import datetime
import json
import sys
from collections import deque


def check_if_file_exists(curr_file):
    """
    Checks if a file exists
    ARGS:
      curr_file: path to the current csv file.
    RETURNS:
      True if the file exists
      False if the file does not exist
    """
    try:
        with open(curr_file):
            pass
        return True
    except FileNotFoundError as e:
        print(f"File not found: {e}")
        return False


class Scratch:
    name: str

    innate: str
    learned: str
    currently: str
    ID: str
    role: str

    curr_step: int

    complain_buffer: list

    total_num_investor: int
    success_num_investor: int
    total_num_trustee: int
    success_num_trustee: int
    total_chat_num: int
    success_chat_num: int

    relationship: dict
    resources_unit: int

    observed: dict

    def __init__(self, f_saved,investment=None):
        self.is_investment = bool(investment)
        self.name = None

        self.innate = None
        # L1 stable traits.
        self.learned = {}
        # L2 external implementation.
        self.currently = None

        # reputation related
        self.ID = None
        self.role = None

        self.curr_step = 0

        # gossip relate action
        self.complain_buffer = []

        self.total_num_investor = 0
        self.success_num_investor = 0
        self.total_num_trustee = 0
        self.success_num_trustee = 0
        self.total_chat_num = 0
        self.success_chat_num = 0

        self.relationship = {"bind_list": [], "black_list": deque([], maxlen=5)}
        self.resources_unit = 0

        self.observed = dict()

        if check_if_file_exists(f_saved):
            # If we have a bootstrap file, load that here.
            scratch_load = json.load(open(f_saved,encoding='utf-8', errors='ignore'))

            self.name = scratch_load.get("name")
            self.innate = scratch_load.get("innate")
            self.learned = self._normalize_learned(scratch_load.get("learned"), self.is_investment)
            self.currently = scratch_load.get("currently")

            self.ID = scratch_load.get("ID")
            self.role = scratch_load.get("role")

            self.curr_step = scratch_load.get("curr_step", 0)

            self.complain_buffer = scratch_load.get("complain_buffer", [])

            self.total_num_investor = scratch_load.get("total_num_investor", 0)
            self.success_num_investor = scratch_load.get("success_num_investor", 0)
            self.total_num_trustee = scratch_load.get("total_num_trustee", 0)
            self.success_num_trustee = scratch_load.get("success_num_trustee", 0)
            self.total_chat_num = scratch_load.get("total_chat_num", 0)
            self.success_chat_num = scratch_load.get("success_chat_num", 0)

            relationship_load = scratch_load.get("relationship", {"bind_list": [], "black_list": []})
            self.relationship = {
                "bind_list": relationship_load.get("bind_list", []),
                "black_list": deque(
                    relationship_load.get("black_list", []), maxlen=5
                ),
            }
            self.resources_unit = scratch_load.get("resources_unit", 0)

            self.observed = scratch_load.get("observed", {})
        else:
            self.learned = self._normalize_learned(self.learned, self.is_investment)

    def _normalize_learned(self, learned_value, investment):
        """
        Ensure learned takes a consistent shape:
        - investment=True -> {"investor": str, "trustee": str}
        - otherwise -> str/dict as provided or empty string.
        """
        if investment:
            investor = ""
            trustee = ""
            if isinstance(learned_value, dict):
                investor = learned_value.get("investor") or learned_value.get("0") or learned_value.get("investor_learned") or next(iter(learned_value.values()), "")
                trustee = learned_value.get("trustee") or learned_value.get("1") or learned_value.get("trustee_learned") or investor
            elif isinstance(learned_value, list):
                investor = learned_value[0] if len(learned_value) > 0 else ""
                trustee = learned_value[1] if len(learned_value) > 1 else investor
            elif learned_value is not None:
                investor = trustee = learned_value
            return {"investor": investor, "trustee": trustee if trustee is not None else investor}

        if isinstance(learned_value, dict):
            if "value" in learned_value:
                return learned_value.get("value")
            return learned_value if learned_value else ""
        return learned_value if learned_value is not None else ""

    def save(self, out_json):
        """
        Save persona's scratch.

        INPUT:
          out_json: The file where we wil be saving our persona's state.
        OUTPUT:
          None
        """
        scratch = dict()

        scratch["name"] = self.name
        scratch["innate"] = self.innate
        scratch["learned"] = self._normalize_learned(self.learned, self.is_investment)
        scratch["currently"] = self.currently

        scratch["ID"] = self.ID
        scratch["role"] = self.role

        scratch["curr_step"] = self.curr_step

        scratch["complain_buffer"] = self.complain_buffer

        scratch["total_num_investor"] = self.total_num_investor
        scratch["success_num_investor"] = self.success_num_investor
        scratch["total_num_trustee"] = self.total_num_trustee
        scratch["success_num_trustee"] = self.success_num_trustee
        scratch["total_chat_num"] = self.total_chat_num
        scratch["success_chat_num"] = self.success_chat_num

        scratch["relationship"] = {
            "bind_list": list(self.relationship["bind_list"]),
            "black_list": list(self.relationship["black_list"]),
        }

        scratch["resources_unit"] = self.resources_unit

        scratch["observed"] = self.observed

        with open(out_json, "w") as outfile:
            json.dump(scratch, outfile, indent=2, ensure_ascii=False)

    def get_str_iss(self):
        """
        ISS stands for "identity stable set." This describes the commonset summary
        of this persona -- basically, the bare minimum description of the persona
        that gets used in almost all prompts that need to call on the persona.

        INPUT
          None
        OUTPUT
          the identity stable set summary of the persona in a string form.
        EXAMPLE STR OUTPUT
          "Name: Dolores Heitmiller
           Age: 28
           Innate traits: hard-edged, independent, loyal
           Learned traits: Dolores is a painter who wants live quietly and paint
             while enjoying her everyday life.
           Currently: Dolores is preparing for her first solo show. She mostly
             works from home.
           Lifestyle: Dolores goes to bed around 11pm, sleeps for 7 hours, eats
             dinner around 6pm.
           Daily plan requirement: Dolores is planning to stay at home all day and
             never go out."
        """
        commonset = ""
        commonset += f"Name: {self.name}\n"
        commonset += f"Innate traits: {self.innate}\n"
        commonset += f"Learned traits: {self.learned}\n"
        commonset += f"Currently: {self.currently}\n"
        return commonset

    def validate(self):
        """
        Validate the current state of the scratch.

        INPUT
          None
        OUTPUT
          True if the state is valid
          False if the state is invalid
        """
        try:
            json.loads(self.to_json())
            return True
        except Exception as e:
            print(f"Validation error: {e}")
            return False
