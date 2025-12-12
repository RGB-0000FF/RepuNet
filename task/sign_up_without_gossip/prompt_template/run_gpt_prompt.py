from prompt_interface import *
from utils import default_gpt_params


def run_gpt_prompt_init_sign_up_v1(init_persona):
    def create_prompt_input(init_persona):
        prompt_input = []
        prompt_input += [init_persona.scratch.learned]
        prompt_input += [init_persona.scratch.name]

        return prompt_input

    def __func_validate(gpt_response, prompt=""):
        try:
            response = gpt_response.replace("**", "")

            if response.split(".")[0].lower() in ["yes", "no"]:
                return True
            return False
        except:
            return False

    def __func_clean_up(gpt_response, prompt=""):
        return gpt_response.replace("**", "")

    def get_fail_safe():
        fs = "error"
        return fs

    gpt_param = default_gpt_params()
    prompt_template = "prompt/init_sign_up_request_v2.txt"
    prompt_input = create_prompt_input(init_persona)
    prompt = generate_prompt_role_play(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = safe_generate_response(
        prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up
    )

    print_run_prompts(
        prompt_template, init_persona, gpt_param, prompt_input, prompt, output
    )

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]


def run_gpt_prompt_sign_up_v3(init_persona):
    def create_prompt_input(init_persona):
        prompt_input = []
        prompt_input += [init_persona.scratch.learned]
        prompt_input += [init_persona.scratch.name]
        self_repu = init_persona.reputationDB.get_targets_individual_reputation(
            init_persona.scratch.ID, "resident"
        )
        for v in self_repu.values():
            prompt_input += [v["numerical record"]]

        last_choice = init_persona.associativeMemory.get_latest_event()
        if type(last_choice) is dict:
            last_choice = last_choice["description"]
        else:
            last_choice = last_choice.toJSON()["description"]
        last_choice = last_choice.splitlines()
        for line in last_choice:
            if init_persona.name in line:
                # last choice of the persona in memory
                prompt_input += [line]

        return prompt_input

    def __func_validate(gpt_response, prompt=""):
        try:
            response = gpt_response.replace("**", "")

            if response.split(".")[0].lower() in ["yes", "no"]:
                return True
            return False
        except:
            return False

    def __func_clean_up(gpt_response, prompt=""):
        return gpt_response.replace("**", "")

    def get_fail_safe():
        fs = "error"
        return fs

    gpt_param = default_gpt_params()
    prompt_template = "prompt/sign_up_request_v2.txt"
    prompt_input = create_prompt_input(init_persona)
    prompt = generate_prompt_role_play(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = safe_generate_response(
        prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up
    )

    print_run_prompts(
        prompt_template, init_persona, gpt_param, prompt_input, prompt, output
    )

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]


def run_gpt_prompt_decide_to_talk_v1(init_persona, target_persona):
    def create_prompt_input(init_persona, target_persona):
        target_reputation = init_persona.reputationDB.get_targets_individual_reputation(
            target_persona.scratch.ID, "resident"
        )

        prompt_input = []
        prompt_input += [init_persona.scratch.learned]
        prompt_input += [init_persona.scratch.name]
        prompt_input += [target_persona.scratch.name]
        prompt_input += [json.dumps(target_reputation)]

        return prompt_input

    def __func_validate(gpt_response, prompt=""):
        try:
            response = gpt_response.replace("**", "")

            if "step 1" in response.lower() or "step 2" in response.lower():
                return True
            return False
        except:
            return False

    def __func_clean_up(gpt_response, prompt=""):
        return gpt_response.replace("**", "")

    def get_fail_safe():
        fs = "error"
        return fs

    gpt_param = default_gpt_params()
    prompt_template = "prompt/decide_to_talk_v2.txt"
    prompt_input = create_prompt_input(init_persona, target_persona)
    prompt = generate_prompt_role_play(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = safe_generate_response(
        prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up
    )

    print_run_prompts(
        prompt_template, init_persona, gpt_param, prompt_input, prompt, output
    )

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]


def run_gpt_prompt_create_chat_v1(init_persona, target_persona):
    def create_prompt_input(init_persona, target_persona):
        prompt_input = []
        prompt_input += ["You are now a dialogue generation expert."]
        prompt_input += [init_persona.scratch.name]
        prompt_input += [target_persona.scratch.name]
        prompt_input += [init_persona.scratch.learned]
        prompt_input += [target_persona.scratch.learned]
        info = init_persona.associativeMemory.get_latest_event()
        if type(info) is dict:
            latest_sign_up_info = info
        else:
            latest_sign_up_info = info.toJSON()
        latest_sign_up_info = latest_sign_up_info["description"]
        latest_sign_up_info = latest_sign_up_info.splitlines()
        init_p_sign_up_info = ""
        for line in latest_sign_up_info:
            if init_persona.name in line:
                init_p_sign_up_info = line
            elif target_persona.name in line:
                target_p_sign_up_info = line
        prompt_input += [init_p_sign_up_info]
        prompt_input += [target_p_sign_up_info]

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
    prompt_template = "prompt/create_chat_v2.txt"
    prompt_input = create_prompt_input(init_persona, target_persona)
    prompt = generate_prompt_role_play(prompt_input, prompt_template, role_play=False)

    fail_safe = get_fail_safe()
    output = safe_generate_response(
        prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up
    )

    print_run_prompts(
        prompt_template, init_persona, gpt_param, prompt_input, prompt, output
    )

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]


def run_gpt_prompt_summarize_chat_v1(init_persona, target_persona, convo):
    def create_prompt_input(init_persona, target_persona, convo):
        prompt_input = []
        prompt_input += ["You are now an expert for summarizing dialogues."]
        prompt_input += [init_persona.scratch.name]
        prompt_input += [target_persona.scratch.name]
        prompt_input += [convo]

        return prompt_input

    def __func_validate(gpt_response, prompt=None):
        try:
            if "viewpoint:" in gpt_response.lower():
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
    prompt_template = "prompt/summarize_basic_chat_v2.txt"
    prompt_input = create_prompt_input(init_persona, target_persona, convo)
    prompt = generate_prompt_role_play(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = safe_generate_response(
        prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up
    )

    print_run_prompts(
        prompt_template, init_persona, gpt_param, prompt_input, prompt, output
    )

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]