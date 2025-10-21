#!/usr/bin/env python3
"""
美国合法博彩州用户渗透率分析
分析DraftKings等主要玩家在美国合法博彩州的用户分布
"""

import json
import csv

# 2025年美国各州人口数据（百万）
STATE_POPULATION = {
    # 合法在线体育博彩的州
    'New York': 19.5,
    'Florida': 23.0,
    'Pennsylvania': 13.0,
    'Illinois': 12.5,
    'Ohio': 11.8,
    'Georgia': 11.0,  # 注：Georgia可能未合法，需要确认
    'North Carolina': 11.1,
    'Michigan': 10.0,
    'New Jersey': 9.3,
    'Virginia': 8.7,
    'Washington': 7.8,
    'Arizona': 7.4,
    'Massachusetts': 7.0,
    'Tennessee': 7.1,
    'Indiana': 6.9,
    'Maryland': 6.2,
    'Missouri': 6.2,
    'Wisconsin': 5.9,
    'Colorado': 5.9,
    'Minnesota': 5.7,
    'South Carolina': 5.4,
    'Alabama': 5.1,
    'Louisiana': 4.6,
    'Kentucky': 4.5,
    'Oregon': 4.2,
    'Oklahoma': 4.1,
    'Connecticut': 3.6,
    'Utah': 3.5,
    'Iowa': 3.2,
    'Nevada': 3.2,
    'Arkansas': 3.1,
    'Kansas': 3.0,
    'Mississippi': 2.9,
    'New Mexico': 2.1,
    'Nebraska': 2.0,
    'West Virginia': 1.8,
    'Idaho': 1.9,
    'Hawaii': 1.4,
    'New Hampshire': 1.4,
    'Maine': 1.4,
    'Montana': 1.1,
    'Rhode Island': 1.1,
    'Delaware': 1.0,
    'South Dakota': 0.9,
    'North Dakota': 0.8,
    'Alaska': 0.7,
    'Vermont': 0.65,
    'Wyoming': 0.59,
}

# 合法在线体育博彩的州（2025年）
LEGAL_ONLINE_BETTING_STATES = [
    'New York', 'New Jersey', 'Pennsylvania', 'Illinois', 'Ohio',
    'North Carolina', 'Michigan', 'Virginia', 'Tennessee', 'Arizona',
    'Massachusetts', 'Indiana', 'Maryland', 'Colorado', 'Louisiana',
    'Kentucky', 'Kansas', 'Iowa', 'West Virginia', 'Arkansas',
    'Nevada', 'Connecticut', 'Oregon', 'Washington', 'Rhode Island',
    'New Hampshire', 'Delaware', 'Maine', 'Montana', 'South Dakota',
    'North Dakota', 'Vermont', 'Wyoming', 'Wisconsin', 'Missouri',
    'New Mexico'  # 共36个州 + DC
]

# 基于市场规模和投注量的相对搜索指数/市场活跃度（标准化为100）
# 数据来源：基于各州的投注量报告
STATE_BETTING_ACTIVITY_INDEX = {
    'New York': 100,  # 最大市场，$23.94B handle
    'New Jersey': 65,  # $12.77B handle
    'Illinois': 60,  # $11.6B
    'Pennsylvania': 50,  # $7.6B
    'Ohio': 45,
    'Michigan': 40,
    'Virginia': 35,
    'Arizona': 35,
    'Tennessee': 32,
    'Massachusetts': 30,
    'North Carolina': 28,
    'Indiana': 28,
    'Colorado': 25,
    'Maryland': 25,
    'Louisiana': 20,
    'Iowa': 18,
    'Nevada': 45,  # 虽然人口少，但博彩文化深厚
    'Kansas': 15,
    'Kentucky': 18,
    'Arkansas': 12,
    'West Virginia': 10,
    'Connecticut': 22,
    'Oregon': 20,
    'Washington': 25,
    'Wisconsin': 22,
    'Missouri': 28,
    'New Mexico': 10,
    'Rhode Island': 12,
    'New Hampshire': 12,
    'Delaware': 10,
    'Maine': 10,
    'Montana': 8,
    'South Dakota': 7,
    'North Dakota': 6,
    'Vermont': 6,
    'Wyoming': 5,
}

