from prompt_interface import *
from utils import default_gpt_params
from persona.persona import Persona
import json


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


def run_gpt_prompt_reputation_update_after_stage4_investor_v1(
    init_persona,
    target_persona,
    Interaction_memory,
):
    def create_self_update_prompt_input(
        init_persona,
        Interaction_memory,
    ):
        prompt_input = []
        prompt_input.append(init_persona.scratch.learned["investor"])
        prompt_input.append(init_persona.scratch.name)
        prompt_input.append(init_persona.scratch.ID)
        prompt_input.append(Interaction_memory["init_behavior_summary"])
        init_persona_repu = init_persona.reputationDB.get_targets_individual_reputation(init_persona.scratch.ID, "Investor")
        # target_persona_reputation = (
        #     init_persona.reputationDB.get_targets_individual_reputation(
        #         target_persona.scratch.ID, "Trustee"
        #     )
        # )
        prompt_input += [json.dumps(init_persona_repu)]

        return prompt_input

    def create_target_update_prompt_input(
        init_persona,
        target_persona,
        Interaction_memory,
    ):
        prompt_input = []
        prompt_input.append(init_persona.scratch.learned)
        prompt_input.append(init_persona.scratch.name)
        prompt_input.append(target_persona.scratch.ID)
        prompt_input.append(Interaction_memory["target_behavior_summary"])
        target_persona_repu = init_persona.reputationDB.get_targets_individual_reputation(target_persona.scratch.ID, "Trustee")
        prompt_input += [json.dumps(target_persona_repu)]
        prompt_input.append(target_persona.scratch.name)
        return prompt_input

    def __func_validate(gpt_response, prompt=""):
        try:
            if __func_clean_up(gpt_response, prompt):
                return True
            return False
        except Exception as e:
            print(e)
            return False

    def __func_clean_up(gpt_response, prompt=""):
        response = gpt_response.split("```json")[-1].split("```")[0].strip()
        # print(response)
        final_res = dict()
        res = json.loads(response)

        for _, val in res.items():
            full_name = replace_full_name(val["name"])
            if full_name:
                val["name"] = full_name
            else:
                print(f"Full name not found for {val['name']}")
                return False
        for _, val in res.items():
            id = val["ID"]
            if val["role"].lower() == "investor":
                final_res[f"Investor_{id}"] = val
            elif val["role"].lower() == "trustee":
                final_res[f"Trustee_{id}"] = val
        if len(final_res) == 1:
            return dict(final_res)
        return False

    def get_fail_safe():
        fs = "error"
        return fs

    gpt_param = default_gpt_params()
    prompt_template_1 = "prompt/investment/All-self_investor_reputation_update_after_full_investment_v1.txt"
    prompt_template_2 = "prompt/investment/All-investor_update_others_reputation_after_full_investment_v1.txt"

    prompt_input_1 = create_self_update_prompt_input(
        init_persona,
        Interaction_memory,
    )
    prompt_input_2 = create_target_update_prompt_input(
        init_persona,
        target_persona,
        Interaction_memory,
    )
    prompt_1 = generate_prompt_role_play(prompt_input_1, prompt_template_1)
    prompt_2 = generate_prompt_role_play(prompt_input_2, prompt_template_2)
    fail_safe = get_fail_safe()
    output_1 = safe_generate_response(prompt_1, gpt_param, 5, fail_safe, __func_validate, __func_clean_up)
    output_2 = safe_generate_response(prompt_2, gpt_param, 5, fail_safe, __func_validate, __func_clean_up)
    print_run_prompts(prompt_template_1, init_persona, gpt_param, prompt_input_1, prompt_1, output_1)
    print_run_prompts(prompt_template_2, init_persona, gpt_param, prompt_input_2, prompt_2, output_2)

    output = {**output_1, **output_2}
    return output, [
        output,
        prompt_1,
        prompt_2,
        gpt_param,
        prompt_input_1,
        prompt_input_2,
        fail_safe,
    ]


def run_gpt_prompt_reputation_update_after_stage1_investor_v1(
    init_persona,
    target_persona,
    init_persona_role,
    target_persona_role,
    allocation_plan,
    reason_refusal,
    total_number_of_people,
    number_of_bidirectional_connections,
):
    def create_prompt_input(
        init_persona,
        target_persona,
        init_persona_role,
        target_persona_role,
        allocation_plan,
        reason_refusal,
        total_number_of_people,
        number_of_bidirectional_connections,
    ):
        prompt_input = []
        prompt_input += [init_persona.scratch.name]
        prompt_input += [target_persona.scratch.name]
        prompt_input += [init_persona.scratch.ID]
        prompt_input += [target_persona.scratch.ID]
        prompt_input += [allocation_plan]
        prompt_input += [reason_refusal]
        init_persona_reputation = init_persona.reputationDB.get_targets_individual_reputation(init_persona.scratch.ID, init_persona_role)
        target_persona_reputation = init_persona.reputationDB.get_targets_individual_reputation(target_persona.scratch.ID, target_persona_role)
        prompt_input += [json.dumps(init_persona_reputation)]
        prompt_input += [json.dumps(target_persona_reputation)]
        prompt_input += [total_number_of_people]
        prompt_input += [number_of_bidirectional_connections]

        return prompt_input

    def __func_validate(gpt_response, prompt=""):
        try:
            if __func_clean_up(gpt_response, prompt):
                return True
            return False
        except Exception as e:
            print(e)
            return False

    def __func_clean_up(gpt_response, prompt=""):
        response = gpt_response.split("```json")[-1].split("```")[0].strip()
        # print(response)
        final_res = dict()
        res = json.loads(response)

        for _, val in res.items():
            full_name = replace_full_name(val["name"])
            if full_name:
                val["name"] = full_name
            else:
                print(f"Full name not found for {val['name']}")
                return False
        for _, val in res.items():
            id = val["ID"]
            if val["role"].lower() == "investor":
                final_res[f"Investor_{id}"] = val
            elif val["role"].lower() == "trustee":
                final_res[f"Trustee_{id}"] = val
        if len(final_res) == 2:
            return final_res
        return False

    def get_fail_safe():
        fs = "error"
        return fs

    gpt_param = default_gpt_params()
    prompt_template = "prompt/investment/reputation_update_after_stage1_investor_v1.txt"
    prompt_input = create_prompt_input(
        init_persona,
        target_persona,
        init_persona_role,
        target_persona_role,
        allocation_plan,
        reason_refusal,
        total_number_of_people,
        number_of_bidirectional_connections,
    )
    prompt = generate_prompt(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = safe_generate_response(prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up)

    print_run_prompts(prompt_template, init_persona, gpt_param, prompt_input, prompt, output)

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]


