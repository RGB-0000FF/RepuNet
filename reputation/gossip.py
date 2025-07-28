from .prompt_template.run_gpt_prompt import (
    # run_gpt_prompt_gossip_v1,
    run_gpt_prompt_gossip_v2,
    run_gpt_prompt_gossip_listener_select_v2,
    run_gpt_prompt_identify_and_summary_gossip_info_v1,
    run_gpt_prompt_first_order_evaluation_v1,
    run_gpt_prompt_second_order_evaluation_v1,
)
from .reputation_update import reputation_update_invest, reputation_update_sign_up, reputation_update_pd_game
from .social_network import social_network_update_after_gossip


def first_order_gossip(init_persona, target_persona, init_persona_role, complain_persona_role, personas, G, val):
    """
    init_persona: gossiper
    target_persona: listener
    init_persona_role: gossiper role
    complain_persona_role: complained person role
    """
    print("FIRST ORDER GOSSIP")
    finished = []
    if val["complaint_target_role"] != complain_persona_role:
        return
    reason = val["complaint_reason"]
    # gossip chat
    convo = generate_convo(init_persona, target_persona, reason, val["complaint_target"], role=init_persona_role)
    init_persona.associativeMemory.add_chat(
        subject=init_persona.name,
        predicate="gossip",
        obj=target_persona.name,
        description=reason,
        created_at=init_persona.scratch.curr_step,
        conversation=convo,
    )
    target_persona.associativeMemory.add_chat(
        subject=init_persona.name,
        predicate="gossip",
        obj=target_persona.name,
        description=reason,
        created_at=init_persona.scratch.curr_step,
        conversation=convo,
    )
    # gossip evaluation
    complain_info = {
        "gossip chat": convo,
        "complained name": val["complaint_target"],
        "complained ID": val["complaint_target_ID"],
        "complained role": complain_persona_role,
    }
    gossip_info = run_gpt_prompt_identify_and_summary_gossip_info_v1(target_persona, init_persona, complain_info, init_persona_role=init_persona_role)[0]
    complain_info["gossip info"] = gossip_info
    complain_info["gossiper role"] = init_persona_role
    gossip = run_gpt_prompt_first_order_evaluation_v1(target_persona, init_persona, complain_info, init_persona_role)[0]
    target_persona.gossipDB.add_gossip(gossip, target_persona.scratch.curr_step)
    # reputation update
    if complain_info["complained role"] != "resident" and complain_info["complained role"] != "player":
        update_info = {
            "reason": "reputation update after first order gossip",
            "init_persona_role": init_persona_role,
            "target_persona_role": complain_persona_role,
            "gossip": gossip,
            "total_number_of_people": len(personas),
            "number_of_bidirectional_connections": len(
                get_d_connect(
                    personas[complain_info["complained name"]],
                    G[complain_info["complained role"]],
                )
            ),
        }
        reputation_update_invest(
            target_persona,
            personas[complain_info["complained name"]],
            update_info,
        )
    elif complain_info["complained role"] == "player":
        update_info = {
            "reason": "reputation update after first order gossip",
            "init_persona_role": init_persona_role,
            "target_persona_role": complain_persona_role,
            "gossip": gossip,
        }
        reputation_update_pd_game(
            target_persona,
            personas[complain_info["complained name"]],
            update_info,
        )
    else:
        update_info = {
            "reason": "reputation update after first order gossip",
            "init_persona_role": init_persona_role,
            "target_persona_role": complain_persona_role,
            "gossip": gossip,
            "total_number_of_people": len(personas),
            "number_of_bidirectional_connections": len(
                get_d_connect(
                    personas[complain_info["complained name"]],
                    G[complain_info["complained role"]],
                )
            ),
        }
        reputation_update_sign_up(
            target_persona,
            personas[complain_info["complained name"]],
            update_info,
        )

    social_network_update_after_gossip(
        target_persona,
        personas[complain_info["complained name"]],
        init_persona_role,
        complain_persona_role,
        init_persona.name,
        gossip[0]["gossip info"],
    )

    if gossip[0]["whether to spread gossip second-hand"] == "Yes":
        complain_info = {
            "original gossiper name": init_persona.name,
            "original gossiper ID": init_persona.scratch.ID,
            "original gossiper role": init_persona_role,
            "first-order listener name": target_persona.name,
            "first-order listener ID": target_persona.scratch.ID,
            "first-order listener role": complain_persona_role,
            "complained name": val["complaint_target"],
            "complained ID": val["complaint_target_ID"],
            "complained role": complain_persona_role,
            "complain reason": gossip[0]["reasons"],
        }
        second_order_gossip(
            target_persona,
            init_persona_role,
            complain_persona_role,
            complain_info,
            personas,
            G,
        )
    finished.append(val)
    for f in finished:
        init_persona.scratch.complain_buffer.remove(f)


