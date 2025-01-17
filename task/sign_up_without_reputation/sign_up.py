import random
import os

from without_reputation.gossip import first_order_gossip
from without_reputation.prompt_template.run_gpt_prompt import (
    run_gpt_prompt_update_learned_in_description_v1,
    run_gpt_prompt_gossip_listener_select_v1,
)
from without_reputation.social_network import social_network_update

from .prompt_template.run_gpt_prompt import (
    run_gpt_prompt_sign_up_v1,
    run_gpt_prompt_decide_to_talk_v1,
    run_gpt_prompt_create_chat_v1,
    run_gpt_prompt_summarize_chat_v1,
    run_gpt_prompt_willingness_to_gossip_v1,
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


def sign_up(personas, step, save_folder):
    save_m = ""
    res = f"--------------------Sign up info {step}--------------------\n"
    count = 0
    for persona_name, persona in personas.items():
        count += 1
        if step != 1:
            output = run_gpt_prompt_sign_up_v1(persona)[0]
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
        persona.associativeMemory.add_event(
            subject=persona.name,
            predicate="sign up",
            obj="All persona",
            description=save_m,
            created_at=step,
        )


def start_chat(pair, G, ps):
    if pair[1].name in pair[0].scratch.relationship["black_list"]:
        p0_willing = "no"
    else:
        p0_res = run_gpt_prompt_decide_to_talk_v1(pair[0], pair[1])[0]
        p0_willing = p0_res.split("step 2:")[-1].strip()
        if "error" in p0_willing.lower():
            raise Exception("GPT ERROR")

    if pair[0].name in pair[1].scratch.relationship["black_list"]:
        p1_willing = "no"
    else:
        p1_res = run_gpt_prompt_decide_to_talk_v1(pair[1], pair[0])[0]
        p1_willing = p1_res.split("step 2:")[-1].strip()
        if "error" in p1_willing.lower():
            raise Exception("GPT ERROR")

    if "yes" in p0_willing.lower() and "yes" in p1_willing.lower():
        pair[0].scratch.total_chat_num += 1
        pair[1].scratch.total_chat_num += 1
        pair[0].scratch.success_chat_num += 1
        pair[1].scratch.success_chat_num += 1
        p0_name = pair[0].name
        p1_name = pair[1].name
        # chat
        convo = run_gpt_prompt_create_chat_v1(pair[0], pair[1])[0]
        sum_covno = run_gpt_prompt_summarize_chat_v1(pair[0], pair[1], convo)[0]
        if "error" in sum_covno.lower() or "error" in convo.lower():
            raise Exception("GPT ERROR")

        sum_covno_s = sum_covno.strip().split("- ")
        p0_view = ""
        p1_view = ""
        for s in sum_covno_s:
            if f"{p0_name}'s Viewpoint" in s:
                p0_view = s.split(":")[-1].strip()
            elif f"{p1_name}'s Viewpoint" in s:
                p1_view = s.split(":")[-1].strip()

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
        p0_gossip = run_gpt_prompt_willingness_to_gossip_v1(
            pair[0], pair[1], sum_covno
        )[0]
        p1_gossip = run_gpt_prompt_willingness_to_gossip_v1(
            pair[1], pair[0], sum_covno
        )[0]
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

        p0_learned = run_gpt_prompt_update_learned_in_description_v1(pair[0], "resident", p0_view)[0]
        p1_learned = run_gpt_prompt_update_learned_in_description_v1(pair[1], "resident", p1_view)[0]

        if "error" in p0_learned.lower() or "error" in p1_learned.lower():
            raise Exception("GPT ERROR")
        
        pair[0].scratch.learned = p0_learned
        pair[1].scratch.learned = p1_learned

        social_network_update(pair[0], pair[1], "resident", "resident", sum_covno)
        social_network_update(pair[1], pair[0], "resident", "resident", sum_covno)

    else:
        pair[0].scratch.total_chat_num += 1
        pair[1].scratch.total_chat_num += 1


def start_sign_up_without_reputation(personas, G, step, save_floder, sign_up_f=False):
    if sign_up_f:
        # sign up ever 5th step
        sign_up(personas, step, save_floder)

    # interaction
    pairs = chat_pair(personas)
    for pair in pairs:
        start_chat(pair, G, personas)

        if pair[0].scratch.complain_buffer:
            # gossip
            # gossip target choose
            gossip_target_investor = run_gpt_prompt_gossip_listener_select_v1(
                pair[0], "resident", pair[1]
            )[0]
            for gossip_target in gossip_target_investor:
                # gossip chat
                gossip_target_persona = personas[gossip_target]
                first_order_gossip(
                    pair[0],
                    gossip_target_persona,
                    "resident",
                    "resident",
                    personas,
                    G,
                )
        if pair[1].scratch.complain_buffer:
            # gossip
            # gossip target choose
            gossip_target_investor = run_gpt_prompt_gossip_listener_select_v1(
                pair[1], "resident", pair[0]
            )[0]
            for gossip_target in gossip_target_investor:
                # gossip chat
                gossip_target_persona = personas[gossip_target]
                first_order_gossip(
                    pair[1],
                    gossip_target_persona,
                    "resident",
                    "resident",
                    personas,
                    G,
                )
