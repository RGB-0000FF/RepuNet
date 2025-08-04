import sys

from .prompt_template.run_gpt_prompt import (
    run_gpt_prompt_disconnection_after_gossip_v2,
    run_gpt_prompt_disconnection_after_new_sign_up_v1,
    run_gpt_prompt_disconnection_after_observed_v1,
    run_gpt_disconnection_res,
    run_gpt_prompt_bind_res,
)


def social_network_update(
    init_persona,
    target_persona,
    init_persona_role,
    target_persona_role,
    update_info=None,
    full_investment=True,
):
    disconnection_res = run_gpt_disconnection_res(update_info)

    if disconnection_res["Disconnect"].lower() == "yes":
        init_persona.scratch.relationship["bind_list"].remove([target_persona.scratch.name, target_persona_role])
        init_persona.scratch.relationship["black_list"].append([target_persona.scratch.name, target_persona_role])

    bind_res = run_gpt_prompt_bind_res(update_info)

    if bind_res["Connect"].lower() == "yes":
        init_persona.scratch.relationship["bind_list"].append([target_persona.scratch.name, target_persona_role])


def social_network_update_after_new_sign_up(
    init_persona,
    target_persona,
):
    try:
        _ = init_persona.scratch.relationship["bind_list"].index([target_persona.scratch.name, "resident"])
        disconnection_res = run_gpt_prompt_disconnection_after_new_sign_up_v1(
            init_persona,
            target_persona,
            "resident",
        )[0]

        if disconnection_res["Disconnect"].lower() == "yes":
            init_persona.scratch.relationship["bind_list"].remove([target_persona.scratch.name, "resident"])
            init_persona.scratch.relationship["black_list"].append([target_persona.scratch.name, "resident"])
    except Exception as e:
        if isinstance(e, Exception) and str(e) == "GPT ERROR":
            sys.exit(str(e))


def social_network_update_after_observed_invest(
    init_persona,
    target_persona,
    update_info,
):
    try:
        _ = init_persona.scratch.relationship["bind_list"].index([target_persona.scratch.name, "resident"])
        disconnection_res = run_gpt_prompt_disconnection_after_observed_v1(
            init_persona,
            target_persona,
            update_info["init_persona_role"],
            update_info["target_persona_role"],
            update_info["interaction_memory"],
        )[0]

        if type(disconnection_res) is str and "error" in disconnection_res.lower():
            raise Exception("GPT ERROR")

        if disconnection_res["Disconnect"].lower() == "yes":
            init_persona.scratch.relationship["bind_list"].remove([target_persona.scratch.name, "resident"])
            init_persona.scratch.relationship["black_list"].append([target_persona.scratch.name, "resident"])
    except Exception as e:
        if isinstance(e, Exception) and str(e) == "GPT ERROR":
            sys.exit(str(e))


def social_network_update_after_gossip(
    init_persona,
    target_persona,
    init_persona_role,
    target_persona_role,
    gossiper_name,
    gossip_info,
):
    gossip_res = run_gpt_prompt_disconnection_after_gossip_v2(init_persona, target_persona, init_persona_role, target_persona_role, gossiper_name, gossip_info)[0]
    if gossip_res["Disconnect"].lower() == "yes":
        try:
            init_persona.scratch.relationship["bind_list"].remove([target_persona.scratch.name, target_persona_role])
            init_persona.scratch.relationship["black_list"].append([target_persona.scratch.name, target_persona_role])
        except ValueError:
            init_persona.scratch.relationship["black_list"].append([target_persona.scratch.name, target_persona_role])
            pass
