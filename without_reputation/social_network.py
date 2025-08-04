import sys

from .prompt_template.run_gpt_prompt import (
    run_gpt_disconnection_res,
    run_gpt_prompt_bind_res,
    run_gpt_prompt_disconnection_after_gossip_v1,
)


def social_network_update(init_persona, target_persona, init_persona_role, target_persona_role, interaction_memory=None, full_investment=True):
    disconnection_res = run_gpt_disconnection_res(interaction_memory)

    if disconnection_res["Disconnect"].lower() == "yes":
        init_persona.scratch.relationship["bind_list"].remove(target_persona.scratch.name)
        init_persona.scratch.relationship["black_list"].append(target_persona.scratch.name)

    bind_res = run_gpt_prompt_bind_res(interaction_memory)

    if bind_res["Connect"].lower() == "yes":
        init_persona.scratch.relationship["bind_list"].append(target_persona.scratch.name)


def social_network_update_after_gossip(init_persona, target_persona, init_persona_role, target_persona_role, gossiper_name, gossip_info):
    gossip_res = run_gpt_prompt_disconnection_after_gossip_v1(init_persona, target_persona, init_persona_role, target_persona_role, gossiper_name, gossip_info)[0]
    if gossip_res["Disconnect"] == "Yes":
        try:
            init_persona.scratch.relationship["bind_list"].remove(target_persona.scratch.name)
            init_persona.scratch.relationship["black_list"].append(target_persona.scratch.name)
        except ValueError:
            init_persona.scratch.relationship["black_list"].append(target_persona.scratch.name)
            pass
