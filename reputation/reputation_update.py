from .prompt_template.run_gpt_prompt import (
    run_gpt_prompt_reputation_update_after_stage4_investor_v1,
    run_gpt_prompt_reputation_update_after_stage4_trustee_v1,
    run_gpt_prompt_reputation_update_after_gossip_v1,
    run_gpt_prompt_update_learned_in_description_v1,
    run_gpt_prompt_reputation_update_after_stage1_trustee_v1,
    run_gpt_prompt_reputation_update_after_stage1_investor_v1,
    run_gpt_prompt_self_reputation_init_sign_upv1,
)
from .social_network import *


def reputation_init_sign_up(init_persona):
    res = run_gpt_prompt_self_reputation_init_sign_upv1(init_persona)[0]
    if "error" in res.lower():
        raise Exception("GPT ERROR")
    init_persona.reputationDB.init_individual_reputation(
        res, init_persona.scratch.curr_step, "sign up repu init"
    )


def reputation_update_invest(init_persona, target_persona, update_info):
    if "stage 1" in update_info["reason"]:
        reputation_update_after_stage1_invest(init_persona, target_persona, update_info)
    elif "stage 4" in update_info["reason"]:
        reputation_update_after_stage4_invest(init_persona, target_persona, update_info)
    elif "gossip" in update_info["reason"]:
        reputation_update_after_gossip_invest(init_persona, target_persona, update_info)
        # NETWORK AFTER GOSSIP IS IN THE GOSSIP PART
        return

    if update_info["init_persona_role"] == "investor":
        social_network_update_invest(
            init_persona, target_persona, "investor", "trustee"
        )
    elif update_info["init_persona_role"] == "trustee":
        social_network_update_invest(
            init_persona, target_persona, "trustee", "investor"
        )


def reputation_update_sign_up(init_persona, update_info):
    if "interaction" in update_info["reason"]:
        reputation_update_after_interaction_sign_up(init_persona, update_info)

    social_network_update_sign_up(init_persona, update_info)
 



def reputation_update_after_interaction_sign_up(init_persona, target_persona):
    # TODO: Implement sign up reputation update
    pass


def reputation_update_after_gossip_invest(init_persona, target_persona, update_info):
    res = run_gpt_prompt_reputation_update_after_gossip_v1(
        init_persona,
        target_persona,
        update_info["gossip"][0],
        update_info["target_persona_role"],
        update_info["total_number_of_people"],
        update_info["number_of_bidirectional_connections"],
    )[0]
    if "error" in res.lower():
        raise Exception("GPT ERROR")
    init_persona.reputationDB.update_individual_reputation(
        res, init_persona.scratch.curr_step, update_info["reason"]
    )
    # print(res)


def reputation_update_after_stage4_invest(init_persona, target_persona, update_info):
    if update_info["init_persona_role"] == "investor":
        res = run_gpt_prompt_reputation_update_after_stage4_investor_v1(
            init_persona,
            target_persona,
            "investor",
            "trustee",
            update_info["init_behavior_summary"],
            update_info["target_behavior_summary"],
            update_info["total_number_of_people"],
            update_info["number_of_bidirectional_connections"],
        )[0]
    elif update_info["init_persona_role"] == "trustee":
        res = run_gpt_prompt_reputation_update_after_stage4_trustee_v1(
            init_persona,
            target_persona,
            "trustee",
            "investor",
            update_info["init_behavior_summary"],
            update_info["target_behavior_summary"],
            update_info["total_number_of_people"],
            update_info["number_of_bidirectional_connections"],
        )[0]
    if "error" in res.lower():
        raise Exception("GPT ERROR")
    init_persona.reputationDB.update_individual_reputation(
        res, init_persona.scratch.curr_step, update_info["reason"]
    )
    # learned_update(init_persona, update_info["init_persona_role"])

    # print(res)


def reputation_update_after_stage1_invest(init_persona, target_persona, update_info):
    if update_info["init_persona_role"] == "investor":
        res = run_gpt_prompt_reputation_update_after_stage1_investor_v1(
            init_persona,
            target_persona,
            "investor",
            "trustee",
            update_info["allocation_plan"],
            update_info["reason_refusal"],
            update_info["total_number_of_people"],
            update_info["number_of_bidirectional_connections"],
        )[0]
    elif update_info["init_persona_role"] == "trustee":
        res = run_gpt_prompt_reputation_update_after_stage1_trustee_v1(
            init_persona,
            target_persona,
            "trustee",
            "investor",
            update_info["allocation_plan"],
            update_info["reason_refusal"],
            update_info["total_number_of_people"],
            update_info["number_of_bidirectional_connections"],
        )[0]
    if "error" in res.lower():
        raise Exception("GPT ERROR")
    init_persona.reputationDB.update_individual_reputation(
        res, init_persona.scratch.curr_step, update_info["reason"]
    )
    # learned_update(init_persona, update_info["init_persona_role"])


def learned_update(init_persona, init_persona_role):
    res = run_gpt_prompt_update_learned_in_description_v1(
        init_persona, init_persona_role
    )[0]
    init_persona.scratch.learned = res


def replace_full_name(personas, name):
    for persona in personas.keys():
        if name in personas:
            return persona
    return None
