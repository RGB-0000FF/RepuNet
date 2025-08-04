import random
import os
import sys

random.seed(42)
from reputation.reputation_update import (
    reputation_update_sign_up,
)
from reputation.gossip import first_order_gossip
from reputation.prompt_template.run_gpt_prompt import (
    run_gpt_prompt_gossip_listener_select_v2,
)
from reputation.social_network import social_network_update_after_new_sign_up

from .prompt_template.run_gpt_prompt import (
    run_gpt_prompt_sign_up_v3,
    run_gpt_prompt_decide_to_talk_v1,
    run_gpt_prompt_create_chat_v1,
    run_gpt_prompt_summarize_chat_v1,
    run_gpt_prompt_willingness_to_gossip_v1,
    run_gpt_prompt_init_sign_up_v1,
)


def chat_pair(personas):
    personas_keys = list(personas.keys())
    random.shuffle(personas_keys)

    pairs = []
    for i in range(0, len(personas_keys), 2):
        pairs.append((personas[personas_keys[i]], personas[personas_keys[i + 1]]))
        print(personas_keys[i], personas_keys[i + 1])
    return pairs


def sign_up(personas, step, save_folder, G):
    save_m = ""
    res = f"--------------------Sign up info {step}--------------------\n"
    count = 0
    for persona_name, persona in personas.items():
        count += 1
        if step != 1:
            # output = run_gpt_prompt_sign_up_v1(persona)[0]
            output = run_gpt_prompt_sign_up_v3(persona)[0]
        else:
            output = run_gpt_prompt_init_sign_up_v1(persona)[0]
        if "error" in output.lower():
            raise Exception("GPT ERROR")
        output_res = output.split(".")[0].strip()
        save_m += f"{persona_name}: {output_res}\n"
        res += f"{count}. {persona_name}: {output}\n"
        # TODO: Implement sign up
        # sign up info as EVENT save to memory
    res += "--------------------End of Sign up info--------------------\n\n"

    os.makedirs(save_folder, exist_ok=True)

    with open(f"{save_folder}/sign_up_results_{step}.txt", "a") as f:
        f.write(res)

    for _, persona in personas.items():
        # update sign up info to memory
        persona.associativeMemory.add_event(
            subject=persona.name,
            predicate="sign up",
            obj="All persona",
            description=save_m,
            created_at=step,
        )
        # update reputation after sign up
        repus = persona.reputationDB.get_all_reputations("resident", persona.scratch.ID)
        known_personas = [repu["name"] for _, repu in repus.items()]
        for target_persona_name in known_personas:
            target_persona = personas[target_persona_name]
            update_info = {
                "reason": "reputation update after sign up",
            }
            reputation_update_sign_up(persona, target_persona, update_info)
            social_network_update_after_new_sign_up(persona, target_persona)


