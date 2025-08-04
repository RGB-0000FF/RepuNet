import os
import random
import threading
import time

random.seed(42)
import networkx as nx
from decimal import Decimal
from reputation.reputation_update import reputation_update_pd_game
from reputation.social_network import *
from .prompt_template.run_gpt_prompt import *
from persona.persona import Persona

print_result_lock = threading.Lock()


def check_if_chosen(pairs, player_name):
    for pair in pairs:
        if player_name in pair:
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
        reputation = persona.reputationDB.get_targets_individual_reputation(target_persona.scratch.ID, target_persona_role)
        if reputation:
            count += 1
            repu_score = reputation[f"Player_{target_persona.scratch.ID}"]["numerical record"]
            scores = repu_score.replace("(", "").replace(")", "").split(",")
            score = float(scores[4]) + float(scores[3]) - float(scores[1]) - float(scores[0])
            if score > 1:
                score = 1
            elif score < -1:
                score = -1
            num += score
    if count == 0:
        return 0
    return round((num / count), 3)


def pair_each(personas: dict[str, Persona], G: nx.Graph):
    personas_keys = list(personas.keys())
    random.shuffle(personas_keys)

    pairs = []
    player1_list = []
    player2_list = []
    score_list = []

    for i in range(0, len(personas_keys), 2):
        player1_list.append(personas_keys[i])
        player2_list.append(personas_keys[i + 1])
        score = get_reputation_score(personas[personas_keys[i]], "player", personas)
        score_list.append(score)

    sorted_indices = sorted(range(len(score_list)), key=lambda k: score_list[k], reverse=True)
    player1_list = [player1_list[i] for i in sorted_indices]

    for player1_k in player1_list:
        player1 = personas[player1_k]
        d_connect_list = get_d_connect(player1, G["player"])
        d_connect_list_clean = [d_connect for d_connect in d_connect_list if (d_connect not in player1_list) and (not check_if_chosen(pairs, d_connect))]

        if random.random() >= 0.5 and d_connect_list_clean:
            repu_list = ""
            for persona in d_connect_list_clean:
                repu = player1.reputationDB.get_targets_individual_reputation(personas[persona].scratch.ID, "player")
                repu_list += personas[persona].scratch.name + ":" + list(repu.values())[0]["content"] + "\n"

            while True:
                result, _ = run_gpt_prompt_select_player_v1(personas[player1_k], repu_list)
                if result in d_connect_list_clean:
                    break
                else:
                    print("Value error: The player selected does not exist.")
            chosen_player2 = result

        else:
            unchosen_list = []
            for player2 in player2_list:
                if not check_if_chosen(pairs, player2):
                    unchosen_list.append(player2)
            chosen_player2 = random.choice(unchosen_list)

        pairs.append((player1_k, chosen_player2))

    print(pairs)
    return pairs


def start_pd_game_without_gossip(
    pair: tuple[str, str],
    personas: dict[str, Persona],
    G: nx.Graph,
    save_folder: str,
    max_retries: int = 3,
):
    max_attempts = max_retries + 1

    for attempt in range(max_attempts):
        try:
            return _execute_pd_game(pair, personas, G, save_folder)
        except Exception as e:
            print(f"Thread {threading.current_thread().name}: Attempt {attempt + 1} failed: {e}")

            if attempt < max_attempts - 1:
                print(f"Thread {threading.current_thread().name}: Waiting 5 seconds before retrying...")
                time.sleep(5)
            else:
                print(f"Thread {threading.current_thread().name}: Maximum retries reached, giving up")
                return None, None, None, None


