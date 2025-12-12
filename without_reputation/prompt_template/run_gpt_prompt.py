from prompt_interface import *
from utils import default_gpt_params
import json


def run_gpt_prompt_update_learned_in_description_v1(
    init_persona,
    init_persona_role,
    interaction_memory_self_veiw,
):
    def create_prompt_input(
        init_persona,
        init_persona_role,
        interaction_memory_self_veiw,
    ):
        prompt_input = []
        prompt_input += ["You are an expert on updating learned in an agent description based on its Interaction Memory."]
        prompt_input += [init_persona.scratch.name]
        prompt_input += [init_persona.scratch.learned[init_persona_role]]
        prompt_input += [interaction_memory_self_veiw]

        return prompt_input

    def __func_validate(gpt_response, prompt=None):
        try:
            persona_name = prompt["user"].split("**Task:**")[-1].split("is a")[0].strip()
            if persona_name in gpt_response:
                return True
            return False
        except Exception as e:
            print(e)
            return False

    def __func_clean_up(gpt_response, prompt=None):
        response = gpt_response.split("Updated “learned” information:")[-1].strip()
        return response

    def get_fail_safe():
        fs = "error"
        return fs

    gpt_param = default_gpt_params()
    if init_persona_role == "resident":
        prompt_template = "prompt/update_learned_in_description_v2.txt"
    elif init_persona_role == "investor":
        prompt_template = "prompt/investment/baseline_update_investor_learned_description_v1.txt"
    elif init_persona_role == "trustee":
        prompt_template = "prompt/investment/baseline_update_trustee_learned_description_v1.txt"
    prompt_input = create_prompt_input(
        init_persona,
        init_persona_role,
        interaction_memory_self_veiw,
    )
    prompt = generate_prompt_role_play(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = safe_generate_response(prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up)

    print_run_prompts(prompt_template, init_persona, gpt_param, prompt_input, prompt, output)

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]


def run_gpt_prompt_update_learned_in_description_pd_game_v1(
    init_persona,
    init_persona_role,
    interaction_memory_self_veiw,
):
    def create_prompt_input(
        init_persona,
        init_persona_role,
        interaction_memory_self_veiw,
    ):
        prompt_input = []
        prompt_input += ["You are an expert on updating innate traits in an agent description based on its Interaction Memory."]
        prompt_input += [init_persona.scratch.name]
        prompt_input += [init_persona.scratch.learned]
        prompt_input += [interaction_memory_self_veiw]

        return prompt_input

    def __func_validate(gpt_response, prompt=None):
        try:
            persona_name = prompt["user"].split("Based on ")[-1].split("'s **Previous Innate")[0].strip()
            if persona_name in gpt_response:
                return True
            return False
        except Exception as e:
            print(e)
            return False

    def __func_clean_up(gpt_response, prompt=None):
        response = gpt_response.split('Updated "innate" information:')[-1].strip()
        return response

    def get_fail_safe():
        fs = "error"
        return fs

    gpt_param = default_gpt_params()
    prompt_template = "prompt/pd_game/update_learned_in_description_v1.txt"
    prompt_input = create_prompt_input(
        init_persona,
        init_persona_role,
        interaction_memory_self_veiw,
    )
    prompt = generate_prompt_role_play(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = safe_generate_response(prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up)

    print_run_prompts(prompt_template, init_persona, gpt_param, prompt_input, prompt, output)

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]


def run_gpt_prompt_gossip_listener_select_learned_v1(
    init_persona,
    init_persona_role,
    target_persona,
):
    def create_prompt_input(
        init_persona,
        target_persona,
        init_persona_role,
    ):
        prompt_input = []
        prompt_input += [init_persona.scratch.learned]
        prompt_input += [init_persona.scratch.name]
        prompt_input += [target_persona.scratch.name]
        bind_list = list(init_persona.scratch.relationship["bind_list"])
        prompt_input += [bind_list]

        return prompt_input

    def __func_validate(gpt_response, prompt=None):
        try:
            if "None" in gpt_response:
                return True
            if __func_clean_up(gpt_response, prompt):
                return True
            return False
        except Exception as e:
            print(e)
            return False

    def __func_clean_up(gpt_response, prompt=None):
        if "None" in gpt_response:
            return []
        full_name = replace_full_name(gpt_response)
        if full_name:
            gpt_response = full_name
        else:
            print(f"Full name not found for {gpt_response}")
            return False
        return [gpt_response]

    def get_fail_safe():
        fs = []
        return fs

    gpt_param = default_gpt_params()
    prompt_template = "prompt/gossip_listener_select_v2.txt"
    prompt_input = create_prompt_input(
        init_persona,
        target_persona,
        init_persona_role,
    )
    prompt = generate_prompt_role_play(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = safe_generate_response(prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up)

    print_run_prompts(prompt_template, init_persona, gpt_param, prompt_input, prompt, output)

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]


