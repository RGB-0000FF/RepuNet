#!/usr/bin/env python3
"""
测试PD游戏分析功能
"""

import os
import sys
import json

# 添加项目根目录到路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from analysis.analysis import Analysis, get_all_sim_info


def test_pd_analysis():
    """测试PD游戏分析功能"""
    print("开始测试PD游戏分析功能...")

    # 假设有一个PD游戏的模拟文件夹
    # 这里需要根据实际的文件夹名称进行调整
    sim_folder = "pd_game_s1_with_all"  # 示例文件夹名

    try:
        # 测试获取模拟信息
        print(f"尝试获取模拟信息: {sim_folder}")
        sims = get_all_sim_info(sim_folder, "pd", with_reputation=True, limit=(1, 10))

        if sims:
            print(f"成功获取 {len(sims)} 个模拟步骤")

            # 测试第一个模拟步骤的分析
            sim = sims[0]
            print(f"分析步骤 {sim.step}")

            # 检查分析字典
            for persona_name, analysis_data in sim.analysis_dict.items():
                print(f"\n角色: {persona_name}")
                print(f"  - 声誉分数: {analysis_data.get('reputation score', 'N/A')}")
                print(f"  - 资源单位: {analysis_data.get('resources_unit', 'N/A')}")
                print(f"  - PD游戏状态: {analysis_data.get('pd_game_status', 'N/A')}")

                if "game_result" in analysis_data:
                    print(f"  - 游戏结果: {analysis_data['game_result']}")

                if "player1_strategy" in analysis_data:
                    print(f"  - Player1策略: {analysis_data['player1_strategy']}")
                    print(f"  - Player2策略: {analysis_data['player2_strategy']}")

            # 保存分析结果到文件
            output_file = f"pd_analysis_test_{sim.step}.json"
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(sim.analysis_dict, f, indent=4, ensure_ascii=False)
            print(f"\n分析结果已保存到: {output_file}")

        else:
            print("未找到模拟数据")

    except Exception as e:
        print(f"测试过程中出现错误: {e}")
        print("请确保:")
        print("1. 存在PD游戏的模拟文件夹")
        print("2. 文件夹名称正确")
        print("3. 模拟数据格式正确")


if __name__ == "__main__":
    test_pd_analysis()
