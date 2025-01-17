from .gpt_structure import *
text1="You have never been an investor before, so you are not sure about your reputation."
text2="This trustee had little interaction with you and your friends in the past, and you were not very aware of its reputation."
text3="You have never been an trustee before, so you were not sure about your reputation."
text4="This investor had little interaction with you and your friends in the past, and you were not very aware of its reputation."
def run_gpt_prompt_investor_decided_v1(
    init_persona, target_persona, allocation_plan, verbose=False
):
    global text1 
    global text2
    def create_prompt_input(init_persona, target_persona, allocation_plan):
        global text1
        global text2
        prompt_input = []
        prompt_input += [init_persona.scratch.learned]
        prompt_input += [allocation_plan]
        prompt_input += [init_persona.scratch.resources_unit]
        init_reputation = init_persona.reputationDB.get_targets_individual_reputation(
            init_persona.scratch.ID, "investor"
        )
        target_reputation = (
            init_persona.reputationDB.get_targets_individual_reputation(
                target_persona.scratch.ID, "trustee"
            )
        )
        if not init_reputation:
            init_reputation = text1
        if not target_reputation:
            target_reputation = text2
        prompt_input += [init_reputation]
        prompt_input += [target_reputation]
        memory_list,_=init_persona.get_latest_memory_list()
        memory=""
        for m in memory_list:
            memory+="Memory:" + m + "\n"

        prompt_input.append(memory)
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
        if "Refuse" in gpt_response:
            return gpt_response.replace("*", "")
        elif "Accept" in gpt_response:
            allocation = gpt_response.split("Allocate")[-1].split("units")[0].strip()
            return f"Accept. Allocation {allocation} unit."
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
    prompt_input = create_prompt_input(init_persona, target_persona, allocation_plan)
    if prompt_input[3] == text1 or prompt_input[4] == text2:
        prompt_input.pop(3)
        prompt_input.pop(3)
        prompt_template="prompt/stage_1/stage_1_investor_v2.txt"
        prompt = generate_prompt_role_play(prompt_input, prompt_template)
    else:
        prompt_template="prompt/stage_1/stage_1_investor_v1.txt"
        prompt = generate_prompt_role_play(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = safe_generate_response(
        prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up
    ).strip()

    if verbose:
        print_run_prompts(
            prompt_template, init_persona, gpt_param, prompt_input, prompt, output
        )

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]


def run_gpt_prompt_trustee_plan_v1(init_persona, target_persona, verbose=False):
    global text3
    global text4
    def create_prompt_input(init_persona, target_persona):
        global text3
        global text4
        prompt_input = []
        prompt_input += [init_persona.scratch.learned]
        init_reputation = init_persona.reputationDB.get_targets_individual_reputation(
            init_persona.scratch.ID, "trustee"
        )
        target_reputation = (
            init_persona.reputationDB.get_targets_individual_reputation(
                target_persona.scratch.ID, "investor"
            )
        )
        if not init_reputation:
            init_reputation = text3
        if not target_reputation:
            target_reputation = text4
        prompt_input += [init_reputation]
        prompt_input += [target_reputation]
        _,memory_list=init_persona.get_latest_memory_list()
        memory=""
        for m in memory_list:
            memory+="Memory:" + m + "\n"
        prompt_input.append(memory)
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
        if "Trustee proposes a resource allocation plan" in gpt_response:
            return gpt_response.replace("*", "")
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
    
    prompt_input = create_prompt_input(init_persona, target_persona)
    
    if prompt_input[1] == text3 or prompt_input[2] == text4:
        prompt_input.pop(1)
        prompt_input.pop(1)
        prompt_template="prompt/stage_1/stage_1_trustee_v2.txt"
        prompt = generate_prompt_role_play(prompt_input, prompt_template)
    else:
        prompt_template="prompt/stage_1/stage_1_trustee_v1.txt"
        prompt = generate_prompt_role_play(prompt_input, prompt_template)
    fail_safe = get_fail_safe()
    output = safe_generate_response(
        prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up
    ).strip()

    if verbose:
        print_run_prompts(
            prompt_template, init_persona, gpt_param, prompt_input, prompt, output
        )

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]


