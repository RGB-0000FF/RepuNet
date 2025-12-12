import os
import json
from prompt_interface import *
from utils import default_gpt_params
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


def run_gpt_prompt_stage2_game_result_v1(
    player1: Persona,
    player2: Persona,
    verbose: bool = True,
):
    def create_prompt_input(player1: Persona, player2: Persona):
        prompt_input = []
        prompt_input += [player1.scratch.learned]
        prompt_input += [player1.name]
        prompt_input += [player2.name]
        memory = player1.associativeMemory.get_latest_event_with_target(player1.name, "subject")
        prompt_input += [memory]
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
    prompt_input = create_prompt_input(player1, player2)
    prompt_template = "prompt/stage_2/game_result_v1.txt"
    prompt = generate_prompt_role_play(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    gpt_param = default_gpt_params()
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

        # More robust parsing logic
        try:
            # Find the Self Reflection section
            if "Self Reflection:" in gpt_response:
                self_part = gpt_response.split("Self Reflection:")[-1]
                if "Opponent Reflection:" in self_part:
                    res["self_reflection"] = self_part.split("Opponent Reflection:")[0].strip()
                else:
                    res["self_reflection"] = self_part.strip()
            else:
                return False

            # Find the Opponent Reflection section
            if "Opponent Reflection:" in gpt_response:
                opponent_part = gpt_response.split("Opponent Reflection:")[-1].strip()
                res["opponent_reflection"] = opponent_part
            else:
                return False

            # Validate the parsed content
            for val in res.values():
                if val == "" or len(val) < 5:  # Require non-empty, meaningful content
                    return False
            return res
        except Exception as e:
            print(f"Parsing error: {e}")
            return False

    def get_fail_safe():
        fs = "Error"
        return fs
    prompt_template = "prompt/stage_3/player_evaluation_v1.txt"
    prompt_input = create_prompt_input(
        init_persona,
        target_persona,
        init_persona_decision,
        target_persona_decision,
    )
    prompt = generate_prompt_role_play(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    gpt_param = default_gpt_params()
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
    prompt_template = "prompt/stage_4/player_gossip_willingness_v1.txt"
    prompt_input = create_prompt_input(init_persona, target_persona, self_decision, target_decision, target_reflection)
    prompt = generate_prompt_role_play(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    gpt_param = default_gpt_params()
    output = safe_generate_response(prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up)

    if verbose:
        print_run_prompts(prompt_template, init_persona, gpt_param, prompt_input, prompt, output)

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]