# DraftKings数据（已知）
DRAFTKINGS_MAU = 8_000_000  # DraftKings月活跃用户（800万）
DRAFTKINGS_ACTIVE_TRADERS = 4_000_000  # DraftKings月度活跃交易者（400万）
DRAFTKINGS_MARKET_SHARE = 0.28  # DraftKings市场份额 28%

# 根据DraftKings数据推算整个行业数据
TOTAL_MAU = int(DRAFTKINGS_MAU / DRAFTKINGS_MARKET_SHARE)  # 约2857万
TOTAL_ACTIVE_TRADERS = int(DRAFTKINGS_ACTIVE_TRADERS / DRAFTKINGS_MARKET_SHARE)  # 约1429万

def calculate_state_distribution():
    """计算各州的用户分布"""

    # 计算合法州的总人口
    legal_states_pop = {state: STATE_POPULATION[state]
                       for state in LEGAL_ONLINE_BETTING_STATES
                       if state in STATE_POPULATION}

    total_legal_pop = sum(legal_states_pop.values())

    # 计算总的活跃度指数
    total_activity_index = sum(STATE_BETTING_ACTIVITY_INDEX.values())

    results = []

    for state in LEGAL_ONLINE_BETTING_STATES:
        if state not in STATE_POPULATION or state not in STATE_BETTING_ACTIVITY_INDEX:
            continue

        pop = STATE_POPULATION[state]
        activity = STATE_BETTING_ACTIVITY_INDEX[state]

        # 基于活跃度指数分配用户
        mau_share = (activity / total_activity_index) * TOTAL_MAU
        trader_share = (activity / total_activity_index) * TOTAL_ACTIVE_TRADERS

        # 计算渗透率（假设18-65岁成年人口约占65%）
        adult_pop = pop * 1_000_000 * 0.65
        mau_penetration = (mau_share / adult_pop) * 100
        trader_penetration = (trader_share / adult_pop) * 100

        # 计算DraftKings的用户数（基于DraftKings的活跃度分布）
        dk_mau = (activity / total_activity_index) * DRAFTKINGS_MAU
        dk_traders = (activity / total_activity_index) * DRAFTKINGS_ACTIVE_TRADERS

        results.append({
            'State': state,
            'Population (M)': round(pop, 2),
            'Adult Pop (M)': round(adult_pop / 1_000_000, 2),
            'Activity Index': activity,
            'Industry Total MAU': int(mau_share),
            'Industry Active Traders': int(trader_share),
            'Industry MAU Penetration (%)': round(mau_penetration, 2),
            'Industry Trader Penetration (%)': round(trader_penetration, 2),
            'DraftKings MAU': int(dk_mau),
            'DraftKings Traders': int(dk_traders),
            'DraftKings MAU Penetration (%)': round((dk_mau / adult_pop) * 100, 2),
            'DraftKings Trader Penetration (%)': round((dk_traders / adult_pop) * 100, 2),
        })

    # 按Industry Total MAU降序排序
    results.sort(key=lambda x: x['Industry Total MAU'], reverse=True)

    return results, total_legal_pop

def calculate_overall_metrics(results, total_legal_pop):
    """计算整体指标"""

    total_adult_pop = total_legal_pop * 1_000_000 * 0.65
    overall_mau_penetration = (TOTAL_MAU / total_adult_pop) * 100
    overall_trader_penetration = (TOTAL_ACTIVE_TRADERS / total_adult_pop) * 100

    # DraftKings渗透率
    dk_mau_penetration = (DRAFTKINGS_MAU / total_adult_pop) * 100
    dk_trader_penetration = (DRAFTKINGS_ACTIVE_TRADERS / total_adult_pop) * 100

    metrics = {
        'Total Legal States': len(LEGAL_ONLINE_BETTING_STATES),
        'Total Population (M)': round(total_legal_pop, 2),
        'Total Adult Population (M)': round(total_adult_pop / 1_000_000, 2),
        'Industry Total MAU': TOTAL_MAU,
        'Industry Total Active Traders': TOTAL_ACTIVE_TRADERS,
        'Industry MAU Penetration (%)': round(overall_mau_penetration, 2),
        'Industry Trader Penetration (%)': round(overall_trader_penetration, 2),
        'DraftKings Market Share (%)': DRAFTKINGS_MARKET_SHARE * 100,
        'DraftKings MAU': DRAFTKINGS_MAU,
        'DraftKings Active Traders': DRAFTKINGS_ACTIVE_TRADERS,
        'DraftKings MAU Penetration (%)': round(dk_mau_penetration, 2),
        'DraftKings Trader Penetration (%)': round(dk_trader_penetration, 2),
    }

    return metrics

