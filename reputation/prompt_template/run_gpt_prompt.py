from .gpt_structure import *


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
    init_persona_role,
    target_persona_role,
    init_behavior_summary,
    target_behavior_summary,
    total_number_of_people,
    number_of_bidirectional_connections,
):
    def create_prompt_input(
        init_persona,
        target_persona,
        init_persona_role,
        target_persona_role,
        init_behavior_summary,
        target_behavior_summary,
        total_number_of_people,
        number_of_bidirectional_connections,
    ):
        prompt_input = []
        prompt_input += [init_persona.scratch.name]
        prompt_input += [target_persona.scratch.name]
        prompt_input += [init_persona.scratch.ID]
        prompt_input += [target_persona.scratch.ID]
        prompt_input += [init_behavior_summary]
        prompt_input += [target_behavior_summary]
        init_persona_reputation = (
            init_persona.reputationDB.get_targets_individual_reputation(
                init_persona.scratch.ID, init_persona_role
            )
        )
        target_persona_reputation = (
            init_persona.reputationDB.get_targets_individual_reputation(
                target_persona.scratch.ID, target_persona_role
            )
        )
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
    prompt_template = "prompt/reputation_update_after_stage4_investor_v1.txt"
    prompt_input = create_prompt_input(
        init_persona,
        target_persona,
        init_persona_role,
        target_persona_role,
        init_behavior_summary,
        target_behavior_summary,
        total_number_of_people,
        number_of_bidirectional_connections,
    )
    prompt = generate_prompt(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = safe_generate_response(
        prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up
    )

    print_run_prompts(
        prompt_template, init_persona, gpt_param, prompt_input, prompt, output
    )

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]


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
        init_persona_reputation = (
            init_persona.reputationDB.get_targets_individual_reputation(
                init_persona.scratch.ID, init_persona_role
            )
        )
        target_persona_reputation = (
            init_persona.reputationDB.get_targets_individual_reputation(
                target_persona.scratch.ID, target_persona_role
            )
        )
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
    prompt_template = "prompt/reputation_update_after_stage1_investor_v1.txt"
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
    output = safe_generate_response(
        prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up
    )

    print_run_prompts(
        prompt_template, init_persona, gpt_param, prompt_input, prompt, output
    )

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]


def run_gpt_prompt_reputation_update_after_stage4_trustee_v1(
    init_persona,
    target_persona,
    init_persona_role,
    target_persona_role,
    init_behavior_summary,
    target_behavior_summary,
    total_number_of_people,
    number_of_bidirectional_connections,
):
    def create_prompt_input(
        init_persona,
        target_persona,
        init_persona_role,
        target_persona_role,
        init_behavior_summary,
        target_behavior_summary,
        total_number_of_people,
        number_of_bidirectional_connections,
    ):
        prompt_input = []
        prompt_input += [init_persona.scratch.name]
        prompt_input += [target_persona.scratch.name]
        prompt_input += [init_persona.scratch.ID]
        prompt_input += [target_persona.scratch.ID]
        prompt_input += [init_behavior_summary]
        prompt_input += [target_behavior_summary]
        init_persona_reputation = (
            init_persona.reputationDB.get_targets_individual_reputation(
                init_persona.scratch.ID, init_persona_role
            )
        )
        target_persona_reputation = (
            init_persona.reputationDB.get_targets_individual_reputation(
                target_persona.scratch.ID, target_persona_role
            )
        )
        prompt_input += [json.dumps(init_persona_reputation)]
        prompt_input += [json.dumps(target_persona_reputation)]
        prompt_input += [total_number_of_people]
        prompt_input += [number_of_bidirectional_connections]
        prompt_input += [
            init_persona.scratch.success_num_investor
            / init_persona.scratch.total_num_trustee
        ]

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
    prompt_template = "prompt/reputation_update_after_stage4_trustee_v1.txt"
    prompt_input = create_prompt_input(
        init_persona,
        target_persona,
        init_persona_role,
        target_persona_role,
        init_behavior_summary,
        target_behavior_summary,
        total_number_of_people,
        number_of_bidirectional_connections,
    )
    prompt = generate_prompt(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = safe_generate_response(
        prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up
    )

    print_run_prompts(
        prompt_template, init_persona, gpt_param, prompt_input, prompt, output
    )

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
        init_persona_reputation = (
            init_persona.reputationDB.get_targets_individual_reputation(
                init_persona.scratch.ID, init_persona_role
            )
        )
        target_persona_reputation = (
            init_persona.reputationDB.get_targets_individual_reputation(
                target_persona.scratch.ID, target_persona_role
            )
        )
        prompt_input += [json.dumps(init_persona_reputation)]
        prompt_input += [json.dumps(target_persona_reputation)]
        prompt_input += [total_number_of_people]
        prompt_input += [number_of_bidirectional_connections]
        prompt_input += [
            init_persona.scratch.success_num_investor
            / init_persona.scratch.total_num_trustee
        ]

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
    prompt_template = "prompt/reputation_update_after_stage1_trustee_v1.txt"
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
    output = safe_generate_response(
        prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up
    )

    print_run_prompts(
        prompt_template, init_persona, gpt_param, prompt_input, prompt, output
    )

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]


