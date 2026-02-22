#!/usr/bin/env python3
"""
美股潜力股监控脚本 - Finnhub 数据源 + Mattermost Webhook 推送
"""

import requests
import json
from datetime import datetime

# ============================================
# 配置区
# ============================================

# Finnhub API Key
FINNHUB_API_KEY = "d6aqgspr01qqjvbre640d6aqgspr01qqjvbre64g"

# Mattermost Webhook URL
MATTERMOST_WEBHOOK_URL = "http://192.168.32.220:8065/hooks/zxigmcyefjrgbxdcaj5xg3bata"

# 候选股票列表
STOCKS = {
    # 核心持仓
    'NVDA': 'NVIDIA',
    'AAPL': 'Apple', 
    'MSFT': 'Microsoft',
    'GOOGL': 'Google',
    'AMZN': 'Amazon',
    'META': 'Meta',
    'TSLA': 'Tesla',
    'AMD': 'AMD',
    # 新兴AI
    'PLTR': 'Palantir',
    'SMCI': 'Super Micro',
    'SOUN': 'SoundHound AI',
    'AI': 'C3.ai',
    'PATH': 'UiPath',
}

FINNHUB_BASE_URL = "https://finnhub.io/api/v1"

# ============================================
# 获取股票数据
# ============================================

def get_stock_from_finnhub(symbol):
    """从 Finnhub 获取股票数据"""
    try:
        url = f"{FINNHUB_BASE_URL}/quote"
        params = {
            'symbol': symbol,
            'token': FINNHUB_API_KEY
        }
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('c') and data['c'] > 0:
                return {
                    'symbol': symbol,
                    'price': data['c'],
                    'change': data['d'],
                    'change_pct': data['dp'],
                }
    except Exception as e:
        print(f"Error fetching {symbol}: {e}")
    return None

# ============================================
# Mattermost 推送
# ============================================

def send_to_mattermost(text):
    """发送消息到 Mattermost 频道"""
    try:
        payload = {"text": text}
        response = requests.post(MATTERMOST_WEBHOOK_URL, json=payload, timeout=10)
        if response.status_code in [200, 201]:
            print("✅ 已推送到 Mattermost")
            return True
        else:
            print(f"❌ Mattermost 推送失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Mattermost 连接错误: {e}")
        return False

# ============================================
# 生成报告
# ============================================

def generate_report():
    """生成股票监控报告"""
    print(f"\n📈 美股监控 - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 60)
    
    success = 0
    results = []
    
    for symbol in STOCKS:
        data = get_stock_from_finnhub(symbol)
        if data:
            emoji = "🟢" if data['change'] > 0 else "🔴" if data['change'] < 0 else "⚪"
            results.append((symbol, STOCKS[symbol], data['price'], data['change_pct']))
            success += 1
    
    # 按涨跌幅排序
    results.sort(key=lambda x: x[3], reverse=True)
    
    report_lines = []
    report_lines.append(f"**📈 美股监控 - {datetime.now().strftime('%Y-%m-%d %H:%M')}**\n")
    
    for symbol, name, price, change_pct in results:
        emoji = "🟢" if change_pct > 0 else "🔴" if change_pct < 0 else "⚪"
        report_lines.append(f"{emoji} **{symbol}** {name} ${price:.2f} {change_pct:+.2f}%")
    
    report_lines.append(f"\n✅ 成功获取 {success}/{len(STOCKS)} 只股票数据")
    
    report_text = "\n".join(report_lines)
    
    # 打印到终端
    for line in report_lines:
        print(line)
    
    print("=" * 60)
    
    return report_text

# ============================================
# 主程序
# ============================================

def main():
    # 生成报告
    report = generate_report()
    
    # 推送到 Mattermost
    send_to_mattermost(report)

if __name__ == '__main__':
    main()
