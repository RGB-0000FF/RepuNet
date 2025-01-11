from .gpt_structure import *


def run_gpt_prompt_investor_decided_v1(
    init_persona, target_persona, allocation_plan, verbose=False
):
    def create_prompt_input(init_persona, target_persona, allocation_plan):
        prompt_input = []
        prompt_input += [init_persona.scratch.learned]
        prompt_input += [allocation_plan]
        prompt_input += [init_persona.scratch.resources_unit]
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
        fs = "Refuse"
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
    prompt_template = "prompt/stage_1/stage_1_investor_v1.txt"
    prompt_input = create_prompt_input(init_persona, target_persona, allocation_plan)
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
    def create_prompt_input(init_persona, target_persona):
        prompt_input = []
        prompt_input += [init_persona.scratch.learned]
        _,memory_list=init_persona.get_latest_memory_list()
        memory=""
        for m in memory_list:
            memory+="Memory:" + m+ "\n"
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
    prompt_template = "prompt/stage_1/stage_1_trustee_v1.txt"
    prompt_input = create_prompt_input(init_persona, target_persona)
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


def run_gpt_prompt_investor_evaluation_v1(
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
        res = dict()
        gpt_response = gpt_response.replace("*", "")
        res["gossip"] = gpt_response.split("Whether to Gossip:")[-1].strip()
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
    prompt_template = "prompt/gossip_willing/stage_4_investor.txt"
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


def run_gpt_prompt_trustee_evaluation_v1(
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
            res = dict()
            gpt_response = gpt_response.replace("*", "")
            res["gossip"] = gpt_response.split("Whether to Gossip:")[-1].strip()
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
    prompt_template = "prompt/gossip_willing/stage_4_trustee.txt"
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
