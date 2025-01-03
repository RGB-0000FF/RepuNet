import random


from reputation.reputation_update import reputation_update

from .prompt_template.run_gpt_prompt import *


def pair_each_without_gossip(personas, G):
    personas_keys = list(personas.keys())
    random.shuffle(personas_keys)

    pairs = []
    investor_list = []
    trustee_list = []
    score_list = []
    for i in range(0, len(personas_keys), 2):
        investor_list.append(personas_keys[i])
        trustee_list.append(personas_keys[i + 1])
        score = get_reputation_score(personas[personas_keys[i]], "investor", personas)
        score_list.append(score)

    # Sort investor_list based on score_list
    sorted_indices = sorted(
        range(len(score_list)), key=lambda k: score_list[k], reverse=True
    )
    investor_list = [investor_list[i] for i in sorted_indices]

    # chosen trustee for each investor
    for investor_k in investor_list:
        investor = personas[investor_k]
        d_connect_list = get_d_connect(investor, G)
        d_connect_list_clean = [
            d_connect for d_connect in d_connect_list if d_connect not in investor_list
        ]
        unchosen_list = []
        weight_list = []
        for d_connect_trustee in d_connect_list_clean:
            if not check_if_chosen(pairs, d_connect_trustee):
                unchosen_list.append(d_connect_trustee)
                weight_list.append(2)
        for unchosen_trustee in trustee_list:
            if (
                not check_if_chosen(pairs, unchosen_trustee)
                and unchosen_trustee not in unchosen_list
            ):
                unchosen_list.append(unchosen_trustee)
                weight_list.append(1)
        chosen_trustee = random.choices(unchosen_list, weight_list)[0]
        pairs.append((investor_k, chosen_trustee))

    print(pairs)
    return pairs


def check_if_chosen(pairs, trustee_name):
    for pair in pairs:
        if trustee_name in pair:
            return True
    return False


def get_d_connect(init_persona, G):
    d_connect_list = []
    for edge in G.edges():
        if edge[0] == init_persona.name:
            if G.has_edge(edge[1], init_persona.name):
                d_connect_list.append(edge[1])
    return d_connect_list


def get_reputation_score(target_persona, target_persona_role, personas):
    count = 0
    num = 0
    for _, persona in personas.items():
        reputation = persona.reputationDB.get_targets_individual_reputation(
            target_persona.scratch.ID, target_persona_role
        )
        if target_persona_role == "investor":
            input = "Investor"
        elif target_persona_role == "trustee":
            input = "Trustee"
        if reputation:
            count += 1
            repu_score = reputation[f"{input}_{target_persona.scratch.ID}"][
                "numerical record"
            ]
            scores = repu_score.replace("(", "").replace(")", "").split(",")
            score = (
                float(scores[4])
                + float(scores[3])
                - float(scores[1])
                - float(scores[0])
            )
            if score > 1:
                score = 1
            elif score < -1:
                score = -1
            num += score
    if count == 0:
        return 0
    return num / count


