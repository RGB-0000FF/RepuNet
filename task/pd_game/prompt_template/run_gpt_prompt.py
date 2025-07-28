import os
import json
from .gpt_structure import *
from persona.persona import Persona


def replace_full_name(name):
    # TODO change to the actual sim persona names
    personas = [
        "Liam OConnor",
        "Hiroshi Tanaka",
        "David Johnson",
        "Maria Rossi",
        "Sofia Hernandez",
        "James Wang",
        "Sergey Petrov",
        "Hannah Muller",
        "Nadia Novak",
        "Elena Ivanova",
        "Mohammed Al-Farsi",
        "Aisha Ibrahim",
        "Akiko Sato",
        "Emma Dubois",
        "Juan Carlos Reyes",
        "Ahmed Hassan",
        "Robert Miller",
        "Fatima Ali",
        "Isabella Costa",
        "Mateo Garcia",
    ]
    for persona in personas:
        if name in persona:
            return persona
    return None


def run_gpt_prompt_select_player_v1(
    init_persona: Persona,
    repu_list: str,
    verbose: bool = True,
):
    def create_prompt_input(init_persona: Persona, repu_list: str):
        prompt_input = []
        prompt_input += [init_persona.scratch.learned]
        prompt_input += [repu_list]

        return prompt_input

    def __func_validate(gpt_response, prompt=""):
        try:
            if __func_clean_up(gpt_response, prompt):
                return True
            return False
        except Exception as e:
            print(f"Validation error: {e}")
            return False

    def __func_clean_up(gpt_response, prompt=""):
        selected_player = replace_full_name(gpt_response)
        if selected_player:
            return selected_player
        return False

    def get_fail_safe():
        fs = "Error"
        return fs

    gpt_param = {
        "engine": "gpt-4o-mini",
        "max_tokens": 4096,
        "temperature": 0,
        "top_p": 1,
        "stream": False,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "stop": None,
    }
    prompt_input = create_prompt_input(init_persona, repu_list)
    prompt_template = "prompt/select_player_v1.txt"
    prompt = generate_prompt_role_play(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = safe_generate_response(prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up)

    if verbose:
        print_run_prompts(prompt_template, init_persona, gpt_param, prompt_input, prompt, output)

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]


def run_gpt_prompt_player_decide_whether_to_play_v1(
    init_persona: Persona,
    target_persona_reputation: str,
    verbose: bool = True,
):
    def create_prompt_input(init_persona: Persona, target_persona_reputation: str):
        prompt_input = []
        prompt_input += [init_persona.scratch.learned]
        prompt_input += [target_persona_reputation]
        return prompt_input

    def __func_validate(gpt_response, prompt=""):
        try:
            if __func_clean_up(gpt_response, prompt):
                return True
            return False
        except Exception as e:
            print(f"Validation error: {e}")
            return False

    def __func_clean_up(gpt_response, prompt=""):
        steps = gpt_response.splitlines()
        steps = [step.strip() for step in steps if step != "" and "step" in step.lower()]
        if steps[1].lower() not in ["yes", "no"]:
            return False
        if len(steps) == 2:
            if "yes" in steps[1].lower():
                steps[1] = "Accept"
            elif "no" in steps[1].lower():
                steps[1] = "Refuse"
            return steps[1]
        return False

    def get_fail_safe():
        fs = "Error"
        return fs

    gpt_param = {
        "engine": "gpt-4o-mini",
        "max_tokens": 4096,
        "temperature": 0,
        "top_p": 1,
        "stream": False,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "stop": None,
    }
    prompt_input = create_prompt_input(init_persona, target_persona_reputation)
    prompt_template = "prompt/stage_1/player_decide_whether_to_play_v1.txt"
    prompt = generate_prompt_role_play(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = safe_generate_response(prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up)

    if verbose:
        print_run_prompts(prompt_template, init_persona, gpt_param, prompt_input, prompt, output)

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]


def run_gpt_prompt_stage2_game_result_v1(
    player1: Persona,
    player2: Persona,
    verbose: bool = True,
):
    def create_prompt_input(player1: Persona, player2: Persona):
        player1_repu = player1.reputationDB.get_targets_individual_reputation(player1.scratch.ID, "player")
        player2_repu = player1.reputationDB.get_targets_individual_reputation(player2.scratch.ID, "player")

        prompt_input = []
        prompt_input += [player1.scratch.learned]
        prompt_input += [player1.name]
        prompt_input += [player1_repu]
        prompt_input += [player2.name]
        prompt_input += [player2_repu]
        return prompt_input

    def __func_validate(gpt_response, prompt=""):
        try:
            if __func_clean_up(gpt_response, prompt):
                return True
            return False
        except Exception as e:
            print(f"Validation error: {e}")
            return False

    def __func_clean_up(gpt_response, prompt=""):
        response = gpt_response.split("```json")[-1].split("```")[0].strip()
        res = json.loads(response)
        return res

    def get_fail_safe():
        fs = "Error"
        return fs

    gpt_param = {
        "engine": "gpt-4o-mini",
        "max_tokens": 4096,
        "temperature": 0,
        "top_p": 1,
        "stream": False,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "stop": None,
    }
    prompt_input = create_prompt_input(player1, player2)
    prompt_template = "prompt/stage_2/game_result_v1.txt"
    prompt = generate_prompt_role_play(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = safe_generate_response(prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up)

    if verbose:
        print_run_prompts(prompt_template, player1, gpt_param, prompt_input, prompt, output)

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]


