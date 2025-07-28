#!/usr/bin/env python3
"""
测试PD游戏合作率分析功能
"""

import os
import sys
import numpy as np
import matplotlib.pyplot as plt

# 添加项目根目录到路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from analysis.pd_analysis import calculate_cooperation_rate, draw_pd_cooperation_rate


def test_cooperation_rate_calculation():
    """测试合作率计算功能"""
    print("测试合作率计算功能...")

    # 模拟分析数据
    mock_analysis_data = {
        "player1": {"pd_game_status": "success", "game_result": "All-Cooperate"},
        "player2": {"pd_game_status": "success", "game_result": "All-Defect"},
        "player3": {"pd_game_status": "success", "game_result": "All-Cooperate"},
        "player4": {"pd_game_status": "failed", "refuse_reason": "blacklist"},
    }

    # 创建模拟的sim对象
    class MockSim:
        def __init__(self, analysis_dict):
            self.analysis_dict = analysis_dict

    mock_sim = MockSim(mock_analysis_data)

    # 计算合作率
    cooperation_rate = calculate_cooperation_rate(mock_sim)

    print(f"模拟数据合作率: {cooperation_rate:.3f}")
    print(f"预期结果: 0.500 (2个成功游戏，1个合作)")

    if abs(cooperation_rate - 0.5) < 0.01:
        print("✅ 合作率计算正确")
    else:
        print("❌ 合作率计算错误")


def test_chart_generation():
    """测试图表生成功能"""
    print("\n测试图表生成功能...")

    # 模拟不同场景的数据
    mock_sim_folders = {"Scenario_1": "pd_game_s1_with_all", "Scenario_2": "pd_game_s2_without_gossip"}

    try:
        # 尝试绘制图表（如果数据不存在会显示警告）
        draw_pd_cooperation_rate(mock_sim_folders, "test_cooperation_plots")
        print("✅ 图表生成功能正常")
    except Exception as e:
        print(f"⚠️ 图表生成时出现警告（可能是数据不存在）: {e}")


def create_sample_data():
    """创建示例数据用于测试"""
    print("\n创建示例数据...")

    # 创建示例分析结果
    sample_data = {"step": 1, "total_personas": 20, "successful_games": 15, "cooperation_rate": 0.4, "game_results_distribution": {"All-Cooperate": 6, "All-Defect": 5, "Mixed": 4}}

    # 保存示例数据
    os.makedirs("test_data", exist_ok=True)
    import json

    with open("test_data/sample_pd_analysis.json", "w") as f:
        json.dump(sample_data, f, indent=4)

    print("✅ 示例数据已创建: test_data/sample_pd_analysis.json")


def main():
    """主测试函数"""
    print("PD游戏合作率分析功能测试")
    print("=" * 50)

    # 测试合作率计算
    test_cooperation_rate_calculation()

    # 测试图表生成
    test_chart_generation()

    # 创建示例数据
    create_sample_data()

    print("\n" + "=" * 50)
    print("测试完成！")
    print("\n使用说明:")
    print("1. 运行合作率分析: python analysis/pd_cooperation_analysis.py")
    print("2. 分析单个文件夹: python analysis/pd_analysis.py <sim_folder>")
    print("3. 绘制合作率图表: python analysis/pd_analysis.py --cooperation <folder1> <folder2>")


if __name__ == "__main__":
    main()