def start_investment_without_gossip(pair, personas, G, save_folder):
    # the pair[0] is investor and the pair[1] is trustee
    investor = personas[pair[0]]
    trustee = personas[pair[1]]

    if (
        trustee.name in investor.scratch.relationship["black_list"]
        or investor.name in trustee.scratch.relationship["black_list"]
    ):
        print_stage1 = {
            "plan": "There is no plan for this investment because both parties might be on each other's blacklist.",
            "investor_decided": "Refuse. The investors refused because the parties might be on each other's blacklist.",
        }
        trustee_plan = print_stage1["plan"]
        investor_decided = print_stage1["investor_decided"]
    else:
        # stage 1
        trustee_plan = run_gpt_prompt_trustee_plan_v1(trustee, investor, verbose=True)[
            0
        ]
        # Negotiation - Trustee proposes a plan for resource allocation and profit sharing

        trustee_part = trustee_plan.split("trustee retains")[-1].split(".")[0].strip()

        investor_part = (
            trustee_plan.split("investor receives")[-1].split("of")[0].strip()
        )

        investor_decided = run_gpt_prompt_investor_decided_v1(
            investor, trustee, trustee_plan, verbose=True
        )[0]

        print_stage1 = {
            "plan": f"trustee_part: {trustee_part}, investor_part: {investor_part}",
            "investor_decided": investor_decided,
        }

    if "Refuse" in investor_decided:
        # total investment num +1
        investor.scratch.total_num_investor += 1
        trustee.scratch.total_num_trustee += 1
        description = f"Failed investment. Investor is {investor.name} and Trustee is {trustee.name}.\n{investor_decided}"
        investor.associativeMemory.add_event(
            subject=investor.name,
            predicate="investment",
            obj=trustee.name,
            description=description,
            created_at=investor.scratch.curr_step,
        )
        trustee.associativeMemory.add_event(
            subject=trustee.name,
            predicate="investment",
            obj=investor.name,
            description=description,
            created_at=investor.scratch.curr_step,
        )

        # eputation update agter stage 1
        # update_info_investor = {
        #     "reason": "reputation update agter stage 1",
        #     "init_persona_role": "investor",
        #     "allocation_plan": trustee_plan,
        #     "reason_refusal": investor_decided,
        #     "total_number_of_people": len(personas),
        #     "number_of_bidirectional_connections": len(get_d_connect(trustee, G)),
        # }
        # update_info_trustee = {
        #     "reason": "reputation update agter stage 1",
        #     "init_persona_role": "trustee",
        #     "allocation_plan": trustee_plan,
        #     "reason_refusal": investor_decided,
        #     "total_number_of_people": len(personas),
        #     "number_of_bidirectional_connections": len(get_d_connect(investor, G)),
        # }
        # reputation_update(investor, trustee, update_info_investor)
        # reputation_update(trustee, investor, update_info_trustee)

        print_stage3 = None
        print_stage4 = None

    elif "Accept" in investor_decided:
        # success investment num +1
        investor.scratch.total_num_investor += 1
        trustee.scratch.total_num_trustee += 1
        investor.scratch.success_num_investor += 1
        trustee.scratch.success_num_trustee += 1

        # stage 2
        a_unit = float(
            investor_decided.split("Allocation")[-1].split("unit")[0].strip()
        )
        investor.scratch.resources_unit -= a_unit
        # k is 2
        k = 2
        unallocated_unit = a_unit * k

        # stage 3
        trustee_allocation = run_gpt_prompt_trustee_stage_3_actual_allocation_v1(
            investor, trustee, trustee_plan, a_unit, k, unallocated_unit, verbose=True
        )[0]
        trustee_allocation_part = float(trustee_allocation["trustee"])
        investor_allocation_part = float(trustee_allocation["investor"])
        # divide the resources
        trustee.scratch.resources_unit += trustee_allocation_part
        investor.scratch.resources_unit += investor_allocation_part

        reported_investment_outcome = trustee_allocation["reported_investment_outcome"]

        event_description = (
            f"Success investment: investor is {investor.name}, trustee is {trustee.name}\n"
            f"stage 1: trustee_plan is {trustee_plan}\n"
            f"stage 2: investor invests {a_unit} units\n"
            f"stage 3: trustee_allocation is {trustee_allocation}, and reported_investment_outcome is {reported_investment_outcome}"
        )
        investor.associativeMemory.add_event(
            subject=investor.name,
            predicate="investment",
            obj=trustee.name,
            description=event_description,
            created_at=investor.scratch.curr_step,
        )
        trustee.associativeMemory.add_event(
            subject=trustee.name,
            predicate="investment",
            obj=investor.name,
            description=event_description,
            created_at=investor.scratch.curr_step,
        )
        print_stage3 = {
            "investor_actual_allocation_part": investor_allocation_part,
            "trustee_actual_allocation_part": trustee_allocation_part,
            "reported_investment_outcome": reported_investment_outcome,
        }

        # stage 4
        investor_evaluation = run_gpt_prompt_stage4_investor_evaluation_v1(
            investor,
            trustee,
            trustee_plan,
            a_unit,
            k,
            a_unit * k,
            trustee_part,
            investor_part,
            reported_investment_outcome,
            trustee_allocation_part,
            investor_allocation_part,
            verbose=True,
        )[0]
        trustee_evaluation = run_gpt_prompt_stage4_trustee_evaluation_v1(
            trustee,
            investor,
            trustee_plan,
            a_unit,
            k,
            a_unit * k,
            trustee_part,
            investor_part,
            reported_investment_outcome,
            trustee_allocation_part,
            investor_allocation_part,
            verbose=True,
        )[0]

        # eputation update agter stage 4
        update_info_investor = {
            "reason": "reputation update agter stage 4",
            "init_persona_role": "investor",
            "init_behavior_summary": investor_evaluation["self_reputation"],
            "target_behavior_summary": investor_evaluation["trustee_reputation"],
            "total_number_of_people": len(personas),
            "number_of_bidirectional_connections": len(get_d_connect(trustee, G)),
        }
        update_info_trustee = {
            "reason": "reputation update agter stage 4",
            "init_persona_role": "trustee",
            "init_behavior_summary": trustee_evaluation["self_reputation"],
            "target_behavior_summary": trustee_evaluation["investor_reputation"],
            "total_number_of_people": len(personas),
            "number_of_bidirectional_connections": len(get_d_connect(investor, G)),
        }
        reputation_update(investor, trustee, update_info_investor)
        reputation_update(trustee, investor, update_info_trustee)

        print_stage4 = None

    print_investment_result(
        investor, trustee, print_stage1, print_stage3, print_stage4, save_folder
    )