def run_gpt_prompt_stage3_player_evaluation_v1(
    init_persona,
    target_persona,
    init_persona_decision,
    target_persona_decision,
    verbose=True,
):
    def create_prompt_input(
        init_persona,
        target_persona,
        init_persona_decision,
        target_persona_decision,
    ):
        prompt_input = []
        prompt_input += [init_persona.scratch.learned]
        investor_reputation = init_persona.reputationDB.get_targets_individual_reputation(init_persona.scratch.ID, "investor")
        if not investor_reputation:
            investor_reputation = "None"
        prompt_input += [investor_reputation]
        trustee_reputation = init_persona.reputationDB.get_targets_individual_reputation(target_persona.scratch.ID, "trustee")
        if not trustee_reputation:
            trustee_reputation = "None"
        prompt_input += [trustee_reputation]
        prompt_input += [init_persona_decision]
        prompt_input += [target_persona_decision]
        prompt_input += [init_persona.name]
        prompt_input += [target_persona.name]
        return prompt_input

    def __func_validate(gpt_response, prompt=""):
        try:
            if __func_clean_up(gpt_response, prompt):
                return True
            return False
        except Exception as e:
            print(f"Validation error: {e}")
            return False

    def __func_clean_up(gpt_response, prompt=""):
        res = dict()
        gpt_response = gpt_response.replace("*", "")
        res["self_reputation"] = gpt_response.split("Self Reputation Reflection:")[-1].split("Opponent Reputation Reflection:")[0].strip()
        res["opponent_reputation"] = gpt_response.split("Opponent Reputation Reflection:")[-1].strip()
        for val in res.values():
            if val == "":
                return False
        return res

    def get_fail_safe():
        fs = "Error"
        return fs

    gpt_param = {
        "engine": "gpt-4o",
        "max_tokens": 4096,
        "temperature": 0,
        "top_p": 1,
        "stream": False,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "stop": None,
    }
    prompt_template = "prompt/stage_3/player_evaluation_v1.txt"
    prompt_input = create_prompt_input(
        init_persona,
        target_persona,
        init_persona_decision,
        target_persona_decision,
    )
    prompt = generate_prompt_role_play(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = safe_generate_response(prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up)

    if verbose:
        print_run_prompts(prompt_template, init_persona, gpt_param, prompt_input, prompt, output)

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]


def run_gpt_prompt_stage4_player_gossip_willing_v1(
    init_persona,
    target_persona,
    self_decision,
    target_decision,
    target_reflection,
    verbose=True,
):
    def create_prompt_input(
        init_persona,
        target_persona,
        self_decision,
        target_decision,
        target_reflection,
    ):
        prompt_input = []
        prompt_input += [init_persona.scratch.learned]
        prompt_input += [init_persona.name]
        prompt_input += [target_persona.name]
        prompt_input += [self_decision]
        prompt_input += [target_decision]
        prompt_input += [target_reflection]
        target_persona_reputation = init_persona.reputationDB.get_targets_individual_reputation(target_persona.scratch.ID, "player")
        prompt_input += [json.dumps(target_persona_reputation)]

        return prompt_input

    def __func_validate(gpt_response, prompt=""):
        try:
            if __func_clean_up(gpt_response, prompt):
                return True
            return False
        except Exception as e:
            print(f"Validation error: {e}")
            return False

    def __func_clean_up(gpt_response, prompt=""):
        try:
            if ("Yes" not in gpt_response) and ("No" not in gpt_response):
                return False
            gpt_response = gpt_response.replace("*", "")
            return gpt_response.strip()
        except Exception as e:
            print(f"Clean up error: {e}")
            return False

    def get_fail_safe():
        fs = "Error"
        return fs

    gpt_param = {
        "engine": "gpt-4o-mini",
        "max_tokens": 4096,
        "temperature": 0,
        "top_p": 1,
        "stream": False,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "stop": None,
    }
    prompt_template = "prompt/stage_4/player_gossip_willingness_v1.txt"
    prompt_input = create_prompt_input(init_persona, target_persona, self_decision, target_decision, target_reflection)
    prompt = generate_prompt_role_play(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = safe_generate_response(prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up)

    if verbose:
        print_run_prompts(prompt_template, init_persona, gpt_param, prompt_input, prompt, output)

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]
