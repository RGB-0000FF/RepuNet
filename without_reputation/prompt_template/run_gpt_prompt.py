from .gpt_structure import *


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
            init_persona.associativeMemory.get_latest_event().toJSON()["description"]
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
        prompt_input += [init_persona.scratch.relationship["bind_list"]]

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
        prompt_input += [complain_info["gossip info"]]
        prompt_input += [init_persona.gossipDB.gossips_count]
        prompt_input += [init_persona.gossipDB.gossips_incredible_count]
        prompt_input += [complain_info["first-order listener name"]]
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


def run_gpt_prompt_connection_build_after_stage4_investor_v1(
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
        target_persona_recent_behavior = (
            init_persona.associativeMemory.get_latest_event()
        ).toJSON()

        prompt_input += [target_persona_recent_behavior["description"]]
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
    prompt_template = "prompt/connection_build_after_stage4_investor_v1.txt"
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


def run_gpt_prompt_disconnection_after_stage4_investor_v1(
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
        target_persona_recent_behavior = (
            init_persona.associativeMemory.get_latest_event()
        ).toJSON()
        prompt_input += [target_persona_recent_behavior["description"]]
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
    prompt_template = "prompt/disconnection_after_stage4_investor_v1.txt"
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


def run_gpt_prompt_connection_build_after_stage4_trustee_v1(
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
        target_persona_recent_behavior = (
            init_persona.associativeMemory.get_latest_event()
        ).toJSON()
        prompt_input += [target_persona_recent_behavior["description"]]
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
    prompt_template = "prompt/connection_build_after_stage4_trustee_v1.txt"
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


def run_gpt_prompt_disconnection_after_stage4_trustee_v1(
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
        target_persona_recent_behavior = (
            init_persona.associativeMemory.get_latest_event()
        ).toJSON()
        prompt_input += [target_persona_recent_behavior["description"]]
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
    prompt_template = "prompt/disconnection_after_stage4_trustee_v1.txt"
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
    init_persona, target_persona, target_persona_role, gossiper_name, gossip_info
):
    def create_prompt_input(
        init_persona, target_persona, target_persona_role, gossiper_name, gossip_info
    ):
        prompt_input = []
        prompt_input += [init_persona.scratch.name]
        prompt_input += [target_persona.scratch.name]
        prompt_input += [gossip_info]
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
        init_persona, target_persona, target_persona_role, gossiper_name, gossip_info
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
