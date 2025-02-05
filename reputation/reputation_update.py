from .prompt_template.run_gpt_prompt import (
    run_gpt_prompt_reputation_update_after_stage4_investor_v1,
    run_gpt_prompt_reputation_update_after_stage4_trustee_v1,
    run_gpt_prompt_reputation_update_after_gossip_invest_v1,
    run_gpt_prompt_reputation_update_after_gossip_sign_up_v1,
    run_gpt_prompt_update_learned_in_description_sign_v1,
    run_gpt_prompt_update_learned_in_description_v2,
    run_gpt_prompt_update_learned_in_description_invest_v1,
    run_gpt_prompt_reputation_update_after_stage1_trustee_v1,
    run_gpt_prompt_reputation_update_after_stage1_investor_v1,
    run_gpt_prompt_self_reputation_init_sign_up_v1,
    run_gpt_prompt_self_reputation_update_after_chat_sign_up_v1,
    run_gpt_prompt_other_reputation_update_after_chat_sign_up_v1,
    run_gpt_prompt_other_reputation_update_after_new_sign_up_v1,
    run_gpt_prompt_reputation_update_after_observed_v1,
)
from .social_network import *


def reputation_init_sign_up(init_persona):
    res = run_gpt_prompt_self_reputation_init_sign_up_v1(init_persona)[0]
    if type(res) is str and "error" in res.lower():
        raise Exception("GPT ERROR")
    init_persona.reputationDB.update_individual_reputation(
        res, init_persona.scratch.curr_step, "sign up repu init"
    )


def reputation_update_invest(
    init_persona, target_persona, update_info,full_investment=True, 
):
    if "stage 1" in update_info["reason"]:
        reputation_update_after_stage1_invest(init_persona, target_persona, update_info)
    elif "stage 4" in update_info["reason"]:
        reputation_update_after_stage4_invest(init_persona, target_persona, update_info)
    elif "observed" in update_info["reason"]:
        reputation_update_after_observed_invest(
            init_persona, target_persona, update_info
        )
        # NETWORK AFTER OBSERVED IS IN THE OBSERVED PART
        return
    elif "gossip" in update_info["reason"]:
        reputation_update_after_gossip_invest(init_persona, target_persona, update_info)
        # NETWORK AFTER GOSSIP IS IN THE GOSSIP PART
        return

    if update_info["init_persona_role"] == "investor":
        social_network_update(
            init_persona,
            target_persona,
            "investor",
            "trustee",
            update_info=update_info,
            full_investment=full_investment,
        )
    elif update_info["init_persona_role"] == "trustee":
        social_network_update(
            init_persona,
            target_persona,
            "trustee",
            "investor",
            update_info=update_info,
            full_investment=full_investment,
        )


def reputation_update_sign_up(init_persona, target_persona, update_info):
    if "interaction" in update_info["reason"]:
        reputation_update_after_interaction_sign_up(
            init_persona, target_persona, update_info
        )
    elif "sign up" in update_info["reason"]:
        reputation_after_new_sign_up(init_persona, target_persona, update_info)
        # NETWORK AFTER SIGN UP IS IN THE SIGN UP PART
        return
    elif "gossip" in update_info["reason"]:
        reputation_update_after_gossip_sign_up(
            init_persona, target_persona, update_info
        )
        # NETWORK AFTER GOSSIP IS IN THE GOSSIP PART
        return

    social_network_update(
        init_persona, target_persona, "resident", "resident", update_info
    )


def reputation_update_after_gossip_sign_up(init_persona, target_persona, update_info):
    res = run_gpt_prompt_reputation_update_after_gossip_sign_up_v1(
        init_persona,
        target_persona,
        update_info["gossip"][0],
        update_info["target_persona_role"],
        update_info["total_number_of_people"],
        update_info["number_of_bidirectional_connections"],
    )[0]
    if type(res) is str and "error" in res.lower():
        raise Exception("GPT ERROR")
    init_persona.reputationDB.update_individual_reputation(
        res, init_persona.scratch.curr_step, update_info["reason"]
    )
    # print(res)


