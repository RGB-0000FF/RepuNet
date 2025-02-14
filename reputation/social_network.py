import sys

from .prompt_template.run_gpt_prompt import (
    run_gpt_prompt_connection_build_investor_v1,
    run_gpt_prompt_connection_build_trustee_v1,
    run_gpt_prompt_disconnection_investor_v1,
    run_gpt_prompt_disconnection_trustee_v1,
    run_gpt_prompt_disconnection_after_gossip_v2,
    run_gpt_prompt_connection_build_after_chat_sign_up_v2,
    run_gpt_prompt_disconnection_after_chat_sign_up_v2,
    run_gpt_prompt_disconnection_after_new_sign_up_v1,
    run_gpt_prompt_disconnection_after_observed_v1,
)


def social_network_update(
    init_persona,
    target_persona,
    init_persona_role,
    target_persona_role,
    update_info=None,
    full_investment=True,
):
    try:
        _ = init_persona.scratch.relationship["bind_list"].index(
            [target_persona.scratch.name, target_persona_role]
        )
        if init_persona_role == "investor":
            disconnection_res = run_gpt_prompt_disconnection_investor_v1(
                init_persona,
                target_persona,
                target_persona_role,
                interaction_memory=update_info["target_behavior_summary"],
            )[0]
        elif init_persona_role == "trustee":
            disconnection_res = run_gpt_prompt_disconnection_trustee_v1(
                init_persona,
                target_persona,
                target_persona_role,
                interaction_memory=update_info["target_behavior_summary"],
            )[0]
        elif init_persona_role == "resident":
            disconnection_res = run_gpt_prompt_disconnection_after_chat_sign_up_v2(
                init_persona,
                target_persona,
                target_persona_role,
                update_info["sum_convo"],
            )[0]
        else:
            disconnection_res = "error"

        if type(disconnection_res) is str and "error" in disconnection_res.lower():
            raise Exception("GPT ERROR")

        if disconnection_res["Disconnect"].lower() == "yes":
            init_persona.scratch.relationship["bind_list"].remove(
                [target_persona.scratch.name, target_persona_role]
            )
            init_persona.scratch.relationship["black_list"].append(
                [target_persona.scratch.name, target_persona_role]
            )

    except Exception as e:
        if not full_investment:
            pass
        else:
            if isinstance(e, Exception) and str(e) == "GPT ERROR":
                sys.exit(str(e))

            if init_persona_role == "investor":
                bind_res = run_gpt_prompt_connection_build_investor_v1(
                    init_persona,
                    target_persona,
                    target_persona_role,
                    update_info["target_behavior_summary"],
                )[0]
            elif init_persona_role == "trustee":
                bind_res = run_gpt_prompt_connection_build_trustee_v1(
                    init_persona,
                    target_persona,
                    target_persona_role,
                    update_info["target_behavior_summary"],
                )[0]
            elif init_persona_role == "resident":
                bind_res = run_gpt_prompt_connection_build_after_chat_sign_up_v2(
                    init_persona,
                    target_persona,
                    target_persona_role,
                    update_info["sum_convo"],
                )[0]
            else:
                bind_res = "error"

            if type(bind_res) is str and "error" in bind_res.lower():
                sys.exit("GPT ERROR")

            if bind_res["Connect"].lower() == "yes":
                init_persona.scratch.relationship["bind_list"].append(
                    [target_persona.scratch.name, target_persona_role]
                )


def social_network_update_after_new_sign_up(
    init_persona,
    target_persona,
):
    try:
        _ = init_persona.scratch.relationship["bind_list"].index(
            [target_persona.scratch.name, "resident"]
        )
        disconnection_res = run_gpt_prompt_disconnection_after_new_sign_up_v1(
            init_persona,
            target_persona,
            "resident",
        )[0]

        if type(disconnection_res) is str and "error" in disconnection_res.lower():
            raise Exception("GPT ERROR")

        if disconnection_res["Disconnect"].lower() == "yes":
            init_persona.scratch.relationship["bind_list"].remove(
                [target_persona.scratch.name, "resident"]
            )
            init_persona.scratch.relationship["black_list"].append(
                [target_persona.scratch.name, "resident"]
            )
    except Exception as e:
        if isinstance(e, Exception) and str(e) == "GPT ERROR":
            sys.exit(str(e))


def social_network_update_after_observed_invest(
    init_persona,
    target_persona,
    update_info,
):
    try:
        _ = init_persona.scratch.relationship["bind_list"].index(
            [target_persona.scratch.name, "resident"]
        )
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
            init_persona.scratch.relationship["bind_list"].remove(
                [target_persona.scratch.name, "resident"]
            )
            init_persona.scratch.relationship["black_list"].append(
                [target_persona.scratch.name, "resident"]
            )
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
    gossip_res = run_gpt_prompt_disconnection_after_gossip_v2(
        init_persona, target_persona, init_persona_role,target_persona_role, gossiper_name, gossip_info
    )[0]
    if gossip_res["Disconnect"].lower() == "yes":
        try:
            init_persona.scratch.relationship["bind_list"].remove(
                [target_persona.scratch.name, target_persona_role]
            )
            init_persona.scratch.relationship["black_list"].append(
                [target_persona.scratch.name, target_persona_role]
            )
        except ValueError:
            init_persona.scratch.relationship["black_list"].append(
                [target_persona.scratch.name, target_persona_role]
            )
            pass