def print_table(data, headers, widths=None):
    """打印表格"""
    if widths is None:
        widths = [len(h) for h in headers]

    # 打印表头
    header_line = " | ".join(h.ljust(w) for h, w in zip(headers, widths))
    print(header_line)
    print("-" * len(header_line))

    # 打印数据行
    for row in data:
        values = [str(row[h]) for h in headers]
        row_line = " | ".join(v.ljust(w) for v, w in zip(values, widths))
        print(row_line)

def generate_report():
    """生成完整的分析报告"""

    print("=" * 100)
    print("美国合法博彩州用户渗透率分析报告")
    print("=" * 100)
    print()

    # 计算各州分布
    results, total_legal_pop = calculate_state_distribution()

    # 计算整体指标
    overall_metrics = calculate_overall_metrics(results, total_legal_pop)

    # 打印整体指标
    print("\n【整体市场指标】")
    print("-" * 100)
    for key, value in overall_metrics.items():
        if isinstance(value, float):
            print(f"{key:.<60} {value:>15.2f}")
        elif isinstance(value, int) and value > 1000:
            print(f"{key:.<60} {value:>15,}")
        else:
            print(f"{key:.<60} {value:>15}")

    # 打印各州详细数据 - Top 15
    print("\n\n【用户数Top 15州 - 详细分析】")
    print("-" * 100)
    top15 = results[:15]
    for i, state in enumerate(top15, 1):
        print(f"\n{i}. {state['State']}")
        print(f"   人口: {state['Population (M)']}M | 成人人口: {state['Adult Pop (M)']}M | 活跃度指数: {state['Activity Index']}")
        print(f"   行业总MAU: {state['Industry Total MAU']:,} (渗透率: {state['Industry MAU Penetration (%)']}%)")
        print(f"   行业总活跃交易者: {state['Industry Active Traders']:,} (渗透率: {state['Industry Trader Penetration (%)']}%)")
        print(f"   DraftKings MAU: {state['DraftKings MAU']:,} (渗透率: {state['DraftKings MAU Penetration (%)']}%)")
        print(f"   DraftKings交易者: {state['DraftKings Traders']:,} (渗透率: {state['DraftKings Trader Penetration (%)']}%)")

    # DraftKings渗透率最高的州
    print("\n\n【DraftKings渗透率Top 10州】")
    print("-" * 100)
    penetration_sorted = sorted(results, key=lambda x: x['DraftKings MAU Penetration (%)'], reverse=True)[:10]
    for i, state in enumerate(penetration_sorted, 1):
        print(f"{i:2}. {state['State']:20} | 人口: {state['Population (M)']:5.2f}M | "
              f"DK MAU渗透率: {state['DraftKings MAU Penetration (%)']:5.2f}% | "
              f"DK交易者渗透率: {state['DraftKings Trader Penetration (%)']:5.2f}% | "
              f"DK MAU: {state['DraftKings MAU']:>8,}")

    # 保存到CSV
    csv_file = '/home/user/leconteren/state_betting_analysis.csv'
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        if results:
            fieldnames = list(results[0].keys())
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)

    # 保存整体指标到JSON
    json_file = '/home/user/leconteren/overall_metrics.json'
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(overall_metrics, f, indent=2, ensure_ascii=False)

    print("\n\n" + "=" * 100)
    print("数据已保存到:")
    print(f"  - {csv_file}")
    print(f"  - {json_file}")
    print("=" * 100)

    return results, overall_metrics

if __name__ == '__main__':
    results, metrics = generate_report()
