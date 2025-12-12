from prompt_interface import *
from utils import default_gpt_params

text1="You have never been an investor before, so you are not sure about your reputation."
text2="You have never been an trustee before, so you were not sure about your reputation."
#fin
def run_gpt_prompt_investor_decided_v1(
    init_persona, target_persona, allocation_plan, verbose=False
):
    global text1 
    def create_prompt_input(init_persona, target_persona, allocation_plan):
        global text1
        prompt_input = []
        prompt_input += [init_persona.scratch.learned["investor"]]
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
            target_reputation = None
        prompt_input += [init_reputation]
        prompt_input += [target_reputation]
        memory_list=init_persona.get_interaction_memory(role="investor")
        memory=""
        for m in memory_list:
            memory+="Memory in previous investments:" + m + "\n"
        if memory:
            prompt_input.append(memory)
        else:
            prompt_input.append("You haven't had any transaction records recently.")
        prompt_input.append(init_persona.scratch.name)
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
    prompt_input = create_prompt_input(init_persona, target_persona, allocation_plan)
    if not prompt_input[4]:
        prompt_input.pop(3)
        prompt_input.pop(3)
        prompt_template="prompt/stage_1/All_init_stage_1_investor_v1.txt"
        prompt = generate_prompt_role_play(prompt_input, prompt_template)
    else:
        prompt_template="prompt/stage_1/All_stage_1_investor_v1.txt"
        prompt = generate_prompt_role_play(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    gpt_param = default_gpt_params()
    output = safe_generate_response(
        prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up
    ).strip()

    if verbose:
        print_run_prompts(
            prompt_template, init_persona, gpt_param, prompt_input, prompt, output
        )

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]

#fin
def run_gpt_prompt_trustee_plan_v1(init_persona, target_persona, verbose=False):
    global text2

    def create_prompt_input(init_persona, target_persona):
        global text2

        prompt_input = []
        prompt_input += [init_persona.scratch.learned["trustee"]]
        init_reputation = init_persona.reputationDB.get_targets_individual_reputation(
            init_persona.scratch.ID, "trustee"
        )
        target_reputation = (
            init_persona.reputationDB.get_targets_individual_reputation(
                target_persona.scratch.ID, "investor"
            )
        )
        if not init_reputation:
            init_reputation = text2
        if not target_reputation:
            target_reputation = None
        prompt_input += [init_reputation]
        prompt_input += [target_reputation]
        memory_list=init_persona.get_interaction_memory(role="trustee")
        memory=""
        for m in memory_list:
            memory+="Memory in previous investments:" + m + "\n"
        if memory:
            prompt_input.append(memory)
        else:
            prompt_input.append("You haven't had any transaction records recently.")
        prompt_input.append(init_persona.scratch.name)
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
    
    prompt_input = create_prompt_input(init_persona, target_persona)
    
    if not prompt_input[2]:
        prompt_input.pop(1)
        prompt_input.pop(1)
        prompt_template="prompt/stage_1/All_init_stage_1_trustee_v1.txt"
        prompt = generate_prompt_role_play(prompt_input, prompt_template)
    else:
        prompt_template="prompt/stage_1/All_stage_1_trustee_v1.txt"
        prompt = generate_prompt_role_play(prompt_input, prompt_template)
    fail_safe = get_fail_safe()
    gpt_param = default_gpt_params()
    output = safe_generate_response(
        prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up
    ).strip()

    if verbose:
        print_run_prompts(
            prompt_template, init_persona, gpt_param, prompt_input, prompt, output
        )

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]