def run_gpt_prompt_reputation_update_after_stage4_trustee_v1(
    init_persona,
    target_persona,
    Interaction_memory,
):
    def create_self_update_prompt_input(
        init_persona,
        Interaction_memory,
    ):
        prompt_input = []
        prompt_input.append(init_persona.scratch.learned["trustee"])
        prompt_input.append(init_persona.scratch.name)
        prompt_input.append(init_persona.scratch.ID)
        prompt_input.append(Interaction_memory["init_behavior_summary"])
        init_persona_repu = init_persona.reputationDB.get_targets_individual_reputation(init_persona.scratch.ID, "Trustee")
        # target_persona_reputation = (
        #     init_persona.reputationDB.get_targets_individual_reputation(
        #         target_persona.scratch.ID, "Trustee"
        #     )
        # )
        prompt_input += [json.dumps(init_persona_repu)]

        return prompt_input

    def create_target_update_prompt_input(
        init_persona,
        target_persona,
        Interaction_memory,
    ):
        prompt_input = []
        prompt_input.append(init_persona.scratch.learned)
        prompt_input.append(init_persona.scratch.name)
        prompt_input.append(target_persona.scratch.ID)
        prompt_input.append(Interaction_memory["target_behavior_summary"])

        target_persona_repu = init_persona.reputationDB.get_targets_individual_reputation(target_persona.scratch.ID, "Investor")
        prompt_input += [json.dumps(target_persona_repu)]
        prompt_input.append(target_persona.scratch.name)
        return prompt_input

    def __func_validate(gpt_response, prompt=""):
        try:
            if __func_clean_up(gpt_response, prompt):
                return True
            return False
        except Exception as e:
            print(e)
            return False

    def __func_clean_up(gpt_response, prompt=""):
        response = gpt_response.split("```json")[-1].split("```")[0].strip()
        # print(response)
        final_res = dict()
        res = json.loads(response)

        for _, val in res.items():
            full_name = replace_full_name(val["name"])
            if full_name:
                val["name"] = full_name
            else:
                print(f"Full name not found for {val['name']}")
                return False
        for _, val in res.items():
            id = val["ID"]
            if val["role"].lower() == "investor":
                final_res[f"Investor_{id}"] = val
            elif val["role"].lower() == "trustee":
                final_res[f"Trustee_{id}"] = val
        if len(final_res) == 1:
            return dict(final_res)
        return False

    def get_fail_safe():
        fs = "error"
        return fs

    gpt_param = default_gpt_params()
    prompt_template_1 = "prompt/investment/All-self_trustee_reputation_update_after_full_investment_v1.txt"
    prompt_template_2 = "prompt/investment/All-trustee_update_others_reputation_after_full_investment_v1.txt"
    prompt_input_1 = create_self_update_prompt_input(
        init_persona,
        Interaction_memory,
    )
    prompt_input_2 = create_target_update_prompt_input(
        init_persona,
        target_persona,
        Interaction_memory,
    )
    prompt_1 = generate_prompt_role_play(prompt_input_1, prompt_template_1)
    prompt_2 = generate_prompt_role_play(prompt_input_2, prompt_template_2)
    fail_safe = get_fail_safe()
    output_1 = safe_generate_response(prompt_1, gpt_param, 5, fail_safe, __func_validate, __func_clean_up)
    output_2 = safe_generate_response(prompt_2, gpt_param, 5, fail_safe, __func_validate, __func_clean_up)
    print_run_prompts(prompt_template_1, init_persona, gpt_param, prompt_input_1, prompt_1, output_1)
    print_run_prompts(prompt_template_2, init_persona, gpt_param, prompt_input_2, prompt_2, output_2)

    output = {**output_1, **output_2}
    return output, [
        output,
        prompt_1,
        prompt_2,
        gpt_param,
        prompt_input_1,
        prompt_input_2,
        fail_safe,
    ]


def run_gpt_prompt_reputation_update_after_observed_v1(
    init_persona,
    target_persona,
    init_persona_role,
    target_persona_role,
    interaction_memory,
):
    def create_prompt_input(
        init_persona,
        target_persona,
        init_persona_role,
        target_persona_role,
        interaction_memory,
    ):
        prompt_input = []
        prompt_input += [init_persona.scratch.learned[init_persona_role]]
        prompt_input += [init_persona.scratch.name]
        prompt_input += [target_persona.scratch.name]
        prompt_input += [interaction_memory]
        prompt_input += [target_persona.scratch.ID]
        pre_target_persona_reputation = init_persona.reputationDB.get_targets_individual_reputation(target_persona.scratch.ID, target_persona_role)
        prompt_input += [json.dumps(pre_target_persona_reputation)]
        prompt_input += [target_persona_role]

        return prompt_input

    def __func_validate(gpt_response, prompt=""):
        try:
            if __func_clean_up(gpt_response, prompt):
                return True
            return False
        except Exception as e:
            print(e)
            return False

    def __func_clean_up(gpt_response, prompt=""):
        response = gpt_response.split("```json")[-1].split("```")[0].strip()
        # print(response)
        final_res = dict()
        res = json.loads(response)

        for _, val in res.items():
            full_name = replace_full_name(val["name"])
            if full_name:
                val["name"] = full_name
            else:
                print(f"Full name not found for {val['name']}")
                return False
        for _, val in res.items():
            id = val["ID"]
            if val["role"].lower() == "investor":
                final_res[f"Investor_{id}"] = val
            elif val["role"].lower() == "trustee":
                final_res[f"Trustee_{id}"] = val
        if len(final_res) == 1:
            return final_res
        return False

    def get_fail_safe():
        fs = "error"
        return fs

    gpt_param = default_gpt_params()
    prompt_template = "prompt/investment/All_observe_update_others_v1.txt"
    prompt_input = create_prompt_input(
        init_persona,
        target_persona,
        init_persona_role,
        target_persona_role,
        interaction_memory,
    )
    prompt = generate_prompt(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = safe_generate_response(prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up)

    print_run_prompts(prompt_template, init_persona, gpt_param, prompt_input, prompt, output)

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]


