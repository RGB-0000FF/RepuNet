from .prompt_template.run_gpt_prompt import (
    run_gpt_prompt_reputation_update_after_stage4_investor_v1,
    run_gpt_prompt_reputation_update_after_stage4_trustee_v1,
    run_gpt_prompt_reputation_update_after_gossip_invest_v1,
    run_gpt_prompt_reputation_update_after_gossip_sign_up_v1,
    run_gpt_prompt_reputation_update_after_gossip_pd_game_v1,
    run_gpt_prompt_update_learned_in_description_sign_v1,
    run_gpt_prompt_update_learned_in_description_invest_v1,
    run_gpt_prompt_self_reputation_init_sign_up_v1,
    run_gpt_prompt_self_reputation_update_after_chat_sign_up_v1,
    run_gpt_prompt_other_reputation_update_after_chat_sign_up_v1,
    run_gpt_prompt_other_reputation_update_after_new_sign_up_v1,
    run_gpt_prompt_reputation_update_after_observed_v1,
    run_gpt_prompt_self_reputation_update_after_pd_game_v1,
    run_gpt_prompt_other_reputation_update_after_pd_game_v1,
    run_gpt_prompt_update_learned_in_description_pd_game_v1,
)
from .social_network import *


def reputation_init_sign_up(init_persona):
    res = run_gpt_prompt_self_reputation_init_sign_up_v1(init_persona)[0]
    if type(res) is str and "error" in res.lower():
        raise Exception("GPT ERROR")
    init_persona.reputationDB.update_individual_reputation(res, init_persona.scratch.curr_step, "sign up repu init")


def reputation_update_pd_game(init_persona, target_persona, update_info):
    if "pd_game" in update_info["reason"]:
        res_s = run_gpt_prompt_self_reputation_update_after_pd_game_v1(init_persona, update_info["init_behavior_summary"])[0]
        if type(res_s) is str and "error" in res_s.lower():
            raise Exception("GPT ERROR")
        res_o = run_gpt_prompt_other_reputation_update_after_pd_game_v1(init_persona, target_persona, update_info["target_behavior_summary"])[0]
        if type(res_o) is str and "error" in res_o.lower():
            raise Exception("GPT ERROR")
        init_persona.reputationDB.update_individual_reputation(res_s, init_persona.scratch.curr_step, update_info["reason"])
        init_persona.reputationDB.update_individual_reputation(res_o, init_persona.scratch.curr_step, update_info["reason"])
        new_learned = run_gpt_prompt_update_learned_in_description_pd_game_v1(init_persona, update_info["init_behavior_summary"])[0]
        if type(new_learned) is str and "error" in new_learned.lower():
            raise Exception("GPT ERROR")
        init_persona.scratch.learned = new_learned
    elif "gossip" in update_info["reason"]:
        res_after_gossip = run_gpt_prompt_reputation_update_after_gossip_pd_game_v1(init_persona, target_persona, update_info["gossip"][0])[0]
        if type(res_after_gossip) is str and "error" in res_after_gossip.lower():
            raise Exception("GPT ERROR")
        init_persona.reputationDB.update_individual_reputation(res_after_gossip, init_persona.scratch.curr_step, update_info["reason"])
        return

    social_network_update(init_persona, target_persona, "player", "player", update_info)


def reputation_update_invest(
    init_persona,
    target_persona,
    update_info,
    full_investment=True,
):
    if "stage 1" in update_info["reason"]:
        reputation_update_after_stage1_invest(init_persona, target_persona, update_info)
    elif "stage 4" in update_info["reason"]:
        reputation_update_after_stage4_invest(init_persona, target_persona, update_info)
    elif "observed" in update_info["reason"]:
        reputation_update_after_observed_invest(init_persona, target_persona, update_info)
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
        reputation_update_after_interaction_sign_up(init_persona, target_persona, update_info)
    elif "sign up" in update_info["reason"]:
        reputation_after_new_sign_up(init_persona, target_persona, update_info)
        # NETWORK AFTER SIGN UP IS IN THE SIGN UP PART
        return
    elif "gossip" in update_info["reason"]:
        reputation_update_after_gossip_sign_up(init_persona, target_persona, update_info)
        # NETWORK AFTER GOSSIP IS IN THE GOSSIP PART
        return

    social_network_update(init_persona, target_persona, "resident", "resident", update_info)


def reputation_update_after_gossip_sign_up(init_persona, target_persona, update_info):
    res = run_gpt_prompt_reputation_update_after_gossip_sign_up_v1()[0]


def reputation_update_after_interaction_sign_up(init_persona, target_persona, update_info):
    # Init persona self reputation update
    res_s = run_gpt_prompt_self_reputation_update_after_chat_sign_up_v1(init_persona, update_info["sum_convo"], update_info["ava_satisfy"])[0]
    res_o = run_gpt_prompt_other_reputation_update_after_chat_sign_up_v1()[0]

    init_persona.reputationDB.update_individual_reputation(res_o, init_persona.scratch.curr_step, update_info["reason"])
    init_persona.reputationDB.update_individual_reputation(res_s, init_persona.scratch.curr_step, update_info["reason"])


def reputation_after_new_sign_up(init_persona, target_persona, update_info):
    res = run_gpt_prompt_other_reputation_update_after_new_sign_up_v1()[0]


def reputation_update_after_gossip_invest(init_persona, target_persona, update_info):
    res = run_gpt_prompt_reputation_update_after_gossip_invest_v1()[0]


def reputation_update_after_observed_invest(init_persona, target_persona, update_info):
    res = run_gpt_prompt_reputation_update_after_observed_v1()[0]


def reputation_update_after_stage4_invest(init_persona, target_persona, update_info):
    if update_info["init_persona_role"] == "investor":
        res = run_gpt_prompt_reputation_update_after_stage4_investor_v1()[0]
    elif update_info["init_persona_role"] == "trustee":
        res = run_gpt_prompt_reputation_update_after_stage4_trustee_v1()[0]


def learned_update_sign(init_persona, init_persona_role, init_persona_view):
    res = run_gpt_prompt_update_learned_in_description_sign_v1(init_persona, init_persona_role, init_persona_view)[0]


def learned_update_invest(init_persona, init_persona_role, init_persona_view):
    res = run_gpt_prompt_update_learned_in_description_invest_v1(init_persona, init_persona_role, init_persona_view)[0]