def reputation_update_after_interaction_sign_up(
    init_persona, target_persona, update_info
):
    # Init persona self reputation update
    res_s = run_gpt_prompt_self_reputation_update_after_chat_sign_up_v1(
        init_persona, update_info["sum_convo"], update_info["ava_satisfy"]
    )[0]
    res_o = run_gpt_prompt_other_reputation_update_after_chat_sign_up_v1(
        init_persona,
        target_persona,
        update_info["sum_convo"],
        update_info["total_number_of_people"],
        update_info["number_of_bidirectional_connections"],
        update_info["ava_num_bibd_connections"],
    )[0]
    if type(res_s) is str and "error" in res_s.lower():
        raise Exception("GPT ERROR")
    if type(res_o) is str and "error" in res_o.lower():
        raise Exception("GPT ERROR")

    init_persona.reputationDB.update_individual_reputation(
        res_o, init_persona.scratch.curr_step, update_info["reason"]
    )
    init_persona.reputationDB.update_individual_reputation(
        res_s, init_persona.scratch.curr_step, update_info["reason"]
    )

    sum_covno_s = update_info["sum_convo"].strip().split("- ")
    self_view = ""
    for s in sum_covno_s:
        if f"{init_persona.name}'s Viewpoint" in s:
            self_view = s.split(":")[-1].strip()

    learned_update_sign(init_persona, "resident", self_view)


def reputation_after_new_sign_up(init_persona, target_persona, update_info):
    res = run_gpt_prompt_other_reputation_update_after_new_sign_up_v1(
        init_persona,
        target_persona,
        update_info["total_number_of_people"],
        update_info["number_of_bidirectional_connections"],
        update_info["ava_num_bibd_connections"],
    )[0]
    if type(res) is str and "error" in res.lower():
        raise Exception("GPT ERROR")
    init_persona.reputationDB.update_individual_reputation(
        res, init_persona.scratch.curr_step, update_info["reason"]
    )


def reputation_update_after_gossip_invest(init_persona, target_persona, update_info):
    res = run_gpt_prompt_reputation_update_after_gossip_invest_v1(
        init_persona,
        target_persona,
        update_info["gossip"][0],
        update_info["init_persona_role"],
        update_info["target_persona_role"],
        update_info["gossip"][0]["credibility level"],
    )[0]
    if type(res) is str and "error" in res.lower():
        raise Exception("GPT ERROR")
    init_persona.reputationDB.update_individual_reputation(
        res, init_persona.scratch.curr_step, update_info["reason"]
    )
    # print(res)


def reputation_update_after_observed_invest(init_persona, target_persona, update_info):
    res = run_gpt_prompt_reputation_update_after_observed_v1(
        init_persona,
        target_persona,
        update_info["init_persona_role"],
        update_info["target_persona_role"],
        update_info["interaction_memory"],
    )[0]
    if type(res) is str and "error" in res.lower():
        raise Exception("GPT ERROR")
    init_persona.reputationDB.update_individual_reputation(
        res, init_persona.scratch.curr_step, update_info["reason"]
    )


def reputation_update_after_stage4_invest(init_persona, target_persona, update_info):
    if update_info["init_persona_role"] == "investor":
        res = run_gpt_prompt_reputation_update_after_stage4_investor_v1(
            init_persona,
            target_persona,
            update_info,
        )[0]
    elif update_info["init_persona_role"] == "trustee":
        res = run_gpt_prompt_reputation_update_after_stage4_trustee_v1(
            init_persona,
            target_persona,
            update_info,
        )[0]
    if type(res) is str and "error" in res.lower():
        raise Exception("GPT ERROR")
    init_persona.reputationDB.update_individual_reputation(
        res, init_persona.scratch.curr_step, update_info["reason"]
    )
    learned_update_invest(
        init_persona,
        update_info["init_persona_role"],
        update_info["init_behavior_summary"],
    )

    # print(res)


def reputation_update_after_stage1_invest(init_persona, target_persona, update_info):
    """
    NOT USED NOW
    """
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
    if type(res) is str and "error" in res.lower():
        raise Exception("GPT ERROR")
    init_persona.reputationDB.update_individual_reputation(
        res, init_persona.scratch.curr_step, update_info["reason"]
    )
    learned_update_invest(
        init_persona,
        update_info["init_persona_role"],
        update_info["init_behavior_summary"],
    )


def learned_update_sign(init_persona, init_persona_role, init_persona_view):
    res = run_gpt_prompt_update_learned_in_description_sign_v1(
        init_persona, init_persona_role, init_persona_view
    )[0]
    if "error" in res.lower():
        raise Exception("GPT ERROR")
    init_persona.scratch.learned = res


def learned_update_invest(init_persona, init_persona_role, init_persona_view):
    res = run_gpt_prompt_update_learned_in_description_invest_v1(
        init_persona, init_persona_role, init_persona_view
    )[0]
    if "error" in res.lower() and len(res) < 10:
        raise Exception("GPT ERROR")
    init_persona.scratch.learned[init_persona_role] = res


def replace_full_name(personas, name):
    for persona in personas.keys():
        if name in personas:
            return persona
    return None
