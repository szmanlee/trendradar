#!/usr/bin/env python3
"""
美股深度分析脚本 - Finnhub 数据源
"""

import requests
import json
from datetime import datetime, timedelta

# ============================================
# 配置区
# ============================================

FINNHUB_API_KEY = "d6aqgspr01qqjvbre640d6aqgspr01qqjvbre64g"
MATTERMOST_WEBHOOK_URL = "http://192.168.32.220:8065/hooks/zxigmcyefjrgbxdcaj5xg3bata"

# 候选股票列表（增加行业分类）
STOCKS = {
    # 核心持仓 - 芯片/AI 巨头
    'NVDA': {'name': 'NVIDIA', 'sector': 'AI/芯片', 'weight': '核心'},
    'AAPL': {'name': 'Apple', 'sector': '消费电子', 'weight': '核心'},
    'MSFT': {'name': 'Microsoft', 'sector': '云计算', 'weight': '核心'},
    'GOOGL': {'name': 'Google', 'sector': '云计算/AI', 'weight': '核心'},
    'AMZN': {'name': 'Amazon', 'sector': '云计算', 'weight': '核心'},
    'META': {'name': 'Meta', 'sector': '社交/AI', 'weight': '核心'},
    'TSLA': {'name': 'Tesla', 'sector': '新能源车', 'weight': '核心'},
    'AMD': {'name': 'AMD', 'sector': 'AI/芯片', 'weight': '核心'},
    # 新兴AI
    'PLTR': {'name': 'Palantir', 'sector': '企业AI', 'weight': '高波动'},
    'SMCI': {'name': 'Super Micro', 'sector': 'AI服务器', 'weight': '高波动'},
    'SOUN': {'name': 'SoundHound AI', 'sector': '语音AI', 'weight': '高波动'},
    'AI': {'name': 'C3.ai', 'sector': '企业AI', 'weight': '高波动'},
    'PATH': {'name': 'UiPath', 'sector': 'RPA/AI', 'weight': '高波动'},
}

FINNHUB_BASE_URL = "https://finnhub.io/api/v1"

# ============================================
# 获取数据
# ============================================