def start_chat(pair, G, ps):
    p0_repu = pair[0].reputationDB.get_targets_individual_reputation(pair[1].scratch.ID, "resident")
    p1_repu = pair[1].reputationDB.get_targets_individual_reputation(pair[0].scratch.ID, "resident")
    if p1_repu:
        if [pair[1], "resident"] in pair[0].scratch.relationship["black_list"]:
            p0_willing = "no"
        else:
            p0_res = run_gpt_prompt_decide_to_talk_v1(pair[0], pair[1])[0]
            p0_willing = p0_res.split("step 2:")[-1].strip()
            if "error" in p0_willing.lower():
                raise Exception("GPT ERROR")
    else:
        p0_willing = "yes"

    if p0_repu:
        if [pair[0], "resident"] in pair[1].scratch.relationship["black_list"]:
            p1_willing = "no"
        else:
            p1_res = run_gpt_prompt_decide_to_talk_v1(pair[1], pair[0])[0]
            p1_willing = p1_res.split("step 2:")[-1].strip()
            if "error" in p1_willing.lower():
                raise Exception("GPT ERROR")
    else:
        p1_willing = "yes"

    if "yes" in p0_willing.lower() and "yes" in p1_willing.lower():
        # chat
        convo = run_gpt_prompt_create_chat_v1(pair[0], pair[1])[0]
        sum_covno = run_gpt_prompt_summarize_chat_v1(pair[0], pair[1], convo)[0]
        if "error" in sum_covno.lower() or "error" in convo.lower():
            raise Exception("GPT ERROR")

        pair[0].associativeMemory.add_chat(
            subject=pair[0].name,
            predicate="basic chat",
            obj=pair[1].name,
            description=sum_covno,
            created_at=pair[0].scratch.curr_step,
            conversation=convo,
        )
        pair[1].associativeMemory.add_chat(
            subject=pair[0].name,
            predicate="basic chat",
            obj=pair[1].name,
            description=sum_covno,
            conversation=convo,
            created_at=pair[0].scratch.curr_step,
        )

        # Chat satisfaction & Gossip willingness
        p0_gossip = run_gpt_prompt_willingness_to_gossip_v1(pair[0], pair[1], sum_covno)[0]
        p1_gossip = run_gpt_prompt_willingness_to_gossip_v1(pair[1], pair[0], sum_covno)[0]
        if "error" in p0_gossip.lower() or "error" in p1_gossip.lower():
            raise Exception("GPT ERROR")
        if "yes" in p0_gossip.split(",")[0].lower():
            pair[0].scratch.complain_buffer.append(
                {
                    "complaint_target_ID": pair[1].scratch.ID,
                    "complaint_target": pair[1].name,
                    "complaint_target_role": "resident",
                    "complaint_reason": p0_gossip.split(",")[-1].strip(),
                }
            )
        if "yes" in p1_gossip.split(",")[0].lower():
            pair[1].scratch.complain_buffer.append(
                {
                    "complaint_target_ID": pair[0].scratch.ID,
                    "complaint_target": pair[0].name,
                    "complaint_target_role": "resident",
                    "complaint_reason": p1_gossip.split(",")[-1].strip(),
                }
            )

        update_info_0 = {
            "reason": "reputation update after interaction",
        }
        update_info_1 = {
            "reason": "reputation update after interaction",
        }
        reputation_update_sign_up(pair[0], pair[1], update_info_0)
        reputation_update_sign_up(pair[1], pair[0], update_info_1)
    else:
        pair[0].scratch.total_chat_num += 1
        pair[1].scratch.total_chat_num += 1


def start_sign_up(personas, G, step, save_floder, sign_up_f=False):
    if sign_up_f:
        # sign up ever 5th step
        sign_up(personas, step, save_floder, G)

    # interaction
    pairs = chat_pair(personas)
    for pair in pairs:
        start_chat(pair, G, personas)

        if pair[0].scratch.complain_buffer:
            # gossip
            # gossip target choose
            for person in pair[0].scratch.complain_buffer:
                # gossip target choose
                gossip_targets = run_gpt_prompt_gossip_listener_select_v2(pair[0], "resident", personas[person["complaint_target"]])[0]
                for gossip_target in gossip_targets:
                    # gossip chat
                    gossip_target_persona = personas[gossip_target]
                    first_order_gossip(
                        pair[0],
                        gossip_target_persona,
                        "resident",
                        "resident",
                        personas,
                        G,
                        val=person,
                    )
        if pair[1].scratch.complain_buffer:
            # gossip
            # gossip target choose
            for person in pair[1].scratch.complain_buffer:
                # gossip target choose
                gossip_targets = run_gpt_prompt_gossip_listener_select_v2(pair[1], "resident", personas[person["complaint_target"]])[0]
                for gossip_target in gossip_targets:
                    # gossip chat
                    gossip_target_persona = personas[gossip_target]
                    first_order_gossip(
                        pair[1],
                        gossip_target_persona,
                        "resident",
                        "resident",
                        personas,
                        G,
                        val=person,
                    )