def _execute_pd_game(pair: tuple[str, str], personas: dict[str, Persona], G: nx.Graph, save_folder: str):
    player1 = personas[pair[0]]
    player2 = personas[pair[1]]

    # Here is force to play
    print_stage1 = {
        "player1_decision": "Accept to play.",
        "player2_decision": "Accept to play.",
    }
    player1_decision = print_stage1["player1_decision"]
    player2_decision = print_stage1["player2_decision"]

    if "Refuse" in player1_decision or "Refuse" in player2_decision:
        player1.scratch.total_chat_num += 1
        player2.scratch.total_chat_num += 1

        print_stage2 = None
        print_stage3 = None
        print_stage4 = None

    else:
        player1.scratch.total_chat_num += 1
        player2.scratch.total_chat_num += 1
        player1.scratch.success_chat_num += 1
        player2.scratch.success_chat_num += 1

        player1_strategy = run_gpt_prompt_stage2_game_result_v1(player1, player2, verbose=True)[0]
        player2_strategy = run_gpt_prompt_stage2_game_result_v1(player2, player1, verbose=True)[0]

        if type(player1_strategy) is str and "error" in player1_strategy.lower():
            raise Exception("GPT ERROR")
        if type(player2_strategy) is str and "error" in player2_strategy.lower():
            raise Exception("GPT ERROR")

        if isinstance(player1_strategy, dict):
            player1_strategy = player1_strategy.get("Decision", "")
        else:
            player1_strategy = player1_strategy
        if isinstance(player2_strategy, dict):
            player2_strategy = player2_strategy.get("Decision", "")
        else:
            player2_strategy = player2_strategy

        player1_strategy = player1_strategy.strip().capitalize()
        player2_strategy = player2_strategy.strip().capitalize()

        if player1_strategy == "Cooperate" and player2_strategy == "Cooperate":
            player1_payoff = 3
            player2_payoff = 3
            game_result = "All-Cooperate"
        elif player1_strategy == "Cooperate" and player2_strategy == "Defect":
            player1_payoff = 0
            player2_payoff = 5
            game_result = f"{player1.name}-Cooperate, {player2.name}-Defect"
        elif player1_strategy == "Defect" and player2_strategy == "Cooperate":
            player1_payoff = 5
            player2_payoff = 0
            game_result = f"{player1.name}-Defect, {player2.name}-Cooperate"
        elif player1_strategy == "Defect" and player2_strategy == "Defect":
            player1_payoff = 1
            player2_payoff = 1
            game_result = "All-Defect"
        else:
            player1_payoff = 0
            player2_payoff = 0
            game_result = "Error"

        if hasattr(player1.scratch, "resources_unit"):
            player1.scratch.resources_unit += player1_payoff
        if hasattr(player2.scratch, "resources_unit"):
            player2.scratch.resources_unit += player2_payoff

        event_description = f"Game_result is {game_result}. {player1.name} chose {player1_strategy}, {player2.name} chose {player2_strategy}"

        player1.associativeMemory.add_event(
            subject=player1.name,
            predicate="pd_game",
            obj=player2.name,
            description=event_description,
            created_at=player1.scratch.curr_step,
        )
        player2.associativeMemory.add_event(
            subject=player2.name,
            predicate="pd_game",
            obj=player1.name,
            description=event_description,
            created_at=player1.scratch.curr_step,
        )

        print_stage2 = {
            "player1_payoff": player1_payoff,
            "player2_payoff": player2_payoff,
            "game_result": game_result,
        }

        player1_evaluation = run_gpt_prompt_stage3_player_evaluation_v1(
            player1,
            player2,
            player1_strategy,
            player2_strategy,
            verbose=True,
        )[0]
        player2_evaluation = run_gpt_prompt_stage3_player_evaluation_v1(
            player2,
            player1,
            player2_strategy,
            player1_strategy,
            verbose=True,
        )[0]

        if type(player1_evaluation) is str and "error" in player1_evaluation.lower():
            raise Exception("GPT ERROR")
        if type(player2_evaluation) is str and "error" in player2_evaluation.lower():
            raise Exception("GPT ERROR")

        update_info_player1 = {
            "reason": "reputation update after pd_game",
            "init_persona_role": "player",
            "init_behavior_summary": player1_evaluation["self_reputation"],
            "target_behavior_summary": player1_evaluation["opponent_reputation"],
            "total_number_of_people": len(personas),
            "number_of_bidirectional_connections": len(get_d_connect(player2, G["player"])),
        }
        update_info_player2 = {
            "reason": "reputation update after pd_game",
            "init_persona_role": "player",
            "init_behavior_summary": player2_evaluation["self_reputation"],
            "target_behavior_summary": player2_evaluation["opponent_reputation"],
            "total_number_of_people": len(personas),
            "number_of_bidirectional_connections": len(get_d_connect(player1, G["player"])),
        }

        reputation_update_pd_game(player1, player2, update_info_player1)
        reputation_update_pd_game(player2, player1, update_info_player2)
        print_stage3 = {
            "player1_evaluation": player1_evaluation,
            "player2_evaluation": player2_evaluation,
        }
        print_stage4 = None

    print_pd_game_result(
        player1,
        player2,
        print_stage1,
        print_stage2,
        print_stage3,
        print_stage4,
        save_folder,
    )