def run_gpt_prompt_reputation_update_after_stage1_trustee_v1(
    init_persona,
    target_persona,
    init_persona_role,
    target_persona_role,
    allocation_plan,
    reason_refusal,
    total_number_of_people,
    number_of_bidirectional_connections,
):
    def create_prompt_input(
        init_persona,
        target_persona,
        init_persona_role,
        target_persona_role,
        allocation_plan,
        reason_refusal,
        total_number_of_people,
        number_of_bidirectional_connections,
    ):
        prompt_input = []
        prompt_input += [init_persona.scratch.name]
        prompt_input += [target_persona.scratch.name]
        prompt_input += [init_persona.scratch.ID]
        prompt_input += [target_persona.scratch.ID]
        prompt_input += [allocation_plan]
        prompt_input += [reason_refusal]
        init_persona_reputation = init_persona.reputationDB.get_targets_individual_reputation(init_persona.scratch.ID, init_persona_role)
        target_persona_reputation = init_persona.reputationDB.get_targets_individual_reputation(target_persona.scratch.ID, target_persona_role)
        prompt_input += [json.dumps(init_persona_reputation)]
        prompt_input += [json.dumps(target_persona_reputation)]
        prompt_input += [total_number_of_people]
        prompt_input += [number_of_bidirectional_connections]
        prompt_input += [init_persona.scratch.success_num_investor / init_persona.scratch.total_num_trustee]

        return prompt_input

    def __func_validate(gpt_response, prompt=""):
        try:
            if __func_clean_up(gpt_response, prompt):
                return True
            return False
        except Exception as e:
            print(e)
            return False

    def __func_clean_up(gpt_response, prompt=""):
        response = gpt_response.split("```json")[-1].split("```")[0].strip()
        # print(response)
        final_res = dict()
        res = json.loads(response)

        for _, val in res.items():
            full_name = replace_full_name(val["name"])
            if full_name:
                val["name"] = full_name
            else:
                print(f"Full name not found for {val['name']}")
                return False
        for _, val in res.items():
            id = val["ID"]
            if val["role"].lower() == "investor":
                final_res[f"Investor_{id}"] = val
            elif val["role"].lower() == "trustee":
                final_res[f"Trustee_{id}"] = val
        if len(final_res) == 2:
            return final_res
        return False

    def get_fail_safe():
        fs = "error"
        return fs

    gpt_param = default_gpt_params()
    prompt_template = "prompt/investment/reputation_update_after_stage1_trustee_v1.txt"
    prompt_input = create_prompt_input(
        init_persona,
        target_persona,
        init_persona_role,
        target_persona_role,
        allocation_plan,
        reason_refusal,
        total_number_of_people,
        number_of_bidirectional_connections,
    )
    prompt = generate_prompt(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = safe_generate_response(prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up)

    print_run_prompts(prompt_template, init_persona, gpt_param, prompt_input, prompt, output)

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]


def run_gpt_prompt_reputation_update_after_gossip_invest_v1(
    init_persona,
    target_persona,
    gossip,
    init_persona_role,
    target_persona_role,
    cred_level,
):
    def create_prompt_input(
        init_persona,
        target_persona,
        gossip,
        init_persona_role,
        target_persona_role,
        cred_level,
    ):
        prompt_input = []
        prompt_input.append(init_persona.scratch.learned[init_persona_role])
        prompt_input += [init_persona.scratch.name]
        prompt_input += [target_persona.scratch.name]
        prompt_input += [target_persona.scratch.ID]
        prompt_input += [gossip["gossiper name"]]
        target_persona_reputation = init_persona.reputationDB.get_targets_individual_reputation(target_persona.scratch.ID, target_persona_role)
        prompt_input += [json.dumps(target_persona_reputation)]
        prompt_input += [json.dumps(gossip)]
        if target_persona_role.lower() == "investor":
            prompt_input += ["Investor"]
        elif target_persona_role.lower() == "trustee":
            prompt_input += ["Trustee"]

        prompt_input += [cred_level]

        return prompt_input

    def __func_validate(gpt_response, prompt=""):
        try:
            if __func_clean_up(gpt_response, prompt):
                return True
            return False
        except Exception as e:
            print(e)
            return False

    def __func_clean_up(gpt_response, prompt=""):
        response = gpt_response.split("```json")[-1].split("```")[0].strip()
        # print(response)
        final_res = dict()
        res = json.loads(response)

        for _, val in res.items():
            full_name = replace_full_name(val["name"])
            if full_name:
                val["name"] = full_name
            else:
                print(f"Full name not found for {val['name']}")
                return False
        for _, val in res.items():
            id = val["ID"]
            if val["role"].lower() == "investor":
                final_res[f"Investor_{id}"] = val
            elif val["role"].lower() == "trustee":
                final_res[f"Trustee_{id}"] = val
        if len(final_res) == 1:
            return final_res
        return False

    def get_fail_safe():
        fs = "error"
        return fs

    gpt_param = default_gpt_params()
    prompt_template = "prompt/investment/All-update_others_reputation_after_gossip_v1.txt"
    prompt_input = create_prompt_input(
        init_persona,
        target_persona,
        gossip,
        init_persona_role,
        target_persona_role,
        cred_level,
    )
    prompt = generate_prompt_role_play(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = safe_generate_response(prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up)

    print_run_prompts(prompt_template, init_persona, gpt_param, prompt_input, prompt, output)

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]


def run_gpt_prompt_reputation_update_after_gossip_sign_up_v1(
    init_persona,
    target_persona,
    gossip,
    target_persona_role,
    total_number_of_people,
    number_of_bidirectional_connections,
):
    def create_prompt_input(
        init_persona,
        target_persona,
        gossip,
        target_persona_role,
        total_number_of_people,
        number_of_bidirectional_connections,
    ):
        prompt_input = []
        prompt_input += [init_persona.scratch.learned]
        prompt_input += [init_persona.scratch.name]
        prompt_input += [target_persona.scratch.name]
        prompt_input += [target_persona.scratch.ID]
        prompt_input += [gossip["gossiper name"]]
        target_persona_reputation = init_persona.reputationDB.get_targets_individual_reputation(target_persona.scratch.ID, target_persona_role)
        prompt_input += [json.dumps(target_persona_reputation)]
        prompt_input += [json.dumps(gossip)]
        if target_persona_role.lower() == "resident":
            prompt_input += ["Resident"]
        # prompt_input += [total_number_of_people]
        # prompt_input += [number_of_bidirectional_connections]
        prompt_input += [target_persona_role]
        prompt_input += [gossip["credibility level"]]

        return prompt_input

    def __func_validate(gpt_response, prompt=""):
        try:
            if __func_clean_up(gpt_response, prompt):
                return True
            return False
        except Exception as e:
            print(e)
            return False

    def __func_clean_up(gpt_response, prompt=""):
        response = gpt_response.split("```json")[-1].split("```")[0].strip()
        # print(response)
        res = json.loads(response)

        for _, val in res.items():
            full_name = replace_full_name(val["name"])
            if full_name:
                val["name"] = full_name
            else:
                print(f"Full name not found for {val['name']}")
                return False
        if len(res) == 1:
            return res
        return False

    def get_fail_safe():
        fs = "error"
        return fs

    gpt_param = default_gpt_params()
    prompt_template = "prompt/sign_up/reputation_update_after_gossip_sign_up_v2.txt"
    prompt_input = create_prompt_input(
        init_persona,
        target_persona,
        gossip,
        target_persona_role,
        total_number_of_people,
        number_of_bidirectional_connections,
    )
    prompt = generate_prompt_role_play(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = safe_generate_response(prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up)

    print_run_prompts(prompt_template, init_persona, gpt_param, prompt_input, prompt, output)

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]