def run_gpt_prompt_trustee_stage_3_actual_allocation_v1(
    init_persona,
    target_persona,
    trustee_plan,
    investor_resource,
    k,
    actual_distributable,
    verbose=False,
):
    def create_prompt_input(
        init_persona,
        target_persona,
        trustee_plan,
        investor_resource,
        k,
        actual_distributable,
    ):
        prompt_input = []
        prompt_input += [init_persona.scratch.learned]
        trustee_reputation = (
            target_persona.reputationDB.get_targets_individual_reputation(
                target_persona.scratch.ID, "trustee"
            )
        )
        investor_reputation = (
            target_persona.reputationDB.get_targets_individual_reputation(
                init_persona.scratch.ID, "investor"
            )
        )
        if not trustee_reputation:
            trustee_reputation = "None"
        if not investor_reputation:
            investor_reputation = "None"
        prompt_input += [trustee_reputation]
        prompt_input += [investor_reputation]
        prompt_input += [trustee_plan]
        prompt_input += [investor_resource]
        prompt_input += [k]
        prompt_input += [actual_distributable]
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
        gpt_response = gpt_response.replace("*", "")
        res = dict()
        res["trustee"] = (
            gpt_response.split("Trustee receives")[-1]
            .split("units")[0]
            .replace(",", "")
            .strip()
        )
        res["investor"] = (
            gpt_response.split("investor receives")[-1]
            .split("units")[0]
            .replace(",", "")
            .strip()
        )
        res["reported_investment_outcome"] = gpt_response.split(
            "Reported Investment Outcome:"
        )[-1].strip()
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
    prompt_template = "prompt/stage_3/stage_3_trustee_v1.txt"
    prompt_input = create_prompt_input(
        init_persona,
        target_persona,
        trustee_plan,
        investor_resource,
        k,
        actual_distributable,
    )
    prompt = generate_prompt_role_play(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = safe_generate_response(
        prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up
    )

    if verbose:
        print_run_prompts(
            prompt_template, init_persona, gpt_param, prompt_input, prompt, output
        )

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]


def run_gpt_prompt_stage4_investor_evaluation_v1(
    init_persona,
    target_persona,
    trustee_plan,
    investor_resource,
    k,
    actual_distributable,
    trustee_share,
    investor_share,
    reported_resource,
    trustee_allocated,
    investor_allocated,
    verbose=False,
):
    def create_prompt_input(
        init_persona,
        target_persona,
        trustee_plan,
        investor_resource,
        k,
        actual_distributable,
        trustee_share,
        investor_share,
        reported_resource,
        trustee_allocated,
        investor_allocated,
    ):
        prompt_input = []
        prompt_input += [init_persona.scratch.learned]
        investor_reputation = (
            init_persona.reputationDB.get_targets_individual_reputation(
                init_persona.scratch.ID, "investor"
            )
        )
        prompt_input += [investor_reputation]
        trustee_reputation = (
            init_persona.reputationDB.get_targets_individual_reputation(
                target_persona.scratch.ID, "trustee"
            )
        )
        if not trustee_reputation:
            trustee_reputation = "None"
        prompt_input += [trustee_reputation]
        prompt_input += [trustee_plan]
        prompt_input += [investor_resource]
        prompt_input += [k]
        prompt_input += [actual_distributable]
        prompt_input += [trustee_share]
        prompt_input += [investor_share]
        prompt_input += [reported_resource]
        prompt_input += [trustee_allocated]
        prompt_input += [investor_allocated]
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
        non_empty_lines = [
            line for line in gpt_response.splitlines() if line.strip() != ""
        ]
        res["self_reputation"] = (
            non_empty_lines[0]
            .split("Self (Investor) Reputation Reflection:")[-1]
            .strip()
        )
        res["trustee_reputation"] = (
            non_empty_lines[1].split("Trustee Reputation Reflection:")[-1].strip()
        )
        for val in res.values():
            if val == "":
                return False
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
    prompt_template = "prompt/stage_4/stage_4_investor.txt"
    prompt_input = create_prompt_input(
        init_persona,
        target_persona,
        trustee_plan,
        investor_resource,
        k,
        actual_distributable,
        trustee_share,
        investor_share,
        reported_resource,
        trustee_allocated,
        investor_allocated,
    )
    prompt = generate_prompt_role_play(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = safe_generate_response(
        prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up
    )

    if verbose:
        print_run_prompts(
            prompt_template, init_persona, gpt_param, prompt_input, prompt, output
        )

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]


