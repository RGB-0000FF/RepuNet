import random
import os
import sys

random.seed(42)
from reputation.reputation_update import (
    reputation_update_sign_up,
)

from reputation.social_network import social_network_update_after_new_sign_up

from .prompt_template.run_gpt_prompt import (
    run_gpt_prompt_sign_up_v3,
    run_gpt_prompt_decide_to_talk_v1,
    run_gpt_prompt_create_chat_v1,
    run_gpt_prompt_summarize_chat_v1,
    run_gpt_prompt_init_sign_up_v1,
)


def get_d_connect(init_persona, G):
    d_connect_list = []
    for edge in G.edges():
        if edge[0] == init_persona.name:
            if G.has_edge(edge[1], init_persona.name):
                d_connect_list.append(edge[1])
    return d_connect_list


def get_ava_satisfy(ps):
    sum_s = 0
    for persona_name, persona in ps.items():
        if persona.scratch.total_chat_num == 0:
            sum_s += 0
        else:
            sum_s += persona.scratch.success_chat_num / persona.scratch.total_chat_num
    return round(sum_s / len(ps), 2)


def get_ava_num_bibd_connections(ps, G):
    sum_s = 0
    for persona_name, persona in ps.items():
        sum_s += len(get_d_connect(persona, G))
    return round(sum_s / len(ps), 2)


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
                "total_number_of_people": len(personas),
                "number_of_bidirectional_connections": len(get_d_connect(target_persona, G["resident"])),
                "ava_num_bibd_connections": get_ava_num_bibd_connections(personas, G["resident"]),
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
        pair[0].scratch.total_chat_num += 1
        pair[1].scratch.total_chat_num += 1
        pair[0].scratch.success_chat_num += 1
        pair[1].scratch.success_chat_num += 1
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

        update_info_0 = {
            "reason": "reputation update after interaction",
            "sum_convo": sum_covno,
            "total_number_of_people": len(ps),
            "number_of_bidirectional_connections": len(get_d_connect(pair[1], G["resident"])),
            "ava_satisfy": get_ava_satisfy(ps),
            "ava_num_bibd_connections": get_ava_num_bibd_connections(ps, G["resident"]),
        }
        update_info_1 = {
            "reason": "reputation update after interaction",
            "sum_convo": sum_covno,
            "total_number_of_people": len(ps),
            "number_of_bidirectional_connections": len(get_d_connect(pair[0], G["resident"])),
            "ava_satisfy": get_ava_satisfy(ps),
            "ava_num_bibd_connections": get_ava_num_bibd_connections(ps, G["resident"]),
        }
        reputation_update_sign_up(pair[0], pair[1], update_info_0)
        reputation_update_sign_up(pair[1], pair[0], update_info_1)
    else:
        pair[0].scratch.total_chat_num += 1
        pair[1].scratch.total_chat_num += 1


def start_sign_up_without_gossip(personas, G, step, save_floder, sign_up_f=False):
    if sign_up_f:
        # sign up ever 5th step
        sign_up(personas, step, save_floder, G)

    # interaction
    pairs = chat_pair(personas)
    for pair in pairs:
        start_chat(pair, G, personas)