def get_quote(symbol):
    """获取实时报价"""
    url = f"{FINNHUB_BASE_URL}/quote"
    params = {'symbol': symbol, 'token': FINNHUB_API_KEY}
    try:
        resp = requests.get(url, params=params, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            return {
                'c': data.get('c', 0),   # 当前价
                'd': data.get('d', 0),   # 变动
                'dp': data.get('dp', 0), # 变动%
                'h': data.get('h', 0),   # 最高
                'l': data.get('l', 0),   # 最低
                'o': data.get('o', 0),   # 开盘
                'pc': data.get('pc', 0), # 昨收
            }
    except:
        pass
    return None

def get_profile(symbol):
    """获取公司概况"""
    url = f"{FINNHUB_BASE_URL}/stock/profile2"
    params = {'symbol': symbol, 'token': FINNHUB_API_KEY}
    try:
        resp = requests.get(url, params=params, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            return {
                'country': data.get('country', ''),
                'exchange': data.get('exchange', ''),
                'finnhubIndustry': data.get('finnhubIndustry', ''),
                'weburl': data.get('weburl', ''),
            }
    except:
        pass
    return None

def get_recommendation(symbol):
    """获取分析师建议"""
    url = f"{FINNHUB_BASE_URL}/stock/recommendation"
    params = {'symbol': symbol, 'token': FINNHUB_API_KEY}
    try:
        resp = requests.get(url, params=params, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            if data:
                latest = data[0]
                return {
                    'buy': latest.get('buy', 0),
                    'hold': latest.get('hold', 0),
                    'sell': latest.get('sell', 0),
                    'strongBuy': latest.get('strongBuy', 0),
                    'strongSell': latest.get('strongSell', 0),
                    'period': latest.get('period', ''),
                }
    except:
        pass
    return None

def get_earnings(symbol):
    """获取下次财报日期"""
    url = f"{FINNHUB_BASE_URL}/calendar/earnings"
    params = {
        'symbol': symbol,
        'token': FINNHUB_API_KEY,
        'from': datetime.now().strftime('%Y-%m-%d'),  # 从今天开始
        'to': (datetime.now() + timedelta(days=90)).strftime('%Y-%m-%d')  # 未来90天
    }
    try:
        resp = requests.get(url, params=params, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            earnings = data.get('earningsCalendar', [])
            if earnings:
                next_earnings = earnings[0].get('date', '')
                return next_earnings
    except:
        pass
    return None

def get_news_sentiment(symbol):
    """获取新闻情绪"""
    url = f"{FINNHUB_BASE_URL}/company-news"
    params = {
        'symbol': symbol,
        'token': FINNHUB_API_KEY,
        'from': (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d'),
        'to': datetime.now().strftime('%Y-%m-%d')
    }
    try:
        resp = requests.get(url, params=params, timeout=10)
        if resp.status_code == 200:
            news = resp.json()
            # 简单计算正面/负面新闻数量
            positive = 0
            negative = 0
            for n in news[:10]:  # 只看最近10条
                headline = n.get('headline', '').lower()
                if any(w in headline for w in ['surge', 'jump', 'beat', 'gain', 'up', 'growth', 'profit']):
                    positive += 1
                elif any(w in headline for w in ['fall', 'drop', 'miss', 'loss', 'warning', 'cut']):
                    negative += 1
            return positive, negative
    except:
        pass
    return 0, 0

# ============================================
# 分析函数
# ============================================

def analyze_stock(symbol, info):
    """综合分析单只股票"""
    quote = get_quote(symbol)
    profile = get_profile(symbol)
    rec = get_recommendation(symbol)
    earnings = get_earnings(symbol)
    pos_news, neg_news = get_news_sentiment(symbol)
    
    if not quote or quote['c'] == 0:
        return None
    
    dp = quote['dp']
    
    # 简化的评分
    score = 50  # 基础分
    
    # 今日表现 (最高+25)
    if dp > 5:
        score += 25
    elif dp > 2:
        score += 15
    elif dp > 0:
        score += 10
    elif dp > -2:
        score += 5
    else:
        score -= 10
    
    # 分析师评级 (最高+25)
    if rec:
        total = rec['strongBuy'] + rec['buy'] + rec['hold'] + rec['sell'] + rec['strongSell']
        if total > 0:
            buy_ratio = (rec['strongBuy'] + rec['buy']) / total
            score += int(buy_ratio * 25)
    
    return {
        'symbol': symbol,
        'name': info['name'],
        'sector': info['sector'],
        'weight': info['weight'],
        'price': quote['c'],
        'change_pct': dp,
        'change': quote['d'],
        'high': quote['h'],
        'low': quote['l'],
        'score': min(100, max(0, score)),  # 限制在0-100
        'earnings': earnings,
        'rec': rec,
        'industry': profile.get('finnhubIndustry', '') if profile else '',
        'news_sentiment': (pos_news, neg_news),
    }

def generate_analysis():
    """生成深度分析报告"""
    results = []
    
    for symbol, info in STOCKS.items():
        analysis = analyze_stock(symbol, info)
        if analysis:
            results.append(analysis)
    
    # 按评分排序
    results.sort(key=lambda x: x['score'], reverse=True)
    
    # 生成报告
    report = []
    report.append(f"**📊 美股深度分析 - {datetime.now().strftime('%Y-%m-%d %H:%M')}**\n")
    
    # 强势推荐 - TOP 5
    report.append("## 🌟 综合评分 TOP 5\n")
    for i, r in enumerate(results[:5], 1):
        emoji = "🟢" if r['change_pct'] > 0 else "🔴"
        report.append(f"**{i}. {r['symbol']} {r['name']}** {emoji}")
        report.append(f"   评分: **{r['score']}/100** | 当前: ${r['price']:.2f} ({r['change_pct']:+.2f}%)")
        if r['rec']:
            rec = r['rec']
            report.append(f"   分析师: 🟢买{rec['strongBuy']+rec['buy']} | 🟡持{rec['hold']} | 🔴卖{rec['sell']+rec['strongSell']}")
        report.append("")
    
    # 核心持仓 vs 高波动
    report.append("## 📈 分类一览\n")
    
    report.append("**核心持仓:**")
    core = [r for r in results if r['weight'] == '核心']
    core_line = " | ".join([f"{r['symbol']}({r['change_pct']:+.1f}%)" for r in core])
    report.append(f"_{core_line}_\n")
    
    report.append("**高波动AI:**")
    volatile = [r for r in results if r['weight'] == '高波动']
    volatile_line = " | ".join([f"{r['symbol']}({r['change_pct']:+.1f}%)" for r in volatile])
    report.append(f"_{volatile_line}_\n")
    
    # 财报日历
    report.append("\n## 📅 财报日历 (未来90天)\n")
    with_earnings = [(r, r['earnings']) for r in results if r['earnings']]
    for r, date in sorted(with_earnings, key=lambda x: x[1])[:5]:
        days = (datetime.strptime(date, '%Y-%m-%d') - datetime.now()).days
        report.append(f"- **{r['symbol']}**: {date} ({days}天后)")
    
    # 行业分布
    report.append("\n## 🏭 行业分布\n")
    sectors = {}
    for r in results:
        sec = r['sector']
        if sec not in sectors:
            sectors[sec] = []
        sectors[sec].append(r['symbol'])
    for sec, symbols in sectors.items():
        report.append(f"- {sec}: {', '.join(symbols)}")
    
    report.append(f"\n_数据来源: Finnhub | 共分析 {len(results)} 只股票_")
    
    return "\n".join(report)

def send_to_mattermost(text):
    """发送消息到 Mattermost"""
    try:
        payload = {"text": text}
        resp = requests.post(MATTERMOST_WEBHOOK_URL, json=payload, timeout=10)
        return resp.status_code in [200, 201]
    except:
        return False

# ============================================
# 主程序
# ============================================

def main():
    print("正在获取深度分析数据...")
    report = generate_analysis()
    print("\n" + report)
    print("\n" + "="*60)
    if send_to_mattermost(report):
        print("✅ 已推送到 Mattermost")
    else:
        print("❌ Mattermost 推送失败")

if __name__ == '__main__':
    main()