def run_gpt_prompt_stage4_trustee_evaluation_v1(
    init_persona,
    target_persona,
    trustee_plan,
    investor_resource,
    k,
    actual_distributable,
    trustee_share,
    investor_share,
    reported_resource,
    trustee_allocated,
    investor_allocated,
    verbose=False,
):
    def create_prompt_input(
        init_persona,
        target_persona,
        trustee_plan,
        investor_resource,
        k,
        actual_distributable,
        trustee_share,
        investor_share,
        reported_resource,
        trustee_allocated,
        investor_allocated,
    ):
        prompt_input = []
        prompt_input += [init_persona.scratch.learned]
        trustee_reputation = (
            init_persona.reputationDB.get_targets_individual_reputation(
                init_persona.scratch.ID, "trustee"
            )
        )
        prompt_input += [trustee_reputation]
        investor_reputation = (
            init_persona.reputationDB.get_targets_individual_reputation(
                target_persona.scratch.ID, "investor"
            )
        )
        if not investor_reputation:
            investor_reputation = "None"
        prompt_input += [investor_reputation]
        prompt_input += [trustee_plan]
        prompt_input += [str(investor_resource)]
        prompt_input += [str(k)]
        prompt_input += [str(actual_distributable)]
        prompt_input += [str(trustee_share)]
        prompt_input += [str(investor_share)]
        prompt_input += [str(reported_resource)]
        prompt_input += [str(trustee_allocated)]
        prompt_input += [str(investor_allocated)]
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
            res = dict()
            gpt_response = gpt_response.replace("*", "")
            non_empty_lines = [
                line for line in gpt_response.splitlines() if line.strip() != ""
            ]
            res["self_reputation"] = (
                non_empty_lines[0]
                .split("Self (Trustee) Reputation Reflection:")[-1]
                .strip()
            )
            res["investor_reputation"] = (
                non_empty_lines[1].split("Investor Reputation Reflection:")[-1].strip()
            )
            for val in res.values():
                if val == "":
                    return False
            return res
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
    prompt_template = "prompt/stage_4/stage_4_trustee.txt"
    prompt_input = create_prompt_input(
        init_persona,
        target_persona,
        trustee_plan,
        investor_resource,
        k,
        actual_distributable,
        trustee_share,
        investor_share,
        reported_resource,
        trustee_allocated,
        investor_allocated,
    )
    prompt = generate_prompt_role_play(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = safe_generate_response(
        prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up
    )

    if verbose:
        print_run_prompts(
            prompt_template, init_persona, gpt_param, prompt_input, prompt, output
        )

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]


def run_gpt_prompt_stage1_trustee_gossip_willing_v1(
    init_persona,
    trustee_plan,
    reject_reason,
    verbose=False,
):
    def create_prompt_input(
        init_persona,
        trustee_plan,
        reject_reason,
    ):
        prompt_input = []
        prompt_input += [init_persona.scratch.learned]
        prompt_input += [trustee_plan]
        prompt_input += [reject_reason]
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
            if "Whether to Gossip:" not in gpt_response:
                return False
            gpt_response = gpt_response.replace("*", "")
            return gpt_response.split("Whether to Gossip:")[-1].strip()
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
    prompt_template = "prompt/stage_1/stage_1_trustee_gossip.txt"
    prompt_input = create_prompt_input(
        init_persona,
        trustee_plan,
        reject_reason,
    )
    prompt = generate_prompt_role_play(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = safe_generate_response(
        prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up
    )

    if verbose:
        print_run_prompts(
            prompt_template, init_persona, gpt_param, prompt_input, prompt, output
        )

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]


def run_gpt_prompt_stage1_investor_gossip_willing_v1(
    init_persona,
    trustee_plan,
    reject_reason,
    verbose=False,
):
    def create_prompt_input(
        init_persona,
        trustee_plan,
        reject_reason,
    ):
        prompt_input = []
        prompt_input += [init_persona.scratch.learned]
        prompt_input += [trustee_plan]
        prompt_input += [reject_reason]
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
            if "Whether to Gossip:" not in gpt_response:
                return False
            gpt_response = gpt_response.replace("*", "")
            return gpt_response.split("Whether to Gossip:")[-1].strip()
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
    prompt_template = "prompt/stage_1/stage_1_investor_gossip.txt"
    prompt_input = create_prompt_input(
        init_persona,
        trustee_plan,
        reject_reason,
    )
    prompt = generate_prompt_role_play(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = safe_generate_response(
        prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up
    )

    if verbose:
        print_run_prompts(
            prompt_template, init_persona, gpt_param, prompt_input, prompt, output
        )

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]