def run_gpt_prompt_reputation_update_after_gossip_v1(
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
        prompt_input += [init_persona.scratch.name]
        prompt_input += [target_persona.scratch.name]
        prompt_input += [target_persona.scratch.ID]
        prompt_input += [gossip["gossiper name"]]
        target_persona_reputation = (
            init_persona.reputationDB.get_targets_individual_reputation(
                target_persona.scratch.ID, target_persona_role
            )
        )
        prompt_input += [json.dumps(target_persona_reputation)]
        prompt_input += [json.dumps(gossip)]
        if target_persona_role.lower() == "investor":
            prompt_input += ["Investor"]
        elif target_persona_role.lower() == "trustee":
            prompt_input += ["Trustee"]
        prompt_input += [total_number_of_people]
        prompt_input += [number_of_bidirectional_connections]
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
    prompt_template = "prompt/reputation_update_after_gossip_v1.txt"
    prompt_input = create_prompt_input(
        init_persona,
        target_persona,
        gossip,
        target_persona_role,
        total_number_of_people,
        number_of_bidirectional_connections,
    )
    prompt = generate_prompt(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = safe_generate_response(
        prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up
    )

    print_run_prompts(
        prompt_template, init_persona, gpt_param, prompt_input, prompt, output
    )

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]


def run_gpt_prompt_update_learned_in_description_v1(
    init_persona,
    init_persona_role,
):
    def create_prompt_input(
        init_persona,
        init_persona_role,
    ):
        prompt_input = []
        prompt_input += [init_persona.scratch.name]
        prompt_input += [init_persona.scratch.learned]
        prompt_input += [
            json.dumps(
                init_persona.reputationDB.get_targets_individual_reputation(
                    init_persona.scratch.ID, init_persona_role
                )
            )
        ]

        return prompt_input

    def __func_validate(gpt_response, prompt=None):
        try:
            if "Updated “learned” information:" in gpt_response:
                return True
            return False
        except Exception as e:
            print(e)
            return False

    def __func_clean_up(gpt_response, prompt=None):
        response = gpt_response.split("Updated “learned” information:")[-1].strip()
        return response

    def get_fail_safe():
        fs = []
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
    prompt_template = "prompt/update_learned_in_description_v1.txt"
    prompt_input = create_prompt_input(
        init_persona,
        init_persona_role,
    )
    prompt = generate_prompt(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = safe_generate_response(
        prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up
    )

    print_run_prompts(
        prompt_template, init_persona, gpt_param, prompt_input, prompt, output
    )

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
        prompt_input += [init_persona.scratch.name]
        prompt_input += [target_persona.scratch.name]
        bind_list = list(init_persona.scratch.relationship["bind_list"])
        prompt_input += [[i[0] for i in bind_list]]

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
        response = gpt_response.split("Selected person's list:")[-1].strip()
        res = json.loads(response)
        for val in res:
            full_name = replace_full_name(val["name"])
            if full_name:
                val["name"] = full_name
            else:
                print(f"Full name not found for {val['name']}")
                return False
        return res

    def get_fail_safe():
        fs = []
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
    prompt_template = "prompt/gossip_listener_select_v1.txt"
    prompt_input = create_prompt_input(
        init_persona,
        target_persona,
        init_persona_role,
    )
    prompt = generate_prompt(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = safe_generate_response(
        prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up
    )

    print_run_prompts(
        prompt_template, init_persona, gpt_param, prompt_input, prompt, output
    )

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]


def run_gpt_prompt_gossip_v1(init_persona, target_persona, reason):
    def create_prompt_input(
        init_persona,
        target_persona,
        reason,
    ):
        prompt_input = []
        prompt_input += [init_persona.scratch.name]
        prompt_input += [target_persona.scratch.name]
        prompt_input += [init_persona.scratch.learned]
        prompt_input += [target_persona.scratch.learned]
        prompt_input += [reason]

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
        fs = []
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
    prompt_template = "prompt/create_gossip_chat_v1.txt"
    prompt_input = create_prompt_input(
        init_persona,
        target_persona,
        reason,
    )
    prompt = generate_prompt(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = safe_generate_response(
        prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up
    )

    print_run_prompts(
        prompt_template, init_persona, gpt_param, prompt_input, prompt, output
    )

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]


def run_gpt_prompt_identify_and_summary_gossip_info_v1(
    init_persona, target_persona, complain_info
):
    def create_prompt_input(
        init_persona,
        target_persona,
        complain_info,
    ):
        prompt_input = []
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
        fs = []
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
    prompt_template = "prompt/identify_and_summary_gossip_info_v1.txt"
    prompt_input = create_prompt_input(
        init_persona,
        target_persona,
        complain_info,
    )
    prompt = generate_prompt(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = safe_generate_response(
        prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up
    )

    print_run_prompts(
        prompt_template, init_persona, gpt_param, prompt_input, prompt, output
    )

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]


def run_gpt_prompt_first_order_evaluation_v1(
    init_persona, target_persona, complain_info
):
    def create_prompt_input(
        init_persona,
        target_persona,
        complain_info,
    ):
        prompt_input = []
        prompt_input += [init_persona.scratch.name]
        prompt_input += [target_persona.scratch.name]
        prompt_input += [complain_info["complained name"]]
        prompt_input += [complain_info["complained ID"]]
        gossiper_reputation = (
            init_persona.reputationDB.get_targets_individual_reputation(
                target_persona.scratch.ID, complain_info["gossiper role"]
            )
        )
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
        fs = []
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
    prompt_template = "prompt/first_order_evaluation_v1.txt"
    prompt_input = create_prompt_input(
        init_persona,
        target_persona,
        complain_info,
    )
    prompt = generate_prompt(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = safe_generate_response(
        prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up
    )

    print_run_prompts(
        prompt_template, init_persona, gpt_param, prompt_input, prompt, output
    )

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]


def run_gpt_prompt_second_order_evaluation_v1(
    init_persona, target_persona, complain_info
):
    def create_prompt_input(
        init_persona,
        target_persona,
        complain_info,
    ):
        prompt_input = []
        prompt_input += [init_persona.scratch.name]
        prompt_input += [complain_info["original gossiper name"]]
        prompt_input += [complain_info["complained name"]]
        prompt_input += [complain_info["complained ID"]]
        original_gossiper_reputation = (
            init_persona.reputationDB.get_targets_individual_reputation(
                complain_info["original gossiper ID"],
                complain_info["original gossiper role"],
            )
        )
        prompt_input += [json.dumps(original_gossiper_reputation)]
        prompt_input += [complain_info["gossip info"]]
        prompt_input += [init_persona.gossipDB.gossips_count]
        prompt_input += [init_persona.gossipDB.gossips_incredible_count]
        prompt_input += [complain_info["first-order listener name"]]
        first_order_listener_reputation = (
            init_persona.reputationDB.get_targets_individual_reputation(
                complain_info["first-order listener ID"],
                complain_info["first-order listener role"],
            )
        )
        prompt_input += [json.dumps(first_order_listener_reputation)]
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
        fs = []
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
    prompt_template = "prompt/second_order_evaluation_v1.txt"
    prompt_input = create_prompt_input(
        init_persona,
        target_persona,
        complain_info,
    )
    prompt = generate_prompt(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = safe_generate_response(
        prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up
    )

    print_run_prompts(
        prompt_template, init_persona, gpt_param, prompt_input, prompt, output
    )

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]


def run_gpt_prompt_connection_build_investor_v1(
    init_persona, target_persona, target_persona_role
):
    def create_prompt_input(
        init_persona,
        target_persona,
        target_persona_role,
    ):
        prompt_input = []
        prompt_input += [init_persona.scratch.name]
        prompt_input += [target_persona.scratch.name]
        target_persona_reputation = (
            init_persona.reputationDB.get_targets_individual_reputation(
                target_persona.scratch.ID, target_persona_role
            )
        )
        prompt_input += [json.dumps(target_persona_reputation)]
        prompt_input += [init_persona.scratch.learned]

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
        fs = []
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
    prompt_template = "prompt/connection_build_investor_v1.txt"
    prompt_input = create_prompt_input(
        init_persona,
        target_persona,
        target_persona_role,
    )
    prompt = generate_prompt(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = safe_generate_response(
        prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up
    )

    print_run_prompts(
        prompt_template, init_persona, gpt_param, prompt_input, prompt, output
    )

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]


def run_gpt_prompt_disconnection_investor_v1(
    init_persona, target_persona, target_persona_role
):
    def create_prompt_input(
        init_persona,
        target_persona,
        target_persona_role,
    ):
        prompt_input = []
        prompt_input += [init_persona.scratch.name]
        prompt_input += [target_persona.scratch.name]
        target_persona_reputation = (
            init_persona.reputationDB.get_targets_individual_reputation(
                target_persona.scratch.ID, target_persona_role
            )
        )
        prompt_input += [json.dumps(target_persona_reputation)]
        prompt_input += [init_persona.scratch.learned]

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
        fs = []
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
    prompt_template = "prompt/disconnection_investor_v1.txt"
    prompt_input = create_prompt_input(
        init_persona,
        target_persona,
        target_persona_role,
    )
    prompt = generate_prompt(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = safe_generate_response(
        prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up
    )

    print_run_prompts(
        prompt_template, init_persona, gpt_param, prompt_input, prompt, output
    )

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]


def run_gpt_prompt_connection_build_trustee_v1(
    init_persona, target_persona, target_persona_role
):
    def create_prompt_input(
        init_persona,
        target_persona,
        target_persona_role,
    ):
        prompt_input = []
        prompt_input += [init_persona.scratch.name]
        prompt_input += [target_persona.scratch.name]
        target_persona_reputation = (
            init_persona.reputationDB.get_targets_individual_reputation(
                target_persona.scratch.ID, target_persona_role
            )
        )
        prompt_input += [json.dumps(target_persona_reputation)]
        prompt_input += [init_persona.scratch.learned]

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
        fs = []
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
    prompt_template = "prompt/connection_build_trustee_v1.txt"
    prompt_input = create_prompt_input(
        init_persona,
        target_persona,
        target_persona_role,
    )
    prompt = generate_prompt(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = safe_generate_response(
        prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up
    )

    print_run_prompts(
        prompt_template, init_persona, gpt_param, prompt_input, prompt, output
    )

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]


def run_gpt_prompt_disconnection_trustee_v1(
    init_persona, target_persona, target_persona_role
):
    def create_prompt_input(
        init_persona,
        target_persona,
        target_persona_role,
    ):
        prompt_input = []
        prompt_input += [init_persona.scratch.name]
        prompt_input += [target_persona.scratch.name]
        target_persona_reputation = (
            init_persona.reputationDB.get_targets_individual_reputation(
                target_persona.scratch.ID, target_persona_role
            )
        )
        prompt_input += [json.dumps(target_persona_reputation)]
        prompt_input += [init_persona.scratch.learned]

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
        fs = []
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
    prompt_template = "prompt/disconnection_trustee_v1.txt"
    prompt_input = create_prompt_input(
        init_persona,
        target_persona,
        target_persona_role,
    )
    prompt = generate_prompt(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = safe_generate_response(
        prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up
    )

    print_run_prompts(
        prompt_template, init_persona, gpt_param, prompt_input, prompt, output
    )

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]


def run_gpt_prompt_disconnection_after_gossip_v1(
    init_persona, target_persona, target_persona_role, gossiper_name
):
    def create_prompt_input(
        init_persona, target_persona, target_persona_role, gossiper_name
    ):
        prompt_input = []
        prompt_input += [init_persona.scratch.name]
        prompt_input += [target_persona.scratch.name]
        target_persona_reputation = (
            init_persona.reputationDB.get_targets_individual_reputation(
                target_persona.scratch.ID, target_persona_role
            )
        )
        prompt_input += [json.dumps(target_persona_reputation)]
        prompt_input += [gossiper_name]
        prompt_input += [init_persona.scratch.learned]

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
        fs = []
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
    prompt_template = "prompt/disconnection_after_gossip_v1.txt"
    prompt_input = create_prompt_input(
        init_persona, target_persona, target_persona_role, gossiper_name
    )
    prompt = generate_prompt(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = safe_generate_response(
        prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up
    )

    print_run_prompts(
        prompt_template, init_persona, gpt_param, prompt_input, prompt, output
    )

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]


def run_gpt_prompt_self_reputation_init_sign_upv1(
    init_persona, target_persona, complain_info
):
    def create_prompt_input(
        init_persona,
    ):
        prompt_input = []
        prompt_input += [init_persona.scratch.name]
        prompt_input += [target_persona.scratch.learned]
        prompt_input += [target_persona.scratch.ID]

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
        final_res = dict()
        res = json.loads(response)

        for _, val in res.items():
            full_name = replace_full_name(val["name"])
            if full_name:
                val["name"] = full_name
            else:
                print(f"Full name not found for {val['name']}")
                return False

        if len(final_res) == 1:
            return final_res
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
    prompt_template = "prompt/first_order_evaluation_v1.txt"
    prompt_input = create_prompt_input(
        init_persona,
        target_persona,
        complain_info,
    )
    prompt = generate_prompt(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = safe_generate_response(
        prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up
    )

    print_run_prompts(
        prompt_template, init_persona, gpt_param, prompt_input, prompt, output
    )

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]