#fin TODO: Should the prompt change when reputation is disabled?
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
        global text2
        prompt_input = []
        prompt_input += [init_persona.scratch.learned["trustee"]]
        trustee_reputation = (
            init_persona.reputationDB.get_targets_individual_reputation(
                init_persona.scratch.ID, "trustee"
            )
        )
        investor_reputation = (
            init_persona.reputationDB.get_targets_individual_reputation(
                target_persona.scratch.ID, "investor"
            )
        )
        if not trustee_reputation:
            trustee_reputation = text2
        if not investor_reputation:
            investor_reputation = None
        prompt_input += [trustee_reputation]
        prompt_input += [investor_reputation]
        prompt_input += [trustee_plan]
        prompt_input += [investor_resource]
        prompt_input += [k]
        prompt_input += [actual_distributable]
        prompt_input.append(init_persona.scratch.name)
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
        # res["trustee"] = (
        #     gpt_response.split("Trustee receives")[-1]
        #     .split("units")[0]
        #     .replace(",", "")
        #     .strip()
        # )
        # res["investor"] = (
        #     gpt_response.split("investor receives")[-1]
        #     .split("units")[0]
        #     .replace(",", "")
        #     .strip()
        # )
        res["Final Allocation"] = gpt_response.split("Final Allocation:")[-1].split("Reported Investment Outcome:")[0].strip()
        res["reported_investment_outcome"] = gpt_response.split(
            "Reported Investment Outcome:"
        )[-1].strip()
        return res

    def get_fail_safe():
        fs = "Error"
        return fs
    prompt_template_1 = "prompt/stage_3/All-stage_3_trustee_v1.txt"
    prompt_template_2="prompt/stage_3/All-INIT_stage_3_trustee_v1.txt"
    prompt_input = create_prompt_input(
        init_persona,
        target_persona,
        trustee_plan,
        investor_resource,
        k,
        actual_distributable,
    )
    if not prompt_input[2]:
        prompt_input.pop(1)
        prompt_input.pop(1)
        prompt_template=prompt_template_2
    else:
        prompt_template=prompt_template_1
        
    prompt = generate_prompt_role_play(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    gpt_param = default_gpt_params()
    output = safe_generate_response(
        prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up
    )

    if verbose:
        print_run_prompts(
            prompt_template, init_persona, gpt_param, prompt_input, prompt, output
        )

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]

#fin
def run_gpt_prompt_stage4_investor_evaluation_v1(
    init_persona,
    target_persona,
    trustee_plan,
    investor_resource,
    k,
    actual_distributable,
    proposed_plan,
    actual_result,
    reported_resource,
    verbose=False,
):
    def create_prompt_input(
        init_persona,
        target_persona,
        trustee_plan,
        investor_resource,
        k,
        actual_distributable,
        proposed_plan,
        actual_result,
        reported_resource,
    ):
        prompt_input = []
        prompt_input += [init_persona.scratch.learned["investor"]]
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
        prompt_input.append(proposed_plan)
        prompt_input.append(actual_result)
        prompt_input += [reported_resource]
        prompt_input.append(init_persona.scratch.name)
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
        res["self_reputation"] = (
            gpt_response
            .split("Self (Investor) Reputation Reflection:")[-1].split("Trustee Reputation Reflection:")[0]
            .strip()
        )
        res["trustee_reputation"] = (
            gpt_response.split("Trustee Reputation Reflection:")[-1].strip()
        )
        for val in res.values():
            if val == "":
                return False
        return res

    def get_fail_safe():
        fs = "Error"
        return fs
    prompt_template = "prompt/stage_4/All-stage_4_investor_v2.txt"
    prompt_input = create_prompt_input(
        init_persona,
        target_persona,
        trustee_plan,
        investor_resource,
        k,
        actual_distributable,
        proposed_plan,
        actual_result,
        reported_resource,
    )
    prompt = generate_prompt_role_play(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    gpt_param = default_gpt_params()
    output = safe_generate_response(
        prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up
    )

    if verbose:
        print_run_prompts(
            prompt_template, init_persona, gpt_param, prompt_input, prompt, output
        )

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]

#fin
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
    reflection,
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
        reflection
    ):
        prompt_input = []
        prompt_input += [init_persona.scratch.learned["trustee"]]
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
        prompt_input.append(str(init_persona.scratch.name))
        # prompt_input.append(str(reflection))
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
    prompt_template = "prompt/stage_4/All-stage_4_trustee.txt"
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
        reflection=reflection
    )
    prompt = generate_prompt_role_play(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    gpt_param = default_gpt_params()
    output = safe_generate_response(
        prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up
    )

    if verbose:
        print_run_prompts(
            prompt_template, init_persona, gpt_param, prompt_input, prompt, output
        )

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]


#fin
def run_gpt_prompt_select_trustee(
    init_persona,
    learned,
    repu_list,
):
    
    def create_prompt_input(
        learned,
        init_persona_name,
        repu_list
    ):
        prompt_input = []
        prompt_input.append(learned["investor"])
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
    prompt_template = "prompt/stage_0/All_stage_0_investor_select_trustee.txt"
    prompt_input = create_prompt_input(
        learned=learned,
        init_persona_name=init_persona.name,
        repu_list=repu_list,
    )
    prompt = generate_prompt_role_play(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    gpt_param = default_gpt_params()
    output = safe_generate_response(
        prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up
    )

    print_run_prompts(
        prompt_template, init_persona, gpt_param, prompt_input, prompt, output
    )

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]