def run_gpt_prompt_stage4_investor_gossip_v1(
    init_persona,
    target_persona,
    trustee_plan,
    investor_resource,
    k,
    actual_distributable,
    trustee_share,
    investor_share,
    reported_resource,
    trustee_allocated,
    investor_allocated,
    verbose=False,
):
    def create_prompt_input(
        init_persona,
        target_persona,
        trustee_plan,
        investor_resource,
        k,
        actual_distributable,
        trustee_share,
        investor_share,
        reported_resource,
        trustee_allocated,
        investor_allocated,
    ):
        prompt_input = []
        prompt_input += [init_persona.scratch.learned]
        prompt_input += [trustee_plan]
        prompt_input += [investor_resource]
        prompt_input += [k]
        prompt_input += [actual_distributable]
        prompt_input += [trustee_share]
        prompt_input += [investor_share]
        prompt_input += [reported_resource]
        prompt_input += [trustee_allocated]
        prompt_input += [investor_allocated]
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
        if "Whether to Gossip:" not in gpt_response:
            return False
        gpt_response = gpt_response.replace("*", "")
        return gpt_response.split("Whether to Gossip:")[-1].strip()

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
    prompt_template = "prompt/stage_4/stage_4_investor_gossip.txt"
    prompt_input = create_prompt_input(
        init_persona,
        target_persona,
        trustee_plan,
        investor_resource,
        k,
        actual_distributable,
        trustee_share,
        investor_share,
        reported_resource,
        trustee_allocated,
        investor_allocated,
    )
    prompt = generate_prompt_role_play(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = safe_generate_response(
        prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up
    )

    if verbose:
        print_run_prompts(
            prompt_template, init_persona, gpt_param, prompt_input, prompt, output
        )

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]


def run_gpt_prompt_stage4_trustee_gossip_v1(
    init_persona,
    target_persona,
    trustee_plan,
    investor_resource,
    k,
    actual_distributable,
    trustee_share,
    investor_share,
    reported_resource,
    trustee_allocated,
    investor_allocated,
    verbose=False,
):
    def create_prompt_input(
        init_persona,
        target_persona,
        trustee_plan,
        investor_resource,
        k,
        actual_distributable,
        trustee_share,
        investor_share,
        reported_resource,
        trustee_allocated,
        investor_allocated,
    ):
        prompt_input = []
        prompt_input += [init_persona.scratch.learned]
        prompt_input += [trustee_plan]
        prompt_input += [str(investor_resource)]
        prompt_input += [str(k)]
        prompt_input += [str(actual_distributable)]
        prompt_input += [str(trustee_share)]
        prompt_input += [str(investor_share)]
        prompt_input += [str(reported_resource)]
        prompt_input += [str(trustee_allocated)]
        prompt_input += [str(investor_allocated)]
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
            if "Whether to Gossip:" not in gpt_response:
                return False
            gpt_response = gpt_response.replace("*", "")
            return gpt_response.split("Whether to Gossip:")[-1].strip()
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
    prompt_template = "prompt/stage_4/stage_4_trustee_gossip.txt"
    prompt_input = create_prompt_input(
        init_persona,
        target_persona,
        trustee_plan,
        investor_resource,
        k,
        actual_distributable,
        trustee_share,
        investor_share,
        reported_resource,
        trustee_allocated,
        investor_allocated,
    )
    prompt = generate_prompt_role_play(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = safe_generate_response(
        prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up
    )

    if verbose:
        print_run_prompts(
            prompt_template, init_persona, gpt_param, prompt_input, prompt, output
        )

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]

def run_gpt_prompt_select_trustee(
    init_persona,
    learned,
    repu_list,
):
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
    
    def create_prompt_input(
        learned,
        init_persona_name,
        repu_list
    ):
        prompt_input = []
        prompt_input.append(learned)
        prompt_input.append(init_persona_name)
        prompt_input.append(repu_list)

        return prompt_input

    def __func_validate(gpt_response, prompt=None):
        return True

    def __func_clean_up(gpt_response, prompt=None):
        return str(gpt_response).strip()
    
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
    prompt_template = "prompt/stage_1/stage_1_investor_select_trustee.txt"
    prompt_input = create_prompt_input(
        learned=learned,
        init_persona_name=init_persona.name,
        repu_list=repu_list,
    )
    prompt = generate_prompt_role_play(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = safe_generate_response(
        prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up
    )

    print_run_prompts(
        prompt_template, init_persona, gpt_param, prompt_input, prompt, output
    )

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]