def print_pd_game_result(player1, player2, stage1, stage2, stage3, stage4, save_folder):
    with print_result_lock:
        step = player1.scratch.curr_step
        print(f"Step: {step}")
        print("+" + "-" * (100 - 2) + "+")
        print("|" + " " * 38 + "**PD Game Result**" + " " * 38 + "|")
        print("+" + "-" * (100 - 2) + "+")

        width = 100

        # stage 1
        print("+" + "-" * (100 - 2) + "+")
        print("|" + "**Stage  1**" + " " * (width - 14) + "|")
        print("+" + "-" * (100 - 2) + "+")
        player1_line = f"| Player1: {player1.name}: decision {stage1['player1_decision']}"
        print("+" + "-" * (width - 2) + "+")
        print(player1_line + " " * (width - len(player1_line) - 1) + "|")
        player2_line = f"| Player2: {player2.name}: decision {stage1['player2_decision']}"
        print(player2_line + " " * (width - len(player2_line) - 1) + "|")
        print("+" + "-" * (width - 2) + "+")

        if "Refuse" in stage1["player1_decision"] or "Refuse" in stage1["player2_decision"]:
            print("+" + "-" * (width - 2) + "+")
            print("|" + " " * 40 + "End of PD Game " + " " * 40 + "|")
            print("+" + "-" * (width - 2) + "+")
            if not os.path.exists(save_folder):
                os.makedirs(save_folder)

            with open(f"{save_folder}/pd_game_results_{player1.scratch.curr_step}.txt", "a") as f:
                f.write("+" + "-" * (width - 2) + "+\n")
                f.write("|" + "**Stage  1**" + " " * (width - 14) + "|\n")
                f.write("+" + "-" * (width - 2) + "+\n")
                player1_line = f"| Player1: {player1.name}: decision {stage1['player1_decision']}"
                f.write("+" + "-" * (width - 2) + "+\n")
                f.write(player1_line + " " * (width - len(player1_line) - 1) + "|\n")
                player2_line = f"| Player2: {player2.name}: decision {stage1['player2_decision']}"
                f.write(player2_line + " " * (width - len(player2_line) - 1) + "|\n")
                f.write("+" + "-" * (width - 2) + "+\n")

                f.write("+" + "-" * (width - 2) + "+\n")
                f.write("|" + " " * 40 + "End of PD Game " + " " * 40 + "|\n")
                f.write("+" + "-" * (width - 2) + "+\n\n\n")

            return

        # stage 2
        if stage2 is not None:
            print("+" + "-" * (100 - 2) + "+")
            print("|" + "**Stage  2**" + " " * (width - 14) + "|")
            print("+" + "-" * (100 - 2) + "+")
            player1_line = f"| Player1: {player1.name}: payoff {stage2['player1_payoff']}"
            print("+" + "-" * (width - 2) + "+")
            print(player1_line + " " * (width - len(player1_line) - 1) + "|")
            player2_line = f"| Player2: {player2.name}: payoff {stage2['player2_payoff']}"
            print(player2_line + " " * (width - len(player2_line) - 1) + "|")
            game_result_line = f"| Game Result: {stage2['game_result']}"
            print(game_result_line + " " * (width - len(game_result_line) - 1) + "|")
            print("+" + "-" * (width - 2) + "+")

        # stage 3
        if stage3 is not None:
            print("+" + "-" * (100 - 2) + "+")
            print("|" + "**Stage  3**" + " " * (width - 14) + "|")
            print("+" + "-" * (100 - 2) + "+")
            player1_line = f"| Player1: {player1.name}: evaluation {stage3['player1_evaluation']}"
            print("+" + "-" * (width - 2) + "+")
            print(player1_line + " " * (width - len(player1_line) - 1) + "|")
            player2_line = f"| Player2: {player2.name}: evaluation {stage3['player2_evaluation']}"
            print(player2_line + " " * (width - len(player2_line) - 1) + "|")
            print("+" + "-" * (width - 2) + "+")

        # stage 4
        if stage4 is not None:
            print("+" + "-" * (100 - 2) + "+")
            print("|" + "**Stage  4**" + " " * (width - 14) + "|")
            print("+" + "-" * (100 - 2) + "+")
            player1_line = f"| Player1: {player1.name}: gossip willing {stage4['player1_gossip_willing']}"
            print("+" + "-" * (width - 2) + "+")
            print(player1_line + " " * (width - len(player1_line) - 1) + "|")
            player2_line = f"| Player2: {player2.name}: gossip willing {stage4['player2_gossip_willing']}"
            print(player2_line + " " * (width - len(player2_line) - 1) + "|")
            print("+" + "-" * (width - 2) + "+")

        print("+" + "-" * (width - 2) + "+")
        print("|" + " " * 40 + "End of PD Game " + " " * 40 + "|")
        print("+" + "-" * (width - 2) + "+")

        if not os.path.exists(save_folder):
            os.makedirs(save_folder)

        with open(f"{save_folder}/pd_game_results_{player1.scratch.curr_step}.txt", "a") as f:
            f.write("+" + "-" * (width - 2) + "+\n")
            f.write("|" + "**Stage  1**" + " " * (width - 14) + "|\n")
            f.write("+" + "-" * (width - 2) + "+\n")
            player1_line = f"| Player1: {player1.name}: decision {stage1['player1_decision']}"
            f.write("+" + "-" * (width - 2) + "+\n")
            f.write(player1_line + " " * (width - len(player1_line) - 1) + "|\n")
            player2_line = f"| Player2: {player2.name}: decision {stage1['player2_decision']}"
            f.write(player2_line + " " * (width - len(player2_line) - 1) + "|\n")
            f.write("+" + "-" * (width - 2) + "+\n")

            if stage2 is not None:
                f.write("+" + "-" * (100 - 2) + "+\n")
                f.write("|" + "**Stage  2**" + " " * (width - 14) + "|\n")
                f.write("+" + "-" * (100 - 2) + "+\n")
                player1_line = f"| Player1: {player1.name}: payoff {stage2['player1_payoff']}"
                f.write("+" + "-" * (width - 2) + "+\n")
                f.write(player1_line + " " * (width - len(player1_line) - 1) + "|\n")
                player2_line = f"| Player2: {player2.name}: payoff {stage2['player2_payoff']}"
                f.write(player2_line + " " * (width - len(player2_line) - 1) + "|\n")
                game_result_line = f"| Game Result: {stage2['game_result']}"
                f.write(game_result_line + " " * (width - len(game_result_line) - 1) + "|\n")
                f.write("+" + "-" * (width - 2) + "+\n")

            if stage3 is not None:
                f.write("+" + "-" * (100 - 2) + "+\n")
                f.write("|" + "**Stage  3**" + " " * (width - 14) + "|\n")
                f.write("+" + "-" * (100 - 2) + "+\n")
                player1_line = f"| Player1: {player1.name}: evaluation {stage3['player1_evaluation']}"
                f.write("+" + "-" * (width - 2) + "+\n")
                f.write(player1_line + " " * (width - len(player1_line) - 1) + "|\n")
                player2_line = f"| Player2: {player2.name}: evaluation {stage3['player2_evaluation']}"
                f.write(player2_line + " " * (width - len(player2_line) - 1) + "|\n")
                f.write("+" + "-" * (width - 2) + "+\n")

            if stage4 is not None:
                f.write("+" + "-" * (100 - 2) + "+\n")
                f.write("|" + "** gossip **" + " " * (width - 14) + "|\n")
                f.write("+" + "-" * (100 - 2) + "+\n")
                player1_line = f"| Player1: {player1.name}: gossip willing {stage4['player1_gossip_willing']}"
                f.write("+" + "-" * (width - 2) + "+\n")
                f.write(player1_line + " " * (width - len(player1_line) - 1) + "|\n")
                player2_line = f"| Player2: {player2.name}: gossip willing {stage4['player2_gossip_willing']}"
                f.write(player2_line + " " * (width - len(player2_line) - 1) + "|\n")
                f.write("+" + "-" * (width - 2) + "+\n")

            f.write("+" + "-" * (width - 2) + "+\n")
            f.write("|" + " " * 40 + "End of PD Game " + " " * 40 + "|\n")
            f.write("+" + "-" * (width - 2) + "+\n\n\n")
    return