def run_gpt_prompt_gossip_listener_select_v1(
    init_persona,
    init_persona_role,
    target_persona,
):
    def create_prompt_input(
        init_persona,
        target_persona,
        init_persona_role,
    ):
        prompt_input = []
        prompt_input += [init_persona.scratch.learned[init_persona_role]] if type(init_persona.scratch.learned) is dict else [init_persona.scratch.learned]
        prompt_input += [init_persona.scratch.name]
        prompt_input += [target_persona.scratch.name]
        bind_list = list(init_persona.scratch.relationship["bind_list"])
        prompt_input += [[i[0] for i in bind_list]] if type(bind_list) is list else [bind_list]

        return prompt_input

    def __func_validate(gpt_response, prompt=None):
        try:
            if "None" in gpt_response:
                return True
            if __func_clean_up(gpt_response, prompt):
                return True
            return False
        except Exception as e:
            print(e)
            return False

    def __func_clean_up(gpt_response, prompt=None):
        if "None" in gpt_response:
            return []
        full_name = replace_full_name(gpt_response)
        if full_name:
            gpt_response = full_name
        else:
            print(f"Full name not found for {gpt_response}")
            return False
        return [gpt_response]

    def get_fail_safe():
        fs = []
        return fs

    gpt_param = default_gpt_params()
    prompt_template = "prompt/gossip_listener_select_v2.txt"
    prompt_input = create_prompt_input(
        init_persona,
        target_persona,
        init_persona_role,
    )
    prompt = generate_prompt_role_play(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = safe_generate_response(prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up)

    print_run_prompts(prompt_template, init_persona, gpt_param, prompt_input, prompt, output)

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]


def run_gpt_prompt_gossip_v2(init_persona, target_persona, reason, complain_target, init_persona_role=None):
    def create_prompt_input(init_persona, target_persona, reason, complain_target, init_persona_role=None):
        prompt_input = []
        prompt_input += ["You are now a dialogue generation expert."]
        prompt_input += [init_persona.scratch.name]
        prompt_input += [target_persona.scratch.name]
        prompt_input += [init_persona.scratch.learned[init_persona_role]] if type(init_persona.scratch.learned) is dict else [init_persona.scratch.learned]
        prompt_input += [target_persona.scratch.learned[init_persona_role]] if type(target_persona.scratch.learned) is dict else [target_persona.scratch.learned]
        prompt_input += [reason]
        prompt_input += [complain_target]

        return prompt_input

    def __func_validate(gpt_response, prompt=None):
        try:
            if ":" in gpt_response:
                return True
            return False
        except Exception as e:
            print(e)
            return False

    def __func_clean_up(gpt_response, prompt=None):
        return gpt_response

    def get_fail_safe():
        fs = "error"
        return fs

    gpt_param = default_gpt_params()
    prompt_template = "prompt/create_gossip_chat_v2.txt"
    prompt_input = create_prompt_input(init_persona, target_persona, reason, complain_target, init_persona_role)
    prompt = generate_prompt_role_play(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = safe_generate_response(prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up)

    print_run_prompts(prompt_template, init_persona, gpt_param, prompt_input, prompt, output)

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]


def run_gpt_prompt_identify_and_summary_gossip_info_and_second_gossip_willingnes_v1(init_persona, target_persona, complain_info, init_persona_role=None):
    def create_prompt_input(init_persona, target_persona, complain_info, init_persona_role):
        prompt_input = []
        prompt_input += [init_persona.scratch.learned[init_persona_role]] if type(init_persona.scratch.learned) is dict else [init_persona.scratch.learned]
        prompt_input += [init_persona.scratch.name]
        prompt_input += [target_persona.scratch.name]
        prompt_input += [complain_info["complained name"]]
        prompt_input += [complain_info["complained ID"]]
        prompt_input += [complain_info["gossip chat"]]

        return prompt_input

    def __func_validate(gpt_response, prompt=None):
        try:
            if __func_clean_up(gpt_response, prompt):
                return True
            return False
        except Exception as e:
            print(e)
            return False

    def __func_clean_up(gpt_response, prompt=None):
        response = gpt_response.split("```json")[-1].split("```")[0].strip()
        res = json.loads(response)
        res_fin = []
        res_fin.append(res)
        return res_fin

    def get_fail_safe():
        fs = "error"
        return fs

    gpt_param = default_gpt_params()
    prompt_template = "prompt/woutRepu_identify_and_summary_gossip_info_and_second_gossip_willingnes_v1.txt"
    prompt_input = create_prompt_input(init_persona, target_persona, complain_info, init_persona_role)
    prompt = generate_prompt_role_play(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = safe_generate_response(prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up)

    print_run_prompts(prompt_template, init_persona, gpt_param, prompt_input, prompt, output)

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]


