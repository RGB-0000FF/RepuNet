import sys

from .prompt_template.run_gpt_prompt import (
    run_gpt_prompt_connection_build_investor_v1,
    run_gpt_prompt_connection_build_trustee_v1,
    run_gpt_prompt_connection_build_after_chat_sign_up_v1,
    run_gpt_prompt_disconnection_investor_v1,
    run_gpt_prompt_disconnection_trustee_v1,
    run_gpt_prompt_disconnection_after_chat_sign_up_v1,
    run_gpt_prompt_disconnection_after_gossip_v1,
)


def social_network_update(
    init_persona,
    target_persona,
    init_persona_role,
    target_persona_role,
    interaction_memory=None,
    full_investment=True
):
    try:
        _ = init_persona.scratch.relationship["bind_list"].index(
            target_persona.scratch.name
        )

        if init_persona_role == "investor":
            disconnection_res = run_gpt_prompt_disconnection_investor_v1(
                init_persona, target_persona, interaction_memory
            )[0]
        elif init_persona_role == "trustee":
            disconnection_res = run_gpt_prompt_disconnection_trustee_v1(
                init_persona, target_persona, interaction_memory
            )[0]
        elif init_persona_role == "resident":
            disconnection_res = run_gpt_prompt_disconnection_after_chat_sign_up_v1(
                init_persona, target_persona, target_persona_role, interaction_memory
            )[0]
        else:
            disconnection_res = "error"

        if type(disconnection_res) is str and "error" in disconnection_res.lower():
            raise Exception("GPT ERROR")

        if disconnection_res["Disconnect"].lower() == "yes":
            init_persona.scratch.relationship["bind_list"].remove(
                target_persona.scratch.name
            )
            init_persona.scratch.relationship["black_list"].append(
                target_persona.scratch.name
            )

    except Exception as e:
        if not full_investment:
            pass
        else:
            if isinstance(e, Exception) and str(e) == "GPT ERROR":
                sys.exit(str(e))

            if init_persona_role == "investor":
                bind_res = run_gpt_prompt_connection_build_investor_v1(
                    init_persona, target_persona, interaction_memory
                )[0]
            elif init_persona_role == "trustee":
                bind_res = run_gpt_prompt_connection_build_trustee_v1(
                    init_persona, target_persona, interaction_memory
                )[0]
            elif init_persona_role == "resident":
                bind_res = run_gpt_prompt_connection_build_after_chat_sign_up_v1(
                    init_persona, target_persona, target_persona_role, interaction_memory
                )[0]
            else:
                bind_res = "error"

            if type(bind_res) is str and "error" in bind_res.lower():
                sys.exit("GPT ERROR")

            if bind_res["Connect"].lower() == "yes":
                init_persona.scratch.relationship["bind_list"].append(
                    target_persona.scratch.name
                )


def social_network_update_after_gossip(
    init_persona, target_persona, target_persona_role, gossiper_name, gossip_info
):
    gossip_res = run_gpt_prompt_disconnection_after_gossip_v1(
        init_persona, target_persona, target_persona_role, gossiper_name, gossip_info
    )[0]
    if gossip_res["Disconnect"] == "Yes":
        try:
            init_persona.scratch.relationship["bind_list"].remove(
                target_persona.scratch.name
            )
            init_persona.scratch.relationship["black_list"].append(
                target_persona.scratch.name
            )
        except ValueError:
            init_persona.scratch.relationship["black_list"].append(
                target_persona.scratch.name
            )