def run_gpt_prompt_reputation_update_after_gossip_pd_game_v1(
    init_persona,
    target_persona,
    gossip,
):
    def create_prompt_input(
        init_persona,
        target_persona,
        gossip,
    ):
        prompt_input = []
        prompt_input += [init_persona.scratch.learned]
        prompt_input += [init_persona.scratch.name]
        prompt_input += [target_persona.scratch.name]
        prompt_input += [target_persona.scratch.ID]
        prompt_input += [gossip["gossiper name"]]
        target_persona_reputation = init_persona.reputationDB.get_targets_individual_reputation(target_persona.scratch.ID, "player")
        prompt_input += [json.dumps(target_persona_reputation)]
        prompt_input += [json.dumps(gossip)]
        prompt_input += ["Player"]
        prompt_input += ["player"]
        prompt_input += [gossip["credibility level"]]

        return prompt_input

    def __func_validate(gpt_response, prompt=""):
        try:
            if __func_clean_up(gpt_response, prompt):
                return True
            return False
        except Exception as e:
            print(e)
            return False

    def __func_clean_up(gpt_response, prompt=""):
        response = gpt_response.split("```json")[-1].split("```")[0].strip()
        # print(response)
        res = json.loads(response)

        for _, val in res.items():
            full_name = replace_full_name(val["name"])
            if full_name:
                val["name"] = full_name
            else:
                print(f"Full name not found for {val['name']}")
                return False
        if len(res) == 1:
            return res
        return False

    def get_fail_safe():
        fs = "error"
        return fs

    gpt_param = default_gpt_params()
    prompt_template = "prompt/pd_game/reputation_update_after_gossip_pd_game_v1.txt"
    prompt_input = create_prompt_input(
        init_persona,
        target_persona,
        gossip,
    )
    prompt = generate_prompt_role_play(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = safe_generate_response(prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up)

    print_run_prompts(prompt_template, init_persona, gpt_param, prompt_input, prompt, output)

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]


def run_gpt_prompt_update_learned_in_description_pd_game_v1(
    init_persona,
    self_reflection,
):
    def create_prompt_input(
        init_persona,
        self_reflection,
    ):
        prompt_input = []
        prompt_input += ["You are an expert on updating Innate Traits in an agent description based on its current reputation."]
        prompt_input += [init_persona.scratch.name]
        prompt_input += [init_persona.scratch.learned]
        prompt_input += [json.dumps(init_persona.reputationDB.get_targets_individual_reputation(init_persona.scratch.ID, "player"))]
        prompt_input += [self_reflection]

        return prompt_input

    def __func_validate(gpt_response, prompt=None):
        try:
            persona_name = prompt["user"].split("**Task:**Your name is ")[-1].split(". Using the")[0].strip()
            if persona_name in gpt_response:
                return True
            return False
        except Exception as e:
            print(e)
            return False

    def __func_clean_up(gpt_response, prompt=None):
        import re

        # Strip all asterisks to avoid formatting noise
        gpt_response = gpt_response.replace("*", "")

        # Extract only the "Updated Innate Traits Information:" section (case-insensitive)
        match = re.search(r"Updated\s+Innate\s+Traits\s+Information\s*:(.*)", gpt_response, re.IGNORECASE | re.DOTALL)
        if match:
            response = match.group(1).strip()
        else:
            response = gpt_response.strip()
        return response

    def get_fail_safe():
        fs = "error"
        return fs

    gpt_param = default_gpt_params()
    prompt_template = "prompt/pd_game/update_learned_in_description_v1.txt"
    prompt_input = create_prompt_input(
        init_persona,
        self_reflection,
    )
    prompt = generate_prompt_role_play(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = safe_generate_response(prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up)

    print_run_prompts(prompt_template, init_persona, gpt_param, prompt_input, prompt, output)

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]


def run_gpt_prompt_update_learned_in_description_sign_v1(
    init_persona,
    init_persona_role,
    init_persona_view,
):
    def create_prompt_input(
        init_persona,
        init_persona_role,
        init_persona_view,
    ):
        prompt_input = []
        prompt_input += ["You are an expert on updating learned in an agent description based on its current reputation."]
        prompt_input += [init_persona.scratch.name]
        prompt_input += [init_persona.scratch.learned]
        prompt_input += [json.dumps(init_persona.reputationDB.get_targets_individual_reputation(init_persona.scratch.ID, init_persona_role))]
        prompt_input += [init_persona_view]

        return prompt_input

    def __func_validate(gpt_response, prompt=None):
        try:
            persona_name = prompt["user"].split("**Task:** Based on “")[-1].split("’s Previous Learned")[0].strip()
            print(persona_name)
            print(gpt_response)
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
    prompt_template = "prompt/sign_up/update_learned_in_description_v2.txt"
    prompt_input = create_prompt_input(
        init_persona,
        init_persona_role,
        init_persona_view,
    )
    prompt = generate_prompt_role_play(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = safe_generate_response(prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up)

    print_run_prompts(prompt_template, init_persona, gpt_param, prompt_input, prompt, output)

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]


def run_gpt_prompt_update_learned_in_description_invest_v1(
    init_persona,
    init_persona_role,
    init_persona_view,
):
    def create_prompt_input(
        init_persona,
        init_persona_role,
        init_persona_view,
    ):
        prompt_input = []
        prompt_input += ["You are an expert on updating learned in an agent description based on its current reputation."]
        prompt_input += [init_persona.scratch.name]
        prompt_input += [init_persona.scratch.learned[init_persona_role]]
        prompt_input += [json.dumps(init_persona.reputationDB.get_targets_individual_reputation(init_persona.scratch.ID, init_persona_role))]
        prompt_input += [init_persona_view]

        return prompt_input

    def __func_validate(gpt_response, prompt=None):
        try:
            persona_name = prompt["user"].split("**Task:**")[-1].split("is a")[0].strip()
            print(persona_name)
            print(gpt_response)
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

    if init_persona_role == "investor":
        prompt_template = "prompt/investment/All-update-investor_learned_in_description.txt"
    elif init_persona_role == "trustee":
        prompt_template = "prompt/investment/All-update-trustee_learned_in_description.txt"

    prompt_input = create_prompt_input(
        init_persona,
        init_persona_role,
        init_persona_view,
    )
    prompt = generate_prompt_role_play(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = safe_generate_response(prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up)

    print_run_prompts(prompt_template, init_persona, gpt_param, prompt_input, prompt, output)

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]