def run_gpt_prompt_connection_build_investor_v1(init_persona, target_persona, interaction_memory):
    def create_prompt_input(init_persona, target_persona, interaction_memory):
        prompt_input = []
        prompt_input += [init_persona.scratch.learned["investor"]]
        prompt_input += [init_persona.scratch.name]
        prompt_input += [target_persona.scratch.name]
        prompt_input.append(interaction_memory)
        # target_persona_recent_behavior = (
        #     init_persona.associativeMemory.get_latest_event()
        # ).toJSON()

        # prompt_input += [target_persona_recent_behavior["description"]]

        return prompt_input

    def __func_validate(gpt_response, prompt=None):
        try:
            if __func_clean_up(gpt_response, prompt):
                return True
            return False
        except Exception as e:
            print(e)
            return False

    def __func_clean_up(gpt_response, prompt=None):
        response = gpt_response.split("```json")[-1].split("```")[0].strip()
        res = json.loads(response)
        return res

    def get_fail_safe():
        fs = "error"
        return fs

    gpt_param = default_gpt_params()
    prompt_template = "prompt/investment/Baseline-connection_build_after_investment_v1.txt"
    prompt_input = create_prompt_input(
        init_persona,
        target_persona,
        interaction_memory,
    )
    prompt = generate_prompt_role_play(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = safe_generate_response(prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up)

    print_run_prompts(prompt_template, init_persona, gpt_param, prompt_input, prompt, output)

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]


def run_gpt_prompt_connection_build_after_pd_game_v1(init_persona, target_persona, interaction_memory):
    def create_prompt_input(init_persona, target_persona, interaction_memory):
        prompt_input = []
        prompt_input += [init_persona.scratch.learned]
        prompt_input += [init_persona.scratch.name]
        prompt_input += [target_persona.scratch.name]
        prompt_input += [interaction_memory]

        return prompt_input

    def __func_validate(gpt_response, prompt=None):
        try:
            if __func_clean_up(gpt_response, prompt):
                return True
            return False
        except Exception as e:
            print(e)
            return False

    def __func_clean_up(gpt_response, prompt=None):
        response = gpt_response.split("```json")[-1].split("```")[0].strip()
        res = json.loads(response)
        return res

    def get_fail_safe():
        fs = "error"
        return fs

    gpt_param = default_gpt_params()
    prompt_template = "prompt/pd_game/connection_after_pd_game_v1.txt"
    prompt_input = create_prompt_input(
        init_persona,
        target_persona,
        interaction_memory,
    )
    prompt = generate_prompt_role_play(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = safe_generate_response(prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up)

    print_run_prompts(prompt_template, init_persona, gpt_param, prompt_input, prompt, output)

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]


def run_gpt_prompt_disconnection_after_pd_game_v1(init_persona, target_persona, interaction_memory):
    def create_prompt_input(
        init_persona,
        target_persona,
        interaction_memory,
    ):
        prompt_input = []
        prompt_input += [init_persona.scratch.learned]
        prompt_input += [init_persona.scratch.name]
        prompt_input += [target_persona.scratch.name]
        prompt_input += [interaction_memory]

        return prompt_input

    def __func_validate(gpt_response, prompt=None):
        try:
            if __func_clean_up(gpt_response, prompt):
                return True
            return False
        except Exception as e:
            print(e)
            return False

    def __func_clean_up(gpt_response, prompt=None):
        response = gpt_response.split("```json")[-1].split("```")[0].strip()
        res = json.loads(response)
        return res

    def get_fail_safe():
        fs = "error"
        return fs

    gpt_param = default_gpt_params()
    prompt_template = "prompt/pd_game/disconnection_after_pd_game_v1.txt"
    prompt_input = create_prompt_input(
        init_persona,
        target_persona,
        interaction_memory,
    )
    prompt = generate_prompt_role_play(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = safe_generate_response(prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up)

    print_run_prompts(prompt_template, init_persona, gpt_param, prompt_input, prompt, output)

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]


