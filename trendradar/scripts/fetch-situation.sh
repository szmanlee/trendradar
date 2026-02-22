#!/bin/bash
# Situation Monitor 数据采集脚本
# 用于从 192.168.32.26:4173 获取数据并保存到文件供 Dashboard 显示
# 放到 gateway 服务器执行

DATA_URL="http://localhost:4173/"
OUTPUT_FILE="/root/.openclaw/workspace/trendradar/output/situation.json"
LOG_FILE="/var/log/situation-monitor.log"

# 创建输出目录（如果不存在）
mkdir -p "$(dirname "$OUTPUT_FILE")"

# 获取数据
echo "[$(date '+%Y-%m-%d %H:%M:%S')] 正在获取数据..." >> "$LOG_FILE"

RESPONSE=$(curl -s -m 10 "$DATA_URL" 2>/dev/null)

if [ -n "$RESPONSE" ]; then
    # 添加时间戳
    TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    
    # 如果返回的是数组，包装成对象格式
    if echo "$RESPONSE" | grep -q '^\['; then
        echo "{\"status\":\"ok\",\"timestamp\":\"$TIMESTAMP\",\"data\":$RESPONSE}" > "$OUTPUT_FILE"
    else
        echo "$RESPONSE" > "$OUTPUT_FILE"
    fi
    
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✅ 数据已更新 ($OUTPUT_FILE)" >> "$LOG_FILE"
else
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ❌ 获取数据失败" >> "$LOG_FILE"
fi

# 输出文件内容供调试
if [ -f "$OUTPUT_FILE" ]; then
    LINES=$(wc -l < "$OUTPUT_FILE")
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] 文件大小: $LINES 行" >> "$LOG_FILE"
fi