def run_gpt_prompt_gossip_listener_select_v2(
    init_persona,
    target_persona_role,
    target_persona,
):
    def create_prompt_input(
        init_persona,
        target_persona,
        target_persona_role,
    ):
        prompt_input = []
        prompt_input += [init_persona.scratch.learned[target_persona_role]] if type(init_persona.scratch.learned) is dict else [init_persona.scratch.learned]
        prompt_input += [init_persona.scratch.name]
        prompt_input += [target_persona.scratch.name]
        bind_list = list(init_persona.scratch.relationship["bind_list"])
        bind_list = [i[0] for i in bind_list]
        prompt_input += [bind_list]
        repus = dict()
        for peronsa_name in bind_list:
            repus[peronsa_name] = init_persona.reputationDB.get_targets_individual_reputation(peronsa_name, target_persona_role)
        prompt_input += [json.dumps(repus)]

        return prompt_input

    def __func_validate(gpt_response, prompt=None):
        try:
            if __func_clean_up(gpt_response, prompt) or __func_clean_up(gpt_response, prompt) == []:
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
    prompt_template = "prompt/gossip_listener_select_v3.txt"
    prompt_input = create_prompt_input(
        init_persona,
        target_persona=target_persona,
        target_persona_role=target_persona_role,
    )
    prompt = generate_prompt_role_play(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = safe_generate_response(prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up)

    print_run_prompts(prompt_template, init_persona, gpt_param, prompt_input, prompt, output)

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]


def run_gpt_prompt_gossip_v2(init_persona, target_persona, reason, complain_target, role=None):
    def create_prompt_input(init_persona, target_persona, reason, complain_target, role=None):
        prompt_input = []
        prompt_input += ["You are now a dialogue generation expert."]
        prompt_input += [init_persona.scratch.name]
        prompt_input += [target_persona.scratch.name]
        prompt_input += [init_persona.scratch.learned[role]] if type(init_persona.scratch.learned) is dict else [init_persona.scratch.learned]
        prompt_input += [target_persona.scratch.learned[role]] if type(target_persona.scratch.learned) is dict else [target_persona.scratch.learned]
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
    prompt_input = create_prompt_input(init_persona, target_persona, reason, complain_target, role)
    prompt = generate_prompt_role_play(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = safe_generate_response(prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up)

    print_run_prompts(prompt_template, init_persona, gpt_param, prompt_input, prompt, output)

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]


def run_gpt_prompt_identify_and_summary_gossip_info_v1(
    init_persona,
    target_persona,
    complain_info,
    init_persona_role,
):
    def create_prompt_input(
        init_persona,
        target_persona,
        complain_info,
        init_persona_role,
    ):
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
        response = gpt_response.split("Gossip info:")[-1].strip()
        return response

    def get_fail_safe():
        fs = "error"
        return fs

    gpt_param = default_gpt_params()
    prompt_template = "prompt/identify_and_summary_gossip_info_v2.txt"
    prompt_input = create_prompt_input(init_persona, target_persona, complain_info, init_persona_role=init_persona_role)
    prompt = generate_prompt_role_play(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = safe_generate_response(prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up)

    print_run_prompts(prompt_template, init_persona, gpt_param, prompt_input, prompt, output)

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]


def run_gpt_prompt_first_order_evaluation_v1(
    init_persona,
    target_persona,
    complain_info,
    init_persona_role,
):
    def create_prompt_input(
        init_persona,
        target_persona,
        complain_info,
        init_persona_role,
    ):
        prompt_input = []
        prompt_input += [init_persona.scratch.learned[init_persona_role]] if type(init_persona.scratch.learned) is dict else [init_persona.scratch.learned]
        prompt_input += [init_persona.scratch.name]
        prompt_input += [target_persona.scratch.name]
        prompt_input += [complain_info["complained name"]]
        prompt_input += [complain_info["complained ID"]]
        gossiper_reputation = init_persona.reputationDB.get_targets_individual_reputation(target_persona.scratch.ID, complain_info["gossiper role"])
        prompt_input += [json.dumps(gossiper_reputation)]
        prompt_input += [complain_info["gossip info"]]
        prompt_input += [init_persona.gossipDB.gossips_count]
        prompt_input += [init_persona.gossipDB.gossips_incredible_count]
        prompt_input += [complain_info["complained role"]]

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
        for _, val in res.items():
            res_fin.append(val)
        return res_fin

    def get_fail_safe():
        fs = "error"
        return fs

    gpt_param = default_gpt_params()
    prompt_template = "prompt/first_order_evaluation_v2.txt"
    prompt_input = create_prompt_input(init_persona, target_persona, complain_info, init_persona_role=init_persona_role)
    prompt = generate_prompt_role_play(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = safe_generate_response(prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up)

    print_run_prompts(prompt_template, init_persona, gpt_param, prompt_input, prompt, output)

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]


def run_gpt_prompt_second_order_evaluation_v1(
    init_persona,
    target_persona,
    complain_info,
    init_persona_role,
):
    def create_prompt_input(
        init_persona,
        target_persona,
        complain_info,
        init_persona_role,
    ):
        prompt_input = []
        prompt_input += [init_persona.scratch.learned[init_persona_role]] if type(init_persona.scratch.learned) is dict else [init_persona.scratch.learned]
        prompt_input += [init_persona.scratch.name]
        prompt_input += [complain_info["first-order listener name"]]
        prompt_input += [complain_info["complained name"]]
        prompt_input += [complain_info["complained ID"]]
        second_gossiper_reputation = init_persona.reputationDB.get_targets_individual_reputation(
            complain_info["first-order listener ID"],
            complain_info["first-order listener role"],
        )
        prompt_input += [json.dumps(second_gossiper_reputation)]
        prompt_input += [complain_info["gossip info"]]
        prompt_input += [init_persona.gossipDB.gossips_count]
        prompt_input += [init_persona.gossipDB.gossips_incredible_count]
        prompt_input += [complain_info["complained role"]]
        prompt_input += [complain_info["original gossiper name"]]
        first_order_gossiper_reputation = init_persona.reputationDB.get_targets_individual_reputation(
            complain_info["original gossiper ID"],
            complain_info["original gossiper role"],
        )
        prompt_input += [json.dumps(first_order_gossiper_reputation)]

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
        for _, val in res.items():
            res_fin.append(val)
        return res_fin

    def get_fail_safe():
        fs = "error"
        return fs

    gpt_param = default_gpt_params()
    prompt_template = "prompt/second_order_evaluation_v2.txt"
    prompt_input = create_prompt_input(init_persona, target_persona, complain_info, init_persona_role=init_persona_role)
    prompt = generate_prompt_role_play(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = safe_generate_response(prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up)

    print_run_prompts(prompt_template, init_persona, gpt_param, prompt_input, prompt, output)

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]