def second_order_gossip(
    init_persona,
    init_persona_role,
    complain_persona_role,
    complain_info,
    personas,
    G,
):
    print("SECOND ORDER GOSSIP")
    complain_persona = personas[complain_info["complained name"]]
    gossip_target_investor = run_gpt_prompt_gossip_listener_select_v2(init_persona, init_persona_role, complain_persona)[0]

    for gossip_target in gossip_target_investor:
        gossip_target_persona = personas[gossip_target]
        # CHAT
        convo = generate_convo(
            init_persona,
            gossip_target_persona,
            complain_info["complain reason"],
            complain_info["complained name"],
            role=init_persona_role,
        )
        gossip_target_persona.associativeMemory.add_chat(
            subject=init_persona.name,
            predicate="gossip",
            obj=gossip_target_persona.name,
            description=complain_info["complain reason"],
            created_at=init_persona.scratch.curr_step,
            conversation=convo,
        )
        init_persona.associativeMemory.add_chat(
            subject=gossip_target_persona.name,
            predicate="gossip",
            obj=init_persona.name,
            description=complain_info["complain reason"],
            created_at=init_persona.scratch.curr_step,
            conversation=convo,
        )
        complain_info["gossip chat"] = convo
        gossip_info = run_gpt_prompt_identify_and_summary_gossip_info_v1(gossip_target_persona, init_persona, complain_info, init_persona_role=init_persona_role)[0]
        complain_info["gossip info"] = gossip_info
        complain_info["gossiper role"] = init_persona_role
        gossip = run_gpt_prompt_second_order_evaluation_v1(gossip_target_persona, init_persona, complain_info, init_persona_role=init_persona_role)[0]
        gossip[0]["gossiper name"] = init_persona.name
        gossip_target_persona.gossipDB.add_gossip(gossip, gossip_target_persona.scratch.curr_step)
        # reputation update
        if complain_info["complained role"] != "resident" and complain_info["complained role"] != "player":
            update_info = {
                "reason": "reputation update after second order gossip",
                "init_persona_role": init_persona_role,
                "target_persona_role": complain_persona_role,
                "gossip": gossip,
                "total_number_of_people": len(personas),
                "number_of_bidirectional_connections": len(get_d_connect(complain_persona, G[complain_info["complained role"]])),
            }
            reputation_update_invest(
                gossip_target_persona,
                complain_persona,
                update_info,
            )
        elif complain_info["complained role"] == "player":
            update_info = {
                "reason": "reputation update after second order gossip",
                "init_persona_role": init_persona_role,
                "target_persona_role": complain_persona_role,
                "gossip": gossip,
            }
            reputation_update_pd_game(
                gossip_target_persona,
                complain_persona,
                update_info,
            )
        else:
            update_info = {
                "reason": "reputation update after second order gossip",
                "init_persona_role": init_persona_role,
                "target_persona_role": complain_persona_role,
                "gossip": gossip,
                "total_number_of_people": len(personas),
                "number_of_bidirectional_connections": len(get_d_connect(complain_persona, G[complain_info["complained role"]])),
            }
            reputation_update_sign_up(
                gossip_target_persona,
                complain_persona,
                update_info,
            )
        social_network_update_after_gossip(
            gossip_target_persona,
            complain_persona,
            init_persona_role,
            complain_persona_role,
            init_persona.name,
            gossip[0]["gossip info"],
        )


def generate_convo(init_persona, target_persona, reason, complain_target, role):
    convo = run_gpt_prompt_gossip_v2(init_persona, target_persona, reason, complain_target, role)[0]
    print(convo)
    return convo


def get_d_connect(init_persona, G):
    d_connect_list = []
    for edge in G.edges():
        if edge[0] == init_persona.name:
            if G.has_edge(edge[1], init_persona.name):
                d_connect_list.append(edge[1])
    return d_connect_list
