#!/usr/bin/env python3
"""
A 股轻量化监控脚本 (新浪财经接口)
轻量依赖：仅需 requests 库
"""

import requests
import time
from datetime import datetime
from typing import List, Dict, Optional

# ============= 配置区域 =============

# A 股自选股列表 (用户自定义)
WATCH_STOCKS = {
    "688660": ("高铁电气", "科创"),
    "600730": ("中国高科", "沪市"),
    "002612": ("朗姿股份", "深市"),
    "002864": ("高伟达", "深市"),
    "600748": ("上实发展", "沪市"),
    "002097": ("皖通科技", "深市"),
    "600619": ("海立股份", "沪市"),
    "000425": ("徐工机械", "深市"),
}

# 推送配置
MATTERMOST_WEBHOOK = "http://192.168.32.220:8065/hooks/zxigmcyefjrgbxdcaj5xg3bata"

# ============= 核心函数 =============

def get_market(code: str) -> str:
    """判断市场前缀"""
    if code.startswith("6") or code.startswith("8"):
        return "sh"
    return "sz"


def get_stock_data(code: str, name: str = None) -> Optional[Dict]:
    """
    获取单只股票数据 (新浪财经接口)
    """
    try:
        market = get_market(code)
        url = f"http://hq.sinajs.cn/list={market}{code}"
        headers = {"Referer": "http://finance.sina.com.cn"}

        resp = requests.get(url, headers=headers, timeout=10)
        content = resp.text

        if len(content) <= 30:
            return None

        # 解析数据
        parts = content.split("=")[1].split(",")
        stock_name = parts[0].strip('"')
        open_price = float(parts[1])
        close_price = float(parts[2])
        high_price = float(parts[4])
        low_price = float(parts[5])
        volume = int(parts[8])
        amount = float(parts[9])  # 成交额(万元)

        change_pct = (close_price - open_price) / open_price * 100 if open_price else 0

        return {
            "code": code,
            "name": stock_name,
            "open": open_price,
            "close": close_price,
            "high": high_price,
            "low": low_price,
            "volume": volume,
            "amount": amount,
            "change": change_pct,
        }
    except Exception as e:
        print(f"获取 {code} ({name}) 失败: {e}")
        return None


def get_batch_data(stock_dict: Dict) -> List[Dict]:
    """批量获取股票数据"""
    results = []
    for code, (name, _) in stock_dict.items():
        data = get_stock_data(code, name)
        if data:
            results.append(data)
        time.sleep(0.15)  # 避免请求过快
    return results


def format_price(price: float) -> str:
    """格式化价格"""
    if price is None:
        return "-"
    return f"{price:.2f}"


def format_change(pct: float) -> str:
    """格式化涨跌幅"""
    if pct is None:
        return "-"
    return f"{pct:+.2f}%"


def format_volume(vol: int) -> str:
    """格式化成交量"""
    if vol is None:
        return "-"
    if vol >= 1e8:
        return f"{vol/1e8:.2f}亿"
    elif vol >= 1e4:
        return f"{vol/1e4:.2f}万"
    return str(vol)


def format_amount(amount: float) -> str:
    """格式化成交额（单位：万）"""
    if amount is None:
        return "-"
    if amount >= 1e8:
        return f"{amount/1e4:.0f}万"  # 转换为万
    elif amount >= 1e4:
        return f"{amount/1e4:.0f}万"
    return f"{amount:.0f}万"


def generate_report(data_list: List[Dict]) -> str:
    """生成监控报告"""
    if not data_list:
        return "❌ 暂无数据"

    # 排序：按涨跌幅
    sorted_data = sorted(data_list, key=lambda x: x.get("change", 0), reverse=True)

    # 分类
    gainers = [d for d in sorted_data if d.get("change", 0) > 0]
    losers = [d for d in sorted_data if d.get("change", 0) < 0]
    others = [d for d in sorted_data if d.get("change", 0) == 0]

    lines = []
    lines.append(f"## 📊 A 股监控报告")
    lines.append(f"**时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append(f"**数量**: {len(data_list)} 只")
    lines.append("")

    # 上涨榜
    if gainers:
        lines.append(f"### 🟢 上涨 ({len(gainers)}只)")
        lines.append("| 代码 | 名称 | 现价 | 涨跌幅 | 成交额 |")
        lines.append("|------|------|------|--------|--------|")
        for d in gainers:
            lines.append(f"| {d['code']} | {d['name'][:4]} | {format_price(d['close'])} | {format_change(d['change'])} | {format_amount(d.get('amount'))} |")
        lines.append("")

    # 下跌榜
    if losers:
        lines.append(f"### 🔴 下跌 ({len(losers)}只)")
        lines.append("| 代码 | 名称 | 现价 | 涨跌幅 | 成交额 |")
        lines.append("|------|------|------|--------|--------|")
        for d in losers:
            lines.append(f"| {d['code']} | {d['name'][:4]} | {format_price(d['close'])} | {format_change(d['change'])} | {format_amount(d.get('amount'))} |")
        lines.append("")

    # 汇总
    if gainers or losers:
        avg_change = sum(d.get("change", 0) for d in data_list) / len(data_list)
        lines.append(f"### 📈 汇总")
        lines.append(f"- **平均涨跌幅**: {format_change(avg_change)}")
        lines.append(f"- **涨跌比**: {len(gainers)}/{len(losers)}")
        lines.append(f"- **最强**: {sorted_data[0]['code']} ({sorted_data[0]['name'][:4]}) {format_change(sorted_data[0]['change'])}")
        lines.append(f"- **最弱**: {sorted_data[-1]['code']} ({sorted_data[-1]['name'][:4]}) {format_change(sorted_data[-1]['change'])}")

    return "\n".join(lines)


def send_to_mattermost(message: str, webhook_url: str = None) -> bool:
    """推送到 Mattermost"""
    if not webhook_url:
        webhook_url = MATTERMOST_WEBHOOK

    try:
        payload = {"text": message}
        resp = requests.post(webhook_url, json=payload, timeout=10)
        return resp.status_code == 200
    except Exception as e:
        print(f"推送失败: {e}")
        return False


def quick_scan(stock_dict: Dict = None, push: bool = True):
    """快速扫描"""
    if stock_dict is None:
        stock_dict = WATCH_STOCKS

    print(f"🔍 正在扫描 {len(stock_dict)} 只股票...")
    data = get_batch_data(stock_dict)

    if not data:
        print("❌ 获取数据失败")
        return

    print("\n" + "="*50)
    report = generate_report(data)
    print(report)

    # 推送到 Mattermost
    if push:
        if send_to_mattermost(report):
            print("\n✅ 已推送到 Mattermost")
        else:
            print("\n⚠️ 推送失败")


if __name__ == "__main__":
    quick_scan()
