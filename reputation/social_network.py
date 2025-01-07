from .prompt_template.run_gpt_prompt import (
    run_gpt_prompt_connection_build_investor_v1,
    run_gpt_prompt_connection_build_trustee_v1,
    run_gpt_prompt_disconnection_investor_v1,
    run_gpt_prompt_disconnection_trustee_v1,
    run_gpt_prompt_disconnection_after_gossip_v1,
    run_gpt_prompt_connection_build_after_chat_sign_up_v1,
    run_gpt_prompt_disconnection_after_chat_sign_up_v1,
)


def social_network_update_sign_up(init_persona, target_persona):
    bind_res = run_gpt_prompt_connection_build_after_chat_sign_up_v1(
        init_persona, target_persona, "resident"
    )[0]

    disconnection_res = run_gpt_prompt_disconnection_after_chat_sign_up_v1(
        init_persona, target_persona, "resident"
    )[0]

    if bind_res["Connect"].lower() == "yes":
        try:
            init_persona.scratch.relationship["bind_list"].remove(
                (target_persona.scratch.name, "resident")
            )
        except:
            init_persona.scratch.relationship["bind_list"].append(
                (target_persona.scratch.name, "resident")
            )

    if disconnection_res["Disconnect"].lower() == "yes":
        if (
            target_persona.scratch.name,
            "resident",
        ) in init_persona.scratch.relationship["bind_list"]:
            init_persona.scratch.relationship["bind_list"].remove(
                (target_persona.scratch.name, "resident")
            )
        init_persona.scratch.relationship["black_list"].append(
            [target_persona.scratch.name, "resident"]
        )


def social_network_update_invest(
    init_persona, target_persona, init_persona_role, target_persona_role
):
    if init_persona_role == "investor":
        # bind the target persona to the init persona
        bind_res = run_gpt_prompt_connection_build_investor_v1(
            init_persona, target_persona, target_persona_role
        )[0]

        # disconnection the target persona from the init persona
        disconnection_res = run_gpt_prompt_disconnection_investor_v1(
            init_persona, target_persona, target_persona_role
        )[0]

    elif init_persona_role == "trustee":
        # bind the target persona to the init persona
        bind_res = run_gpt_prompt_connection_build_trustee_v1(
            init_persona, target_persona, target_persona_role
        )[0]

        # disconnection the target persona from the init persona
        disconnection_res = run_gpt_prompt_disconnection_trustee_v1(
            init_persona, target_persona, target_persona_role
        )[0]

    if bind_res["Connect"].lower() == "yes":
        try:
            init_persona.scratch.relationship["bind_list"].remove(
                (target_persona.scratch.name, target_persona_role)
            )
        except:
            init_persona.scratch.relationship["bind_list"].append(
                (target_persona.scratch.name, target_persona_role)
            )

    if disconnection_res["Disconnect"].lower() == "yes":
        if (
            target_persona.scratch.name,
            target_persona_role,
        ) in init_persona.scratch.relationship["bind_list"]:
            init_persona.scratch.relationship["bind_list"].remove(
                (target_persona.scratch.name, target_persona_role)
            )
        init_persona.scratch.relationship["black_list"].append(
            [target_persona.scratch.name, target_persona_role]
        )


def social_network_update_after_gossip(
    init_persona, target_persona, target_persona_role, gossiper_name
):
    gossip_res = run_gpt_prompt_disconnection_after_gossip_v1(
        init_persona, target_persona, target_persona_role, gossiper_name
    )[0]
    if gossip_res["Disconnect"].lower() == "yes":
        if (
            target_persona.scratch.name
            in init_persona.scratch.relationship["bind_list"]
        ):
            init_persona.scratch.relationship["bind_list"].remove(
                (target_persona.scratch.name, target_persona_role)
            )
        init_persona.scratch.relationship["black_list"].append(
            [target_persona.scratch.name, target_persona_role]
        )
