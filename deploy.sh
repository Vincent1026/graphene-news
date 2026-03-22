#!/bin/bash
set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
LOG="$SCRIPT_DIR/fetch.log"
TODAY=$(date '+%Y-%m-%d')

echo "[$(date '+%Y-%m-%d %H:%M:%S')] === 石墨烯新闻采集任务 ===" | tee -a "$LOG"

cd "$SCRIPT_DIR"
git config user.name "Vincent1026" 2>/dev/null || true
git config user.email "2698877462@qq.com" 2>/dev/null || true

# Run the fetch script
python3 "$SCRIPT_DIR/fetch_news.py" 2>&1 | tee -a "$LOG"

# Check output
if [ -f index.html ] && [ -s index.html ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✓ HTML生成成功" | tee -a "$LOG"
else
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ❌ HTML生成失败!" | tee -a "$LOG"
    exit 1
fi

# Commit and push
git add index.html news_data.json 2>/dev/null
if git diff --cached --quiet; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] 没有新内容" | tee -a "$LOG"
else
    git commit -m "🤖 Auto-update: $TODAY 石墨烯新闻自动更新" 2>&1 | tee -a "$LOG"
    git push origin main 2>&1 | tee -a "$LOG"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✅ 推送成功!" | tee -a "$LOG"
fi
echo "" | tee -a "$LOG"