def run_gpt_prompt_disconnection_investor_v1(init_persona, target_persona, interaction_memory):
    def create_prompt_input(
        init_persona,
        target_persona,
        interaction_memory,
    ):
        prompt_input = []
        prompt_input += [init_persona.scratch.learned["investor"]]
        prompt_input += [init_persona.scratch.name]
        prompt_input += [target_persona.scratch.name]
        # target_persona_recent_behavior = (
        #     init_persona.associativeMemory.get_latest_event()
        # ).toJSON()
        # prompt_input += [target_persona_recent_behavior["description"]]
        prompt_input.append(interaction_memory)

        return prompt_input

    def __func_validate(gpt_response, prompt=None):
        try:
            if __func_clean_up(gpt_response, prompt):
                return True
            return False
        except Exception as e:
            print(e)
            return False

    def __func_clean_up(gpt_response, prompt=None):
        response = gpt_response.split("```json")[-1].split("```")[0].strip()
        res = json.loads(response)
        return res

    def get_fail_safe():
        fs = "error"
        return fs

    gpt_param = default_gpt_params()
    prompt_template = "prompt/investment/Baseline-disconnection_after_investment_v1.txt"
    prompt_input = create_prompt_input(
        init_persona,
        target_persona,
        interaction_memory,
    )
    prompt = generate_prompt_role_play(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = safe_generate_response(prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up)

    print_run_prompts(prompt_template, init_persona, gpt_param, prompt_input, prompt, output)

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]


def run_gpt_prompt_connection_build_trustee_v1(init_persona, target_persona, interaction_memory):
    def create_prompt_input(
        init_persona,
        target_persona,
        interaction_memory,
    ):
        prompt_input = []
        prompt_input += [init_persona.scratch.learned["trustee"]]
        prompt_input += [init_persona.scratch.name]
        prompt_input += [target_persona.scratch.name]
        # target_persona_recent_behavior = (
        #     init_persona.associativeMemory.get_latest_event()
        # ).toJSON()
        # prompt_input += [target_persona_recent_behavior["description"]]
        prompt_input.append(interaction_memory)

        return prompt_input

    def __func_validate(gpt_response, prompt=None):
        try:
            if __func_clean_up(gpt_response, prompt):
                return True
            return False
        except Exception as e:
            print(e)
            return False

    def __func_clean_up(gpt_response, prompt=None):
        response = gpt_response.split("```json")[-1].split("```")[0].strip()
        res = json.loads(response)
        return res

    def get_fail_safe():
        fs = "error"
        return fs

    gpt_param = default_gpt_params()
    prompt_template = "prompt/investment/Baseline-connection_build_after_investment_v1.txt"
    prompt_input = create_prompt_input(
        init_persona,
        target_persona,
        interaction_memory,
    )
    prompt = generate_prompt(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = safe_generate_response(prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up)

    print_run_prompts(prompt_template, init_persona, gpt_param, prompt_input, prompt, output)

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]


def run_gpt_prompt_disconnection_trustee_v1(init_persona, target_persona, interaction_memory):
    def create_prompt_input(
        init_persona,
        target_persona,
        interaction_memory,
    ):
        prompt_input = []
        prompt_input += [init_persona.scratch.learned["trustee"]]
        prompt_input += [init_persona.scratch.name]
        prompt_input += [target_persona.scratch.name]
        prompt_input.append(interaction_memory)
        # target_persona_recent_behavior = (
        #     init_persona.associativeMemory.get_latest_event()
        # ).toJSON()
        # prompt_input += [target_persona_recent_behavior["description"]]

        return prompt_input

    def __func_validate(gpt_response, prompt=None):
        try:
            if __func_clean_up(gpt_response, prompt):
                return True
            return False
        except Exception as e:
            print(e)
            return False

    def __func_clean_up(gpt_response, prompt=None):
        response = gpt_response.split("```json")[-1].split("```")[0].strip()
        res = json.loads(response)
        return res

    def get_fail_safe():
        fs = "error"
        return fs

    gpt_param = default_gpt_params()
    prompt_template = "prompt/investment/Baseline-disconnection_after_investment_v1.txt"
    prompt_input = create_prompt_input(
        init_persona,
        target_persona,
        interaction_memory,
    )
    prompt = generate_prompt(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = safe_generate_response(prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up)

    print_run_prompts(prompt_template, init_persona, gpt_param, prompt_input, prompt, output)

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]