def run_gpt_prompt_connection_build_player_v1(init_persona, target_persona, interaction_memory):
    def create_prompt_input(init_persona, target_persona, interaction_memory):
        prompt_input = []
        prompt_input += [init_persona.scratch.learned]
        prompt_input += [init_persona.scratch.name]
        prompt_input += [target_persona.scratch.name]
        target_persona_reputation = init_persona.reputationDB.get_targets_individual_reputation(target_persona.scratch.ID, "player")
        prompt_input += [json.dumps(target_persona_reputation)]
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
    prompt_template = "prompt/pd_game/connection_after_pd_game_v1.txt"
    prompt_input = create_prompt_input(init_persona, target_persona, interaction_memory)
    prompt = generate_prompt_role_play(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = safe_generate_response(prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up)

    print_run_prompts(prompt_template, init_persona, gpt_param, prompt_input, prompt, output)

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]


def run_gpt_prompt_connection_build_investor_v1(init_persona, target_persona, target_persona_role, interaction_memory):
    def create_prompt_input(init_persona, target_persona, target_persona_role, interaction_memory):
        prompt_input = []
        prompt_input += [init_persona.scratch.learned["investor"]]
        prompt_input += [init_persona.scratch.name]
        prompt_input += [target_persona.scratch.name]
        target_persona_reputation = init_persona.reputationDB.get_targets_individual_reputation(target_persona.scratch.ID, target_persona_role)
        prompt_input += [json.dumps(target_persona_reputation)]
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
    prompt_template = "prompt/investment/All-connection_build_after_investment_v1.txt"
    prompt_input = create_prompt_input(init_persona, target_persona, target_persona_role, interaction_memory)
    prompt = generate_prompt_role_play(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = safe_generate_response(prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up)

    print_run_prompts(prompt_template, init_persona, gpt_param, prompt_input, prompt, output)

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]


def run_gpt_prompt_disconnection_player_v1(init_persona, target_persona, target_persona_role, interaction_memory):
    def create_prompt_input(init_persona, target_persona, target_persona_role, interaction_memory):
        prompt_input = []
        prompt_input += [init_persona.scratch.learned]
        prompt_input += [init_persona.scratch.name]
        prompt_input += [target_persona.scratch.name]
        target_persona_reputation = init_persona.reputationDB.get_targets_individual_reputation(target_persona.scratch.ID, target_persona_role)
        prompt_input += [json.dumps(target_persona_reputation)]
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
    prompt_template = "prompt/pd_game/disconnection_after_pd_game_v1.txt"
    prompt_input = create_prompt_input(init_persona, target_persona, target_persona_role, interaction_memory)
    prompt = generate_prompt_role_play(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = safe_generate_response(prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up)

    print_run_prompts(prompt_template, init_persona, gpt_param, prompt_input, prompt, output)

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]


def run_gpt_prompt_disconnection_investor_v1(init_persona, target_persona, target_persona_role, interaction_memory):
    def create_prompt_input(init_persona, target_persona, target_persona_role, interaction_memory):
        prompt_input = []
        prompt_input += [init_persona.scratch.learned["investor"]]
        prompt_input += [init_persona.scratch.name]
        prompt_input += [target_persona.scratch.name]
        target_persona_reputation = init_persona.reputationDB.get_targets_individual_reputation(target_persona.scratch.ID, target_persona_role)
        prompt_input += [json.dumps(target_persona_reputation)]
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
    prompt_template = "prompt/investment/All-disconnection_after_investment_v1.txt"
    prompt_input = create_prompt_input(init_persona, target_persona, target_persona_role, interaction_memory)
    prompt = generate_prompt_role_play(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = safe_generate_response(prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up)

    print_run_prompts(prompt_template, init_persona, gpt_param, prompt_input, prompt, output)

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]


def run_gpt_prompt_disconnection_after_observed_v1(
    init_persona,
    target_persona,
    init_persona_role,
    target_persona_role,
    interaction_memory,
):
    def create_prompt_input(
        init_persona,
        target_persona,
        init_persona_role,
        target_persona_role,
        interaction_memory,
    ):
        prompt_input = []
        prompt_input += [init_persona.scratch.learned[init_persona_role]]
        prompt_input += [init_persona.scratch.name]
        prompt_input += [target_persona.scratch.name]
        target_persona_reputation = init_persona.reputationDB.get_targets_individual_reputation(target_persona.scratch.ID, target_persona_role)
        prompt_input += [json.dumps(target_persona_reputation)]
        prompt_input += [init_persona.scratch.learned]
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
    prompt_template = "prompt/investment/All-disconnection_after_investment_v1.txt"
    prompt_input = create_prompt_input(
        init_persona,
        target_persona,
        init_persona_role,
        target_persona_role,
        interaction_memory,
    )
    prompt = generate_prompt_role_play(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = safe_generate_response(prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up)

    print_run_prompts(prompt_template, init_persona, gpt_param, prompt_input, prompt, output)

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]


def run_gpt_prompt_connection_build_trustee_v1(init_persona, target_persona, target_persona_role, interaction_memory):
    def create_prompt_input(init_persona, target_persona, target_persona_role, interaction_memory):
        prompt_input = []
        prompt_input += [init_persona.scratch.learned["trustee"]]
        prompt_input += [init_persona.scratch.name]
        prompt_input += [target_persona.scratch.name]
        target_persona_reputation = init_persona.reputationDB.get_targets_individual_reputation(target_persona.scratch.ID, target_persona_role)
        prompt_input += [json.dumps(target_persona_reputation)]
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
    prompt_template = "prompt/investment/All-connection_build_after_investment_v1.txt"
    prompt_input = create_prompt_input(init_persona, target_persona, target_persona_role, interaction_memory)
    prompt = generate_prompt_role_play(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = safe_generate_response(prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up)

    print_run_prompts(prompt_template, init_persona, gpt_param, prompt_input, prompt, output)

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]


