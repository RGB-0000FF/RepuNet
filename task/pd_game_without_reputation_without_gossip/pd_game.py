import os
import random
import threading
import time

import networkx as nx
from decimal import Decimal
from without_reputation.gossip import first_order_gossip
from without_reputation.prompt_template.run_gpt_prompt import (
    run_gpt_prompt_gossip_listener_select_v1,
    run_gpt_prompt_update_learned_in_description_pd_game_v1,
)
from without_reputation.social_network import *
from .prompt_template.run_gpt_prompt import *
from persona.persona import Persona

# 全局同步对象
print_result_lock = threading.Lock()


def pair_each_without_reputation_without_gossip(personas, G):
    personas_keys = list(personas.keys())
    random.shuffle(personas_keys)

    pairs = []
    for i in range(0, len(personas_keys), 2):
        pairs.append((personas_keys[i], personas_keys[i + 1]))

    print(pairs)
    return pairs


def start_pd_game_without_reputation_without_gossip(
    pair: tuple[str, str],
    personas: dict[str, Persona],
    G: nx.Graph,
    save_folder: str,
    max_retries: int = 3,
):
    """开始PD游戏，支持重试机制"""
    max_attempts = max_retries + 1  # 总尝试次数 = 重试次数 + 1

    for attempt in range(max_attempts):
        try:
            return _execute_pd_game(pair, personas, G, save_folder)
        except Exception as e:
            print(f"Thread {threading.current_thread().name}: 第{attempt + 1}次尝试失败: {e}")

            if attempt < max_attempts - 1:
                print(f"Thread {threading.current_thread().name}: 等待5秒后重试...")
                time.sleep(5)  # 等待5秒后重试
            else:
                print(f"Thread {threading.current_thread().name}: 已达到最大重试次数，放弃执行")
                return None, None, None, None


def _execute_pd_game(pair: tuple[str, str], personas: dict[str, Persona], G: nx.Graph, save_folder: str):
    """执行PD游戏的核心逻辑"""
    # pair[0]是player1，pair[1]是player2
    player1 = personas[pair[0]]
    player2 = personas[pair[1]]

    # Here is force to play
    print_stage1 = {
        "player1_decision": "Accept to play.",
        "player2_decision": "Accept to play.",
    }
    player1_decision = print_stage1["player1_decision"]
    player2_decision = print_stage1["player2_decision"]
    # elif [player2.name, "player"] in player1.scratch.relationship["black_list"] or [player1.name, "player"] in player2.scratch.relationship["black_list"]:
    #     print_stage1 = {
    #         "player1_decision": "Refuse to play due to blacklist.",
    #         "player2_decision": "Refuse to play due to blacklist.",
    #     }
    #     player1_decision = print_stage1["player1_decision"]
    #     player2_decision = print_stage1["player2_decision"]
    # else:
    #     # stage 1: 玩家选择策略
    #     player2_reputation_in_player1_memory = player1.reputationDB.get_targets_individual_reputation(player2.scratch.ID, "player")
    #     if player2_reputation_in_player1_memory:
    #         player1_decision = run_gpt_prompt_player_decide_whether_to_play_v1(player1, player2_reputation_in_player1_memory)[0]
    #         if "error" in player1_decision.lower():
    #             raise Exception("GPT ERROR")
    #     else:
    #         player1_decision = "Accept to play."

    #     player1_reputation_in_player2_memory = player2.reputationDB.get_targets_individual_reputation(player1.scratch.ID, "player")
    #     if player1_reputation_in_player2_memory:
    #         player2_decision = run_gpt_prompt_player_decide_whether_to_play_v1(player2, player1_reputation_in_player2_memory)[0]
    #         if "error" in player2_decision.lower():
    #             raise Exception("GPT ERROR")
    #     else:
    #         player2_decision = "Accept to play."

    #     print_stage1 = {
    #         "player1_decision": player1_decision,
    #         "player2_decision": player2_decision,
    #     }

    # 计算PD游戏结果
    if "Refuse" in player1_decision or "Refuse" in player2_decision:
        # 游戏失败
        player1.scratch.total_chat_num += 1
        player2.scratch.total_chat_num += 1

        print_stage2 = None
        print_stage3 = None
        print_stage4 = None

    else:
        # 游戏成功
        player1.scratch.total_chat_num += 1
        player2.scratch.total_chat_num += 1
        player1.scratch.success_chat_num += 1
        player2.scratch.success_chat_num += 1

        # stage 2: 执行PD游戏并计算结果
        player1_strategy = run_gpt_prompt_stage2_game_result_v1(player1, player2, verbose=True)[0]
        player2_strategy = run_gpt_prompt_stage2_game_result_v1(player2, player1, verbose=True)[0]

        if type(player1_strategy) is str and "error" in player1_strategy.lower():
            raise Exception("GPT ERROR")
        if type(player2_strategy) is str and "error" in player2_strategy.lower():
            raise Exception("GPT ERROR")

        # 根据PD博弈的决策分配收益
        # player1_strategy和player2_strategy应为"Cooperate"或"Defect"
        if isinstance(player1_strategy, dict):
            player1_strategy = player1_strategy.get("Decision", "")
        else:
            player1_strategy = player1_strategy
        if isinstance(player2_strategy, dict):
            player2_strategy = player2_strategy.get("Decision", "")
        else:
            player2_strategy = player2_strategy

        # 标准化大小写
        player1_strategy = player1_strategy.strip().capitalize()
        player2_strategy = player2_strategy.strip().capitalize()

        # 根据决策分配收益
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
            # 出现异常决策
            player1_payoff = 0
            player2_payoff = 0
            game_result = "Error"

        # 更新玩家资源
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

        # stage 3: 玩家评估
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

        # stage 4: 声誉更新
        update_info_player1 = {
            "reason": "reputation update after pd_game",
            "init_persona_role": "player",
            "init_behavior_summary": player1_evaluation["self_reflection"],
            "target_behavior_summary": player1_evaluation["opponent_reflection"],
        }
        update_info_player2 = {
            "reason": "reputation update after pd_game",
            "init_persona_role": "player",
            "init_behavior_summary": player2_evaluation["self_reflection"],
            "target_behavior_summary": player2_evaluation["opponent_reflection"],
        }

        player1_new_learned = run_gpt_prompt_update_learned_in_description_pd_game_v1(player1, "player", update_info_player1["init_behavior_summary"])[0]
        if type(player1_new_learned) is str and "error" in player1_new_learned.lower():
            raise Exception("GPT ERROR")
        player1.scratch.learned = player1_new_learned
        player2_new_learned = run_gpt_prompt_update_learned_in_description_pd_game_v1(player2, "player", update_info_player2["init_behavior_summary"])[0]
        if type(player2_new_learned) is str and "error" in player2_new_learned.lower():
            raise Exception("GPT ERROR")
        player2.scratch.learned = player2_new_learned

        social_network_update(player1, player2, "player", "player", interaction_memory=update_info_player1["target_behavior_summary"])
        social_network_update(player2, player1, "player", "player", interaction_memory=update_info_player2["target_behavior_summary"])

        print_stage3 = {
            "player1_evaluation": player1_evaluation,
            "player2_evaluation": player2_evaluation,
        }
        print_stage4 = None
    # gossip逻辑将在主线程中顺序执行，这里不需要执行

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
    """打印PD游戏结果"""
    # 使用函数级锁，确保整个函数执行期间线程安全
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

        # 写入文件
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