def print_investment_result(investor, trustee, stage1, stage3, stage4, save_folder):
    step = investor.scratch.curr_step
    print(f"Step: {step}")
    print("+" + "-" * (100 - 2) + "+")
    print("|" + " " * 38 + "**Investment  Result**" + " " * 38 + "|")
    print("+" + "-" * (100 - 2) + "+")

    width = 100

    # stage 1
    print("+" + "-" * (100 - 2) + "+")
    print("|" + "**Stage  1**" + " " * (width - 14) + "|")
    print("+" + "-" * (100 - 2) + "+")
    trustee_line = f"| Trustee: {trustee.name}: allocated plan {stage1['plan']}"
    print("+" + "-" * (width - 2) + "+")
    print(trustee_line + " " * (width - len(trustee_line) - 1) + "|")
    investor_line = (
        f"| Investor: {investor.name}: investor decided {stage1['investor_decided']}"
    )
    print(investor_line + " " * (width - len(investor_line) - 1) + "|")
    print("+" + "-" * (width - 2) + "+")

    if "Refuse" in stage1["investor_decided"] or "Reject" in stage1["investor_decided"]:
        print("+" + "-" * (width - 2) + "+")
        print("|" + " " * 40 + "End of Investment " + " " * 40 + "|")
        print("+" + "-" * (width - 2) + "+")
        if not os.path.exists(save_folder):
            os.makedirs(save_folder)
        with open(
            f"{save_folder}/investment_results_{investor.scratch.curr_step}.txt", "a"
        ) as f:
            f.write("+" + "-" * (width - 2) + "+\n")
            f.write("|" + "**Stage  1**" + " " * (width - 14) + "|\n")
            f.write("+" + "-" * (width - 2) + "+\n")
            trustee_line = f"| Trustee: {trustee.name}: allocated plan {stage1['plan']}"
            f.write("+" + "-" * (width - 2) + "+\n")
            f.write(trustee_line + " " * (width - len(trustee_line) - 1) + "|\n")
            investor_line = f"| Investor: {investor.name}: investor decided {stage1['investor_decided']}"
            f.write(investor_line + " " * (width - len(investor_line) - 1) + "|\n")
            f.write("+" + "-" * (width - 2) + "+\n")

            f.write("+" + "-" * (width - 2) + "+\n")

            f.write("+" + "-" * (width - 2) + "+\n")
            f.write("|" + " " * 40 + "End of Investment " + " " * 40 + "|\n")
            f.write("+" + "-" * (width - 2) + "+\n\n\n")

        return

    # stage 3
    print("+" + "-" * (100 - 2) + "+")
    print("|" + "**Stage  3**" + " " * (width - 14) + "|")
    print("+" + "-" * (100 - 2) + "+")
    trustee_line = f"| Trustee: {trustee.name}: actual allocation {stage3['trustee_actual_allocation_part']}"
    print("+" + "-" * (width - 2) + "+")
    print(trustee_line + " " * (width - len(trustee_line) - 1) + "|")
    investor_line = f"| Investor: {investor.name}: actual allocation {stage3['investor_actual_allocation_part']}"
    print(investor_line + " " * (width - len(investor_line) - 1) + "|")
    print("+" + "-" * (width - 2) + "+")

    print("+" + "-" * (width - 2) + "+")
    print("|" + " " * 40 + "End of Investment " + " " * 40 + "|")
    print("+" + "-" * (width - 2) + "+")

    # Write investment results to file
    if not os.path.exists(save_folder):
        os.makedirs(save_folder)
    with open(
        f"{save_folder}/investment_results_{investor.scratch.curr_step}.txt", "a"
    ) as f:
        f.write("+" + "-" * (width - 2) + "+\n")
        f.write("|" + "**Stage  1**" + " " * (width - 14) + "|\n")
        f.write("+" + "-" * (width - 2) + "+\n")
        trustee_line = f"| Trustee: {trustee.name}: allocated plan {stage1['plan']}"
        f.write("+" + "-" * (width - 2) + "+\n")
        f.write(trustee_line + " " * (width - len(trustee_line) - 1) + "|\n")
        investor_line = f"| Investor: {investor.name}: investor decided {stage1['investor_decided']}"
        f.write(investor_line + " " * (width - len(investor_line) - 1) + "|\n")
        f.write("+" + "-" * (width - 2) + "+\n")

        f.write("+" + "-" * (100 - 2) + "+\n")
        f.write("|" + "**Stage  3**" + " " * (width - 14) + "|\n")
        f.write("+" + "-" * (100 - 2) + "+\n")
        trustee_line = f"| Trustee: {trustee.name}: actual allocation {stage3['trustee_actual_allocation_part']}"
        f.write("+" + "-" * (width - 2) + "+\n")
        f.write(trustee_line + " " * (width - len(trustee_line) - 1) + "|\n")
        investor_line = f"| Investor: {investor.name}: actual allocation {stage3['investor_actual_allocation_part']}"
        f.write(investor_line + " " * (width - len(investor_line) - 1) + "|\n")
        f.write("+" + "-" * (width - 2) + "+\n")

        f.write("+" + "-" * (width - 2) + "+\n")
        f.write("|" + " " * 40 + "End of Investment " + " " * 40 + "|\n")
        f.write("+" + "-" * (width - 2) + "+\n\n\n")
    return


def random_choice_except_current(lst, current):
    # Filter out the current element
    filtered_list = [item for item in lst if item != current]
    # Randomly select from the filtered list
    if filtered_list:  # Ensure the list is not empty
        return random.choice(filtered_list)
    else:
        return None  # Return None if there are no other elements