def run_gpt_prompt_disconnection_after_gossip_v1(
    init_persona,
    target_persona,
    init_persona_role,
    target_persona_role,
    gossiper_name,
    gossip_info,
):
    def create_prompt_input(
        init_persona,
        target_persona,
        init_persona_role,
        target_persona_role,
        gossiper_name,
        gossip_info,
    ):
        prompt_input = []
        prompt_input += [init_persona.scratch.learned[init_persona_role]] if type(init_persona.scratch.learned) is dict else [init_persona.scratch.learned]
        prompt_input += [init_persona.scratch.name]
        prompt_input += [target_persona.scratch.name]
        prompt_input += [gossip_info]
        prompt_input += [gossiper_name]

        return prompt_input

    def __func_validate(gpt_response, prompt=None):
        try:
            if __func_clean_up(gpt_response, prompt):
                return True
            return False
        except Exception as e:
            print(e)
            return False

    def __func_clean_up(gpt_response, prompt=None):
        response = gpt_response.split("```json")[-1].split("```")[0].strip()
        res = json.loads(response)
        return res

    def get_fail_safe():
        fs = "error"
        return fs

    gpt_param = default_gpt_params()
    prompt_template = "prompt/disconnection_after_gossip_v2.txt"
    prompt_input = create_prompt_input(
        init_persona,
        target_persona,
        init_persona_role,
        target_persona_role,
        gossiper_name,
        gossip_info,
    )
    prompt = generate_prompt_role_play(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = safe_generate_response(prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up)

    print_run_prompts(prompt_template, init_persona, gpt_param, prompt_input, prompt, output)

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]


def run_gpt_prompt_disconnection_after_chat_sign_up_v1(init_persona, target_persona, target_persona_role, interaction_memory):
    def create_prompt_input(
        init_persona,
        target_persona,
        target_persona_role,
        interaction_memory,
    ):
        prompt_input = []
        prompt_input += [init_persona.scratch.learned]
        prompt_input += [init_persona.scratch.name]
        prompt_input += [target_persona.scratch.name]
        prompt_input += [interaction_memory]

        return prompt_input

    def __func_validate(gpt_response, prompt=None):
        try:
            if __func_clean_up(gpt_response, prompt):
                return True
            return False
        except Exception as e:
            print(e)
            return False

    def __func_clean_up(gpt_response, prompt=None):
        response = gpt_response.split("```json")[-1].split("```")[0].strip()
        res = json.loads(response)
        return res

    def get_fail_safe():
        fs = "error"
        return fs

    gpt_param = default_gpt_params()
    prompt_template = "prompt/sign_up/woutRepu_disconnection_after_chat_sign_up_v1.txt"
    prompt_input = create_prompt_input(
        init_persona,
        target_persona,
        target_persona_role,
        interaction_memory,
    )
    prompt = generate_prompt_role_play(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = safe_generate_response(prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up)

    print_run_prompts(prompt_template, init_persona, gpt_param, prompt_input, prompt, output)

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]


def run_gpt_prompt_connection_build_after_chat_sign_up_v1(init_persona, target_persona, target_persona_role, interaction_memory):
    def create_prompt_input(
        init_persona,
        target_persona,
        target_persona_role,
        interaction_memory,
    ):
        prompt_input = []
        prompt_input += [init_persona.scratch.learned]
        prompt_input += [init_persona.scratch.name]
        prompt_input += [target_persona.scratch.name]
        prompt_input += [interaction_memory]

        return prompt_input

    def __func_validate(gpt_response, prompt=None):
        try:
            if __func_clean_up(gpt_response, prompt):
                return True
            return False
        except Exception as e:
            print(e)
            return False

    def __func_clean_up(gpt_response, prompt=None):
        response = gpt_response.split("```json")[-1].split("```")[0].strip()
        res = json.loads(response)
        return res

    def get_fail_safe():
        fs = "error"
        return fs

    gpt_param = default_gpt_params()
    prompt_template = "prompt/sign_up/woutRepu_connection_build_after_chat_sign_up_v1.txt"
    prompt_input = create_prompt_input(
        init_persona,
        target_persona,
        target_persona_role,
        interaction_memory,
    )
    prompt = generate_prompt_role_play(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = safe_generate_response(prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up)

    print_run_prompts(prompt_template, init_persona, gpt_param, prompt_input, prompt, output)

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]


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