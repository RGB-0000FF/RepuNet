import random

from without_reputation.gossip import first_order_gossip
from without_reputation.prompt_template.run_gpt_prompt import (
    run_gpt_prompt_gossip_listener_select_v1,
    run_gpt_prompt_update_learned_in_description_v1,
)
from without_reputation.social_network import social_network_update_after_stage4

from .prompt_template.run_gpt_prompt import *


def pair_each_without_reputation(personas, G):
    personas_keys = list(personas.keys())
    random.shuffle(personas_keys)

    pairs = []
    for i in range(0, len(personas_keys), 2):
        pairs.append((personas_keys[i], personas_keys[i + 1]))

    print(pairs)
    return pairs


def start_investment_without_reputation(pair, personas, G, save_folder):
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
        description = (
            f"Failed investment. Investor is {investor.name} and Trustee is {trustee.name}.\n{investor_decided}",
        )
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
        trustee_gossip_willing = run_gpt_prompt_stage1_trustee_gossip_willing_v1(
            trustee,
            trustee_plan,
            investor_decided.split("Refuse.")[-1].strip(),
            verbose=True,
        )[0]
        investor_gossip_willing = run_gpt_prompt_stage1_investor_gossip_willing_v1(
            investor,
            trustee_plan,
            investor_decided.split("Refuse.")[-1].strip(),
            verbose=True,
        )[0]
        if "yes" in trustee_gossip_willing.split(",")[0].lower():
            trustee.scratch.complain_buffer.append(
                {
                    "complaint_target_ID": investor.scratch.ID,
                    "complaint_target": investor.name,
                    "complaint_target_role": "investor",
                    "complaint_reason": trustee_gossip_willing.split(",")[-1],
                }
            )
        if "yes" in investor_gossip_willing.split(",")[0].lower():
            investor.scratch.complain_buffer.append(
                {
                    "complaint_target_ID": trustee.scratch.ID,
                    "complaint_target": trustee.name,
                    "complaint_target_role": "trustee",
                    "complaint_reason": investor_gossip_willing.split(",")[-1],
                }
            )

        print_stage3 = None
        print_stage4 = {
            "trustee_gossip_willing": trustee_gossip_willing,
            "investor_gossip_willing": investor_gossip_willing,
        }

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
        # social network update after investment
        social_network_update_after_stage4(investor, trustee, "investor", "trustee")
        social_network_update_after_stage4(trustee, investor, "trustee", "investor")

        i_new_learned = run_gpt_prompt_update_learned_in_description_v1(
            investor, "investor"
        )[0]
        investor.scratch.learned = i_new_learned

        t_new_learned = run_gpt_prompt_update_learned_in_description_v1(
            trustee, "trustee"
        )[0]
        trustee.scratch.learned = t_new_learned

        # gossip willing
        investor_evaluation = run_gpt_prompt_investor_evaluation_v1(
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
        trustee_evaluation = run_gpt_prompt_trustee_evaluation_v1(
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

        print_stage4 = {
            "investor_gossip_willing": investor_evaluation["gossip"],
            "trustee_gossip_willing": trustee_evaluation["gossip"],
        }

        if "yes" in investor_evaluation["gossip"].split(",")[0].lower().strip():
            investor.scratch.complain_buffer.append(
                {
                    "complaint_target_ID": trustee.scratch.ID,
                    "complaint_target": trustee.name,
                    "complaint_target_role": "trustee",
                    "complaint_reason": investor_evaluation["gossip"]
                    .lower()
                    .split("yes,")[-1]
                    .strip(),
                }
            )

        if "yes" in trustee_evaluation["gossip"].split(",")[0].lower().strip():
            trustee.scratch.complain_buffer.append(
                {
                    "complaint_target_ID": investor.scratch.ID,
                    "complaint_target": investor.name,
                    "complaint_target_role": "investor",
                    "complaint_reason": trustee_evaluation["gossip"]
                    .lower()
                    .split("yes,")[-1]
                    .strip(),
                }
            )

    # gossip stage
    if trustee.scratch.complain_buffer:
        # gossip target choose
        gossip_target_trustee = run_gpt_prompt_gossip_listener_select_v1(
            trustee, "trustee", investor
        )[0]
        for gossip_target in gossip_target_trustee:
            # gossip chat
            gossip_target_persona = personas[gossip_target["name"]]
            first_order_gossip(
                trustee,
                gossip_target_persona,
                "trustee",
                "investor",
                personas,
                G,
            )
    if investor.scratch.complain_buffer:
        # gossip target choose
        gossip_target_investor = run_gpt_prompt_gossip_listener_select_v1(
            investor, "investor", trustee
        )[0]
        for gossip_target in gossip_target_investor:
            # gossip chat
            gossip_target_persona = personas[gossip_target["name"]]
            first_order_gossip(
                investor,
                gossip_target_persona,
                "investor",
                "trustee",
                personas,
                G,
            )

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

            f.write("+" + "-" * (100 - 2) + "+\n")
            f.write("|" + "** gossip **" + " " * (width - 14) + "|\n")
            f.write("+" + "-" * (100 - 2) + "+\n")
            trustee_line = f"| Trustee: {trustee.name}: gossip willing {stage4['trustee_gossip_willing']}"
            f.write("+" + "-" * (width - 2) + "+\n")
            f.write(trustee_line + " " * (width - len(trustee_line) - 1) + "|\n")
            investor_line = f"| Investor: {investor.name}: gossip willing {stage4['investor_gossip_willing']}"
            f.write(investor_line + " " * (width - len(investor_line) - 1) + "|\n")
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

    # stage 4
    print("+" + "-" * (100 - 2) + "+")
    print("|" + "**Stage  4**" + " " * (width - 14) + "|")
    print("+" + "-" * (100 - 2) + "+")
    trustee_line = (
        f"| Trustee: {trustee.name}: gossip willing {stage4['trustee_gossip_willing']}"
    )
    print("+" + "-" * (width - 2) + "+")
    print(trustee_line + " " * (width - len(trustee_line) - 1) + "|")
    investor_line = f"| Investor: {investor.name}: gossip willing {stage4['investor_gossip_willing']}"
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

        f.write("+" + "-" * (100 - 2) + "+\n")
        f.write("|" + "** gossip **" + " " * (width - 14) + "|\n")
        f.write("+" + "-" * (100 - 2) + "+\n")
        trustee_line = f"| Trustee: {trustee.name}: gossip willing {stage4['trustee_gossip_willing']}"
        f.write("+" + "-" * (width - 2) + "+\n")
        f.write(trustee_line + " " * (width - len(trustee_line) - 1) + "|\n")
        investor_line = f"| Investor: {investor.name}: gossip willing {stage4['investor_gossip_willing']}"
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