def run_gpt_prompt_disconnection_trustee_v1(init_persona, target_persona, target_persona_role, interaction_memory):
    def create_prompt_input(init_persona, target_persona, target_persona_role, interaction_memory):
        prompt_input = []
        prompt_input += [init_persona.scratch.learned["trustee"]]
        prompt_input += [init_persona.scratch.name]
        prompt_input += [target_persona.scratch.name]
        target_persona_reputation = init_persona.reputationDB.get_targets_individual_reputation(target_persona.scratch.ID, target_persona_role)
        prompt_input += [json.dumps(target_persona_reputation)]
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
    prompt_template = "prompt/investment/All-disconnection_after_investment_v1.txt"
    prompt_input = create_prompt_input(init_persona, target_persona, target_persona_role, interaction_memory)
    prompt = generate_prompt_role_play(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = safe_generate_response(prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up)

    print_run_prompts(prompt_template, init_persona, gpt_param, prompt_input, prompt, output)

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]


def run_gpt_prompt_connection_build_after_chat_sign_up_v2(init_persona, target_persona, target_persona_role, interaction_memory):
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
        target_persona_reputation = init_persona.reputationDB.get_targets_individual_reputation(target_persona.scratch.ID, target_persona_role)
        prompt_input += [json.dumps(target_persona_reputation)]
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
    prompt_template = "prompt/sign_up/connection_build_after_chat_sign_up_v3.txt"
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


def run_gpt_prompt_disconnection_after_chat_sign_up_v2(init_persona, target_persona, target_persona_role, interaction_memory):
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
        target_persona_reputation = init_persona.reputationDB.get_targets_individual_reputation(target_persona.scratch.ID, target_persona_role)
        prompt_input += [json.dumps(target_persona_reputation)]
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
    prompt_template = "prompt/sign_up/disconnection_after_chat_sign_up_v3.txt"
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


def run_gpt_prompt_disconnection_after_new_sign_up_v1(init_persona, target_persona, target_persona_role):
    def create_prompt_input(
        init_persona,
        target_persona,
        target_persona_role,
    ):
        prompt_input = []
        prompt_input += [init_persona.scratch.learned]
        prompt_input += [init_persona.scratch.name]
        prompt_input += [target_persona.scratch.name]
        target_persona_reputation = init_persona.reputationDB.get_targets_individual_reputation(target_persona.scratch.ID, target_persona_role)
        prompt_input += [json.dumps(target_persona_reputation)]

        last_choice = init_persona.associativeMemory.get_latest_event()
        if type(last_choice) is dict:
            last_choice = last_choice["description"]
        else:
            last_choice = last_choice.toJSON()["description"]
        last_choice = last_choice.splitlines()
        for line in last_choice:
            if target_persona.name in line:
                # last choice of the persona in memory
                prompt_input += [line.split(":")[-1].strip()]
            elif init_persona.name in line:
                # last choice of the persona in memory
                prompt_input += [line.split(":")[-1].strip()]

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
    prompt_template = "prompt/sign_up/disconnection_only_after_new_sign_up_v1.txt"
    prompt_input = create_prompt_input(
        init_persona,
        target_persona,
        target_persona_role,
    )
    prompt = generate_prompt_role_play(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = safe_generate_response(prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up)

    print_run_prompts(prompt_template, init_persona, gpt_param, prompt_input, prompt, output)

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]


