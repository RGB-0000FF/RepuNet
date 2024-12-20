from .prompt_template.run_gpt_prompt import (
    run_gpt_prompt_connection_build_after_stage4_investor_v1,
    run_gpt_prompt_connection_build_after_stage4_trustee_v1,
    run_gpt_prompt_disconnection_after_stage4_investor_v1,
    run_gpt_prompt_disconnection_after_stage4_trustee_v1,
    run_gpt_prompt_disconnection_after_gossip_v1,
)


def social_network_update_after_stage4(
    init_persona, target_persona, init_persona_role, target_persona_role
):
    if init_persona_role == "investor":
        # bind the target persona to the init persona
        bind_res = run_gpt_prompt_connection_build_after_stage4_investor_v1(
            init_persona, target_persona, target_persona_role
        )[0]
        if bind_res["Connect"] == "Yes":
            init_persona.scratch.relationship["bind_list"].append(
                target_persona.scratch.name
            )

        # disconnection the target persona from the init persona
        disconnection_res = run_gpt_prompt_disconnection_after_stage4_investor_v1(
            init_persona, target_persona, target_persona_role
        )[0]
        if disconnection_res["Disconnect"] == "Yes":
            if target_persona.scratch.name in init_persona.scratch.relationship[
                "bind_list"
            ]:
                init_persona.scratch.relationship["bind_list"].remove(
                    target_persona.scratch.name
                )
            init_persona.scratch.relationship["black_list"].append(
                target_persona.scratch.name
            )
    elif init_persona_role == "trustee":
        # bind the target persona to the init persona
        bind_res = run_gpt_prompt_connection_build_after_stage4_trustee_v1(
            init_persona, target_persona, target_persona_role
        )[0]
        if bind_res["Connect"] == "Yes":
            init_persona.scratch.relationship["bind_list"].append(
                target_persona.scratch.name
            )
        # disconnection the target persona from the init persona
        disconnection_res = run_gpt_prompt_disconnection_after_stage4_trustee_v1(
            init_persona, target_persona, target_persona_role
        )[0]
        if disconnection_res["Disconnect"] == "Yes":
            if target_persona.scratch.name in init_persona.scratch.relationship[
                "bind_list"
            ]:
                init_persona.scratch.relationship["bind_list"].remove(
                    target_persona.scratch.name
                )
            init_persona.scratch.relationship["black_list"].append(
                target_persona.scratch.name
            )


def social_network_update_after_gossip(
    init_persona, target_persona, target_persona_role, gossiper_name
):
    gossip_res = run_gpt_prompt_disconnection_after_gossip_v1(
        init_persona, target_persona, target_persona_role, gossiper_name
    )[0]
    if gossip_res["Disconnect"] == "Yes":
        if target_persona.scratch.name in init_persona.scratch.relationship[
            "bind_list"
        ]:
            init_persona.scratch.relationship["bind_list"].remove(
                target_persona.scratch.name
            )
        init_persona.scratch.relationship["black_list"].append(
            target_persona.scratch.name
        )