def run_gpt_prompt_disconnection_after_gossip_v2(
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
        target_persona_reputation = init_persona.reputationDB.get_targets_individual_reputation(target_persona.scratch.ID, target_persona_role)
        prompt_input += [json.dumps(target_persona_reputation)]
        prompt_input += [gossiper_name]
        prompt_input += [gossip_info]

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
    prompt_template = "prompt/disconnection_after_gossip_v3.txt"
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


def run_gpt_prompt_self_reputation_init_sign_up_v1(init_persona):
    def create_prompt_input(init_persona):
        prompt_input = []
        prompt_input += [init_persona.scratch.name]
        prompt_input += [init_persona.scratch.learned]
        prompt_input += [init_persona.scratch.ID]

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
        # print(response)
        res = json.loads(response)

        for _, val in res.items():
            full_name = replace_full_name(val["name"])
            if full_name:
                val["name"] = full_name
            else:
                print(f"Full name not found for {val['name']}")
                return False

        if len(res) == 1:
            return res
        return False

    def get_fail_safe():
        fs = "Error"
        return fs

    gpt_param = default_gpt_params()
    prompt_template = "prompt/sign_up/self_reputation_init_sign_up_v1.txt"
    prompt_input = create_prompt_input(init_persona)
    prompt = generate_prompt(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = safe_generate_response(prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up)

    print_run_prompts(prompt_template, init_persona, gpt_param, prompt_input, prompt, output)

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]


def run_gpt_prompt_self_reputation_update_after_pd_game_v1(init_persona, self_reflection):
    def create_prompt_input(init_persona, self_reflection):
        prompt_input = []
        prompt_input += [init_persona.scratch.learned]
        prompt_input += [init_persona.scratch.name]
        prompt_input += [init_persona.scratch.ID]
        prompt_input += [self_reflection]
        self_repu = init_persona.reputationDB.get_targets_individual_reputation(init_persona.scratch.ID, "resident")
        prompt_input += [json.dumps(self_repu)]

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
        # print(response
        res = json.loads(response)

        for _, val in res.items():
            full_name = replace_full_name(val["name"])
            if full_name:
                val["name"] = full_name
            else:
                print(f"Full name not found for {val['name']}")
                return False

        if len(res) == 1:
            return res
        return False

    def get_fail_safe():
        fs = "Error"
        return fs

    gpt_param = default_gpt_params()
    prompt_template = "prompt/pd_game/self_reputation_update_after_pd_game_v1.txt"
    prompt_input = create_prompt_input(init_persona, self_reflection)
    prompt = generate_prompt_role_play(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = safe_generate_response(prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up)

    print_run_prompts(prompt_template, init_persona, gpt_param, prompt_input, prompt, output)

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]


def run_gpt_prompt_other_reputation_update_after_pd_game_v1(init_persona, target_persona, other_reflection):
    def create_prompt_input(init_persona, target_persona, other_reflection):
        prompt_input = []
        prompt_input += [init_persona.scratch.learned]
        prompt_input += [init_persona.name]
        prompt_input += [target_persona.name]
        prompt_input += [target_persona.scratch.ID]
        other_repu = init_persona.reputationDB.get_targets_individual_reputation(target_persona.scratch.ID, "resident")
        prompt_input += [json.dumps(other_repu)]
        prompt_input += [other_reflection]

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
        # print(response
        res = json.loads(response)

        for _, val in res.items():
            full_name = replace_full_name(val["name"])
            if full_name:
                val["name"] = full_name
            else:
                print(f"Full name not found for {val['name']}")
                return False

        if len(res) == 1:
            return res
        return False

    def get_fail_safe():
        fs = "Error"
        return fs

    gpt_param = default_gpt_params()
    prompt_template = "prompt/pd_game/other_reputation_update_after_pd_game_v1.txt"
    prompt_input = create_prompt_input(init_persona, target_persona, other_reflection)
    prompt = generate_prompt_role_play(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = safe_generate_response(prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up)

    print_run_prompts(prompt_template, init_persona, gpt_param, prompt_input, prompt, output)

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]


def run_gpt_prompt_self_reputation_update_after_chat_sign_up_v1(init_persona, sum_convo, ava_satisfy):
    def create_prompt_input(init_persona, sum_convo, ava_satisfy):
        prompt_input = []
        prompt_input += [init_persona.scratch.learned]
        prompt_input += [init_persona.scratch.name]
        prompt_input += [init_persona.scratch.ID]
        prompt_input += [sum_convo]
        prompt_input += [
            round(
                (init_persona.scratch.success_chat_num / init_persona.scratch.total_chat_num),
                3,
            )
        ]
        self_repu = init_persona.reputationDB.get_targets_individual_reputation(init_persona.scratch.ID, "resident")
        prompt_input += [json.dumps(self_repu)]
        prompt_input += [ava_satisfy]

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
        # print(response
        res = json.loads(response)

        for _, val in res.items():
            full_name = replace_full_name(val["name"])
            if full_name:
                val["name"] = full_name
            else:
                print(f"Full name not found for {val['name']}")
                return False

        if len(res) == 1:
            return res
        return False

    def get_fail_safe():
        fs = "Error"
        return fs

    gpt_param = default_gpt_params()
    prompt_template = "prompt/sign_up/self_reputation_update_after_chat_sign_up_v2.txt"
    prompt_input = create_prompt_input(init_persona, sum_convo, ava_satisfy)
    prompt = generate_prompt_role_play(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = safe_generate_response(prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up)

    print_run_prompts(prompt_template, init_persona, gpt_param, prompt_input, prompt, output)

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]


def run_gpt_prompt_other_reputation_update_after_chat_sign_up_v1(
    init_persona,
    target_persona,
    sum_convo,
    total_number_of_people,
    number_of_bidirectional_connections,
    ava_num_bibd_connections,
):
    def create_prompt_input(
        init_persona,
        target_persona,
        sum_convo,
        total_number_of_people,
        number_of_bidirectional_connections,
        ava_num_bibd_connections,
    ):
        prompt_input = []
        prompt_input += [init_persona.scratch.learned]
        prompt_input += [init_persona.name]
        prompt_input += [target_persona.name]
        prompt_input += [sum_convo]
        prompt_input += [target_persona.scratch.ID]
        other_repu = init_persona.reputationDB.get_targets_individual_reputation(target_persona.scratch.ID, "resident")
        prompt_input += [json.dumps(other_repu)]
        prompt_input += [total_number_of_people]
        prompt_input += [number_of_bidirectional_connections]
        prompt_input += [ava_num_bibd_connections]

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
        # print(response)
        res = json.loads(response)

        for _, val in res.items():
            full_name = replace_full_name(val["name"])
            if full_name:
                val["name"] = full_name
            else:
                print(f"Full name not found for {val['name']}")
                return False

        if len(res) == 1:
            return res
        return False

    def get_fail_safe():
        fs = "Error"
        return fs

    gpt_param = default_gpt_params()
    prompt_template = "prompt/sign_up/other_reputation_update_after_chat_sign_up_v2.txt"
    prompt_input = create_prompt_input(
        init_persona,
        target_persona,
        sum_convo,
        total_number_of_people,
        number_of_bidirectional_connections,
        ava_num_bibd_connections,
    )
    prompt = generate_prompt_role_play(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = safe_generate_response(prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up)

    print_run_prompts(prompt_template, init_persona, gpt_param, prompt_input, prompt, output)

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]


def run_gpt_prompt_other_reputation_update_after_new_sign_up_v1(
    init_persona,
    target_persona,
    total_number_of_people,
    number_of_bidirectional_connections,
    ava_num_bibd_connections,
):
    def create_prompt_input(
        init_persona,
        target_persona,
        total_number_of_people,
        number_of_bidirectional_connections,
        ava_num_bibd_connections,
    ):
        prompt_input = []
        prompt_input += [init_persona.scratch.learned]
        prompt_input += [init_persona.name]
        prompt_input += [target_persona.name]
        last_choice = init_persona.associativeMemory.get_latest_event()
        if type(last_choice) is dict:
            last_choice = last_choice["description"]
        else:
            last_choice = last_choice.toJSON()["description"]
        last_choice = last_choice.splitlines()
        for line in last_choice:
            if target_persona.name in line:
                # last choice of the persona in memory
                prompt_input += [line.split(":")[-1].strip()]

        prompt_input += [target_persona.scratch.ID]
        other_repu = init_persona.reputationDB.get_targets_individual_reputation(target_persona.scratch.ID, "resident")
        prompt_input += [json.dumps(other_repu)]
        prompt_input += [total_number_of_people]
        prompt_input += [number_of_bidirectional_connections]
        prompt_input += [ava_num_bibd_connections]
        for line in last_choice:
            if init_persona.name in line:
                # last choice of the persona in memory
                prompt_input += [line.split(":")[-1].strip()]

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
        # print(response)
        res = json.loads(response)

        for _, val in res.items():
            full_name = replace_full_name(val["name"])
            if full_name:
                val["name"] = full_name
            else:
                print(f"Full name not found for {val['name']}")
                return False

        if len(res) == 1:
            return res
        return False

    def get_fail_safe():
        fs = "Error"
        return fs

    gpt_param = default_gpt_params()
    prompt_template = "prompt/sign_up/other_reputation_update_only_after_new_sign_up_v1.txt"
    prompt_input = create_prompt_input(
        init_persona,
        target_persona,
        total_number_of_people,
        number_of_bidirectional_connections,
        ava_num_bibd_connections,
    )
    prompt = generate_prompt_role_play(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = safe_generate_response(prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up)

    print_run_prompts(prompt_template, init_persona, gpt_param, prompt_input, prompt, output)

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]
