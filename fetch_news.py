#!/usr/bin/env python3
"""
石墨烯新闻采集脚本 v2
采集来源:
1. https://www.graphene-info.com/ (英文→中文翻译)
2. http://www.graphene.tv/ (中文，直接使用)
3. Google News (可选，国内可能无法访问)

用法: python3 fetch_news_v2.py
"""

import requests
from bs4 import BeautifulSoup
import json
import re
import os
import sys
import html
import time
import random
from urllib.parse import urljoin, quote_plus

# ── 配置 ──────────────────────────────────────────────────────────────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__)) if '__file__' in dir() else os.getcwd()
OUTPUT_HTML    = os.path.join(SCRIPT_DIR, "index.html")
OUTPUT_JSON    = os.path.join(SCRIPT_DIR, "news_data.json")
TODAY_STR      = __import__("datetime").datetime.now().strftime("%Y-%m-%d")
TODAY_CN       = __import__("datetime").datetime.now().strftime("%Y年%m月%d日")
# 每日独立 HTML 目录 (按年/月组织: news/2026/04/)
NEWS_DIR       = os.path.join(SCRIPT_DIR, "news")
YEAR_MONTH_DIR = os.path.join(NEWS_DIR, 
    __import__("datetime").datetime.now().strftime("%Y/%m"))
DAILY_HTML     = os.path.join(YEAR_MONTH_DIR, f"{TODAY_STR}.html")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
}
SESSION = requests.Session()
SESSION.headers.update(HEADERS)
SESSION.timeout = 12

# ── 日志 ───────────────────────────────────────────────────────────────────────
def log(msg, level="INFO"):
    ts = __import__("datetime").datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] [{level}] {msg}", flush=True)

def err(msg):
    log(msg, "ERROR")

# ── 工具 ──────────────────────────────────────────────────────────────────────
def http_get(url, timeout=12, retries=2):
    """带超时和重试的GET请求"""
    for attempt in range(retries):
        try:
            r = SESSION.get(url, timeout=timeout, allow_redirects=True)
            r.raise_for_status()
            return r.text
        except Exception as e:
            log(f"  请求失败 ({attempt+1}/{retries}): {str(e)[:60]}")
            if attempt < retries - 1:
                time.sleep(random.uniform(1, 3))
    return None

def extract_content(url):
    """提取文章正文"""
    html_content = http_get(url)
    if not html_content:
        return None
    soup = BeautifulSoup(html_content, "html.parser")
    for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
        tag.decompose()
    article = soup.find("article") or soup.find("main")
    if article:
        text = article.get_text(separator="\n", strip=True)
    else:
        best_div, best_count = None, 0
        for div in soup.find_all("div"):
            count = len(div.find_all("p"))
            if count > best_count:
                best_count = count
                best_div = div
        text = best_div.get_text(separator="\n", strip=True) if best_div else ""
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text[:3000] if len(text) > 50 else None

# 石墨烯专业词典（用于API不可用时的备用翻译）
GRAPHENE_GLOSSARY = {
    "graphene": "石墨烯", "graphene-based": "石墨烯基", "graphene-enhanced": "石墨烯增强",
    "sensor": "传感器", "semiconductor": "半导体", "chip": "芯片",
    "battery": "电池", "anode": "阳极", "cathode": "阴极",
    "composite": "复合材料", "membrane": "膜", "polymer": "聚合物",
    "thermal": "导热", "flexible": "柔性", "nanotechnology": "纳米技术",
    "material": "材料", "researchers": "研究人员", "technology": "技术",
    "industry": "行业", "market": "市场", "production": "生产",
    "application": "应用", "development": "开发", "investment": "投资",
    "funding": "融资", "breakthrough": "突破", "performance": "性能",
    "efficiency": "效率", "energy": "能源", "electronic": "电子",
    "medical": "医疗", "healthcare": "医疗", "environmental": "环保",
    "collaboration": "合作", "partnership": "合作", "announced": "宣布",
    "announces": "宣布", "launches": "推出", "launched": "推出",
    "raises": "获得融资", "supercapacitor": "超级电容",
    "desalination": "海水淡化", "aircraft": "航空", "aerospace": "航空航天",
    "detection": "检测", "diagnostic": "诊断", "monitoring": "监测",
    "capacity": "产能", "expansion": "扩建", "expands": "扩建",
    "enhanced": "增强", "improved": "改进", "record": "创纪录",
    "commercial": "商业化", "mass production": "量产", "advanced": "先进",
    "novel": "新型", "solar": "太阳能", "biomedical": "生物医学",
    "automotive": "汽车", "electric vehicle": "电动汽车", "ev": "电动汽车",
    "coating": "涂层", "lightweight": "轻量化", "conductivity": "导电性",
    "photovoltaic": "光电", "transistor": "晶体管", "cancer": "癌症",
    "infrastructure": "基础设施", "health": "健康", "wearable": "可穿戴",
    "internet of things": "物联网", "receives": "获得", "receives": "获得",
    "companies": "公司", "carbon": "碳", "ultra": "超", "high": "高",
    "new": "新", "research": "研究", "study": "研究", "discovery": "发现",
    "Series B": "B轮", "equity round": "股权融资", "million": "百万美元",
    "billion": "十亿美元", "percent": "%", "partners with": "与...合作",
    "teams up with": "与...合作", "collaborates with": "与...合作",
    "enter MOU": "签署谅解备忘录", "prototype": "原型", "pilot": "试点",
    "commercialization": "商业化", "scale-up": "规模化扩大",
    "breakthrough": "突破", "revolutionary": "革命性",
}

def _glossary_translate(text):
    """词典辅助翻译"""
    if not text: return text
    result = text
    for eng, chn in sorted(GRAPHENE_GLOSSARY.items(), key=lambda x: -len(x[0])):
        result = re.sub(r"\b" + re.escape(eng) + r"\b", chn, result, flags=re.I)
    result = re.sub(r"\s+", " ", result).strip()
    return result

def translate(text, source_lang="en"):
    """翻译: 优先MyMemory API → 词典备用"""
    if not text or len(text.strip()) < 5:
        return text
    clean = re.sub(r"\s+", " ", text.strip())[:800]
    if not clean:
        return text
    import textwrap
    chunks = textwrap.wrap(clean, width=450) or [clean]
    results = []
    for chunk in chunks[:10]:
        try:
            url = f"https://api.mymemory.translated.net/get?q={quote_plus(chunk)}&langpair={source_lang}|zh-CN&languser=vincent_news_bot"
            resp = SESSION.get(url, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                if data.get("responseStatus") == 200:
                    translated = data["responseData"]["translatedText"]
                    if "MYMEMORY WARNING" not in translated:
                        results.append(translated)
                        time.sleep(0.35)
                        continue
        except:
            pass
        # Fallback: glossary + partial translate
        results.append(_glossary_translate(chunk))
        time.sleep(0.05)
    return "".join(results) if results else text

def tag_news(title, desc):
    """自动打标签"""
    text = f"{title} {desc}".lower()
    tags = []
    tag_map = [
        ("传感器", ["sensor", "detect", "monitor", "探测", "传感"]),
        ("医疗检测", ["medical", "health", "covid", "diagnostic", "病毒", "医疗"]),
        ("电池技术", ["battery", "energy storage", "lithium", "负极", "电池"]),
        ("超级电容", ["supercapacitor", "capacitor", "电容"]),
        ("海水淡化", ["desalination", "water", "membrane", "淡化", "过滤"]),
        ("航空航天", ["aircraft", "aerospace", "aviation", "航空"]),
        ("复合材料", ["composite", "reinforced", "polymer", "复合"]),
        ("柔性显示屏", ["flexible", "display", "screen", "oled", "柔性"]),
        ("散热技术", ["thermal", "heat", "cooling", "散热"]),
        ("电动汽车", ["electric vehicle", "ev", "automotive", "汽车"]),
        ("投资", ["investment", "funding", "million", "grant", "投资", "融资", "万英镑", "万美元"]),
        ("产能扩张", ["expansion", "production", "capacity", "产能", "扩建"]),
        ("中国", ["china", "chinese", "中国"]),
        ("欧盟项目", ["eu ", "european", "flagship", "欧盟"]),
        ("英国", ["uk", "britain", "england", "英国"]),
        ("可穿戴设备", ["wearable", "smartwatch", "可穿戴"]),
        ("芯片", ["chip", "semiconductor", "transistor", "芯片"]),
        ("环保技术", ["environmental", "eco", "green", "环保"]),
        ("运动用品", ["sports", "gaming", "headphone", "audio", "鞋", "耳机"]),
        ("物联网", ["iot", "internet of things", "物联网"]),
        ("基建", ["infrastructure", "bridge", "building", "基建"]),
        ("量产", ["mass production", "commercialization", "量产"]),
        ("科研进展", ["research", "study", "scientists", "discovery", "科研"]),
        ("行业资讯", ["industry", "market", "announce", "行业"]),
        ("电子产品", ["electronic", "device", "电子产品"]),
        ("石墨烯采暖", ["heating", "heating", "保暖", "采暖", "取暖"]),
        ("石墨烯材料", ["graphene", "material", "材料"]),
    ]
    for tag, kws in tag_map:
        for kw in kws:
            if kw in text:
                if tag not in tags:
                    tags.append(tag)
                break
    return tags[:5] if tags else ["行业资讯"]

def extract_articles_from_html(html_content, base_url, source_name, lang="en"):
    """从HTML中提取文章链接"""
    if not html_content:
        return []
    soup = BeautifulSoup(html_content, "html.parser")
    links = []
    skip_patterns = ["/category/", "/tag/", "/author/", "/page/", "/services",
                     "/contact", "/about", "/search", "facebook", "twitter",
                     "linkedin", "youtube", "/event/"]
    
    for a in soup.find_all("a", href=True):
        href = a["href"]
        text = a.get_text(strip=True)
        if len(text) < 25:
            continue
        full_url = urljoin(base_url, href)
        if any(p in full_url.lower() for p in skip_patterns):
            continue
        # 包含graphene或日期格式
        if "graphene" in full_url.lower() or "/20" in href:
            links.append((full_url, text))
    
    # 去重
    seen = set()
    unique = []
    for url, title in links:
        norm = url.split("?")[0].split("#")[0]
        if norm not in seen:
            seen.add(norm)
            unique.append({"url": url, "title": title, "lang": lang})
    return unique

# ── 采集器 ────────────────────────────────────────────────────────────────────
def fetch_graphene_info():
    log("📡 采集 graphene-info.com (英文→中文)...")
    url = "https://www.graphene-info.com/"
    html_content = http_get(url, timeout=15)
    if not html_content:
        err("graphene-info.com 采集失败")
        return []
    
    articles_raw = extract_articles_from_html(html_content, url, "Graphene-Info", "en")
    log(f"  发现 {len(articles_raw)} 个链接")
    
    results = []
    for i, art in enumerate(articles_raw[:15]):
        log(f"  抓取 [{i+1}/{min(len(articles_raw),15)}]: {art['title'][:40]}", "INFO")
        content = extract_content(art["url"])
        time.sleep(random.uniform(0.3, 1.0))
        results.append({
            "title": html.unescape(art["title"]),
            "url": art["url"],
            "content": content,
            "source": "Graphene-Info",
            "lang": "en",
        })
    
    log(f"  ✓ 采集完成: {len(results)} 篇")
    return results

def fetch_graphene_tv():
    log("📡 采集 graphene.tv (中文内容)...")
    url = "http://www.graphene.tv/"
    html_content = http_get(url, timeout=15)
    if not html_content:
        err("graphene.tv 采集失败")
        return []
    
    articles_raw = extract_articles_from_html(html_content, url, "Graphene.tv", "zh")
    log(f"  发现 {len(articles_raw)} 个链接")
    
    results = []
    for i, art in enumerate(articles_raw[:15]):
        log(f"  抓取 [{i+1}/{min(len(articles_raw),15)}]: {art['title'][:40]}", "INFO")
        content = extract_content(art["url"])
        time.sleep(random.uniform(0.3, 1.0))
        results.append({
            "title": html.unescape(art["title"]),
            "url": art["url"],
            "content": content,
            "source": "Graphene.tv",
            "lang": "zh",
        })
    
    log(f"  ✓ 采集完成: {len(results)} 篇")
    return results

def fetch_google_news():
    """Google News - 需要浏览器配合 VPN（用户手动开启时使用）"""
    log("📡 尝试 Google News...")
    try:
        # 首先尝试直接访问（无 VPN 时会失败）
        url = "https://news.google.com/rss/search?q=graphene&hl=zh-CN&gl=CN&ceid=CN:zh-CN"
        from xml.etree import ElementTree as ET
        content = http_get(url, timeout=10)
        
        if content and "<?xml" in content[:50]:
            root = ET.fromstring(content)
            articles = []
            for item in root.findall(".//item")[:10]:
                title = item.findtext("title", "")
                link = item.findtext("link", "")
                if title and link:
                    articles.append({
                        "title": html.unescape(title),
                        "url": link,
                        "content": None,
                        "source": "Google News",
                        "lang": "en",
                    })
            if articles:
                log(f"  ✓ 通过 RSS 采集到 {len(articles)} 篇")
                return articles
        
        raise Exception("无法直接访问，需要 VPN")
        
    except Exception as e:
        log(f"  ⚠ Google News 需要浏览器 VPN（{str(e)[:40]}），跳过")
        # 自动使用 ProSearch 补充
        return fetch_prosearch_backup()

def fetch_prosearch_backup():
    """ProSearch 备用方案 - 当 Google News 不可用时补充新闻"""
    log("  📡 使用 ProSearch 补充...")
    try:
        import subprocess
        import json as json_mod
        
        port = os.environ.get("AUTH_GATEWAY_PORT", "19000")
        import time as time_mod
        from_time = int(time_mod.time()) - 604800
        
        cmd = [
            "curl", "-s", "-X", "POST",
            f"http://localhost:{port}/proxy/prosearch/search",
            "-H", "Content-Type: application/json",
            "-d", json_mod.dumps({
                "keyword": "graphene",
                "from_time": from_time,
                "industry": "news"
            })
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        if result.returncode != 0:
            return []
        
        data = json_mod.loads(result.stdout)
        if not data.get("success"):
            return []
        
        docs = data.get("data", {}).get("docs", [])
        articles = []
        for doc in docs[:5]:  # 补充少量
            title = doc.get("title", "")
            url = doc.get("url", "")
            passage = doc.get("passage", "")
            if title and url:
                articles.append({
                    "title": html.unescape(title),
                    "url": url,
                    "content": passage[:300] if passage else None,
                    "source": "ProSearch",
                    "lang": "en",
                })
        
        if articles:
            log(f"  ✓ ProSearch 补充 {len(articles)} 篇")
        return articles
    except:
        return []

# ── 处理 ──────────────────────────────────────────────────────────────────────
def process_article(art):
    """翻译并处理单篇文章"""
    title = art.get("title", "")
    content = art.get("content", "")
    lang = art.get("lang", "en")
    source = art.get("source", "Unknown")
    url = art.get("url", "")
    
    # 翻译（仅英文内容需要翻译）
    if lang == "en":
        title_cn = translate(title)
        time.sleep(0.3)
        desc = content[:300].split("\n")[0].strip() if content else ""
        if desc and len(desc) > 20:
            desc_cn = translate(desc)
        else:
            desc_cn = title_cn
        content_cn = translate(content) if content and len(content) > 50 else None
    else:
        # 中文内容直接使用
        title_cn = title
        desc_cn = content[:200].split("\n")[0].strip() if content else title[:200]
        content_cn = content if content and len(content) > 50 else None
    
    tags = tag_news(title_cn, desc_cn)
    return {
        "title": title_cn,
        "description": desc_cn[:200] + "..." if len(desc_cn) > 200 else desc_cn,
        "content": content_cn,
        "source": source,
        "url": url,
        "date": TODAY_STR,
        "tags": tags,
        "original_title": title if lang == "en" else None,
    }

# ── HTML生成 ──────────────────────────────────────────────────────────────────
def generate_html(news_items, standalone=False):
    """生成 HTML 页面
    Args:
        news_items: 新闻列表
        standalone: 是否为独立页面（每日归档），独立页面会添加返回首页链接
    """
    all_tags = sorted({t for item in news_items for t in item.get("tags", [])})
    filter_btns = '<button class="filter-btn active" data-tag="all">全部</button>'
    for tag in all_tags:
        filter_btns += f'<button class="filter-btn" data-tag="{html.escape(tag)}">{html.escape(tag)}</button>'
    
    timeline_html = ""
    for item in news_items:
        tags_html = "".join(f'<span class="news-tag">{html.escape(t)}</span>' for t in item.get("tags", []))
        content_html = ""
        if item.get("content"):
            content_html = f'<p class="news-desc">{html.escape(item["description"])}</p>'
            expand_btn = f'<button class="expand-btn" onclick="toggleContent(this)">展开详情 ▼</button><div class="news-full-content" style="display:none">{html.escape(item["content"] or "").replace(chr(10), "<br>")}</div>'
        else:
            expand_btn = ""
        
        timeline_html += f'''
        <div class="timeline-item" data-tags="{",".join(html.escape(t) for t in item.get("tags", []))}">
            <span class="timeline-date">{TODAY_STR}</span>
            <div class="timeline-content">
                <span class="news-source">{html.escape(item.get("source", ""))}</span>
                <div class="news-tags">{tags_html}</div>
                <h3 class="news-title">{html.escape(item["title"])}</h3>
                {content_html}
                <a href="{html.escape(item["url"])}" target="_blank" class="news-link">阅读原文 →</a>
                {expand_btn}
            </div>
        </div>'''
    
    return f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>石墨烯新闻 - {TODAY_CN}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Microsoft YaHei", sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            min-height: 100vh; padding: 20px;
        }}
        .container {{ max-width: 900px; margin: 0 auto; }}
        header {{ text-align: center; padding: 40px 0; color: #fff; }}
        h1 {{ font-size: 2.5em; margin-bottom: 10px;
            background: linear-gradient(90deg, #00d2ff, #3a7bd5);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; }}
        .subtitle {{ font-size: 1.1em; color: #8ba4c7; margin-bottom: 5px; }}
        .update-info {{ font-size: 0.85em; color: #5a7a9a; margin-top: 5px; }}
        .stats {{ display: flex; justify-content: center; gap: 30px; margin: 20px 0 40px; }}
        .stat-item {{ background: rgba(255,255,255,0.1); padding: 15px 30px; border-radius: 10px; color: #fff; }}
        .stat-number {{ font-size: 2em; font-weight: bold; color: #00d2ff; }}
        .stat-label {{ font-size: 0.9em; color: #8ba4c7; }}
        .filter-section {{ background: rgba(255,255,255,0.1); border-radius: 15px; padding: 20px; margin: 20px 0; }}
        .filter-title {{ color: #fff; font-size: 1.1em; margin-bottom: 15px; display: flex; align-items: center; gap: 8px; }}
        .filter-tags {{ display: flex; flex-wrap: wrap; gap: 10px; }}
        .filter-btn {{
            background: rgba(255,255,255,0.15); border: 1px solid rgba(255,255,255,0.2);
            color: #fff; padding: 8px 16px; border-radius: 20px; cursor: pointer;
            transition: all 0.3s; font-size: 0.9em;
        }}
        .filter-btn:hover {{ background: rgba(0,210,255,0.3); border-color: #00d2ff; }}
        .filter-btn.active {{ background: linear-gradient(90deg, #00d2ff, #3a7bd5); border-color: #00d2ff; font-weight: bold; }}
        .no-results {{ text-align: center; color: #8ba4c7; padding: 60px 20px; font-size: 1.2em; display: none; }}
        .timeline {{ position: relative; padding: 20px 0; }}
        .timeline::before {{ content: ''; position: absolute; left: 50%; transform: translateX(-50%); width: 4px; height: 100%; background: linear-gradient(180deg, #00d2ff, #3a7bd5); border-radius: 2px; }}
        .timeline-item {{ position: relative; width: 50%; padding: 0 30px 40px; box-sizing: border-box; }}
        .timeline-item:nth-child(odd) {{ left: 0; text-align: right; }}
        .timeline-item:nth-child(even) {{ left: 50%; text-align: left; }}
        .timeline-item::before {{ content: ''; position: absolute; top: 0; width: 20px; height: 20px; background: #00d2ff; border-radius: 50%; border: 4px solid #fff; box-shadow: 0 0 10px rgba(0,210,255,0.5); }}
        .timeline-item:nth-child(odd)::before {{ right: -12px; }}
        .timeline-item:nth-child(even)::before {{ left: -12px; }}
        .timeline-date {{ display: inline-block; background: linear-gradient(90deg, #00d2ff, #3a7bd5); color: #fff; padding: 5px 15px; border-radius: 15px; font-size: 0.85em; margin-bottom: 10px; font-weight: bold; }}
        .timeline-item:nth-child(odd) .timeline-date {{ margin-right: 10px; }}
        .timeline-item:nth-child(even) .timeline-date {{ margin-left: 10px; }}
        .timeline-content {{ background: rgba(255,255,255,0.95); border-radius: 15px; padding: 20px; box-shadow: 0 5px 20px rgba(0,0,0,0.2); transition: transform 0.3s, box-shadow 0.3s; }}
        .timeline-content:hover {{ transform: translateY(-5px); box-shadow: 0 10px 30px rgba(0,210,255,0.3); }}
        .news-source {{ background: linear-gradient(90deg, #00d2ff, #3a7bd5); color: white; padding: 5px 12px; font-size: 0.8em; display: inline-block; border-radius: 10px; margin-bottom: 10px; }}
        .news-title {{ font-size: 1.15em; color: #1a1a2e; margin-bottom: 10px; line-height: 1.4; font-weight: 600; }}
        .news-desc {{ color: #666; font-size: 0.95em; line-height: 1.6; margin-bottom: 15px; }}
        .news-tags {{ display: flex; flex-wrap: wrap; gap: 5px; margin-bottom: 10px; }}
        .timeline-item:nth-child(odd) .news-tags {{ justify-content: flex-end; }}
        .timeline-item:nth-child(even) .news-tags {{ justify-content: flex-start; }}
        .news-tag {{ background: #e8f4fc; color: #3a7bd5; padding: 3px 8px; border-radius: 10px; font-size: 0.75em; }}
        .news-link {{ color: #3a7bd5; text-decoration: none; font-weight: 500; font-size: 0.9em; }}
        .news-link:hover {{ text-decoration: underline; }}
        .expand-btn {{ background: #f0f4f8; border: none; color: #3a7bd5; padding: 4px 12px; border-radius: 8px; cursor: pointer; font-size: 0.8em; margin-top: 8px; }}
        .expand-btn:hover {{ background: #e0e8f0; }}
        .news-full-content {{ margin-top: 12px; padding: 12px; background: #f8fafc; border-radius: 8px; color: #333; font-size: 0.9em; line-height: 1.7; text-align: left; border-left: 3px solid #00d2ff; max-height: 300px; overflow-y: auto; }}
        .timeline-item.hidden {{ display: none; }}
        footer {{ text-align: center; padding: 40px 0; color: #8ba4c7; border-top: 1px solid rgba(255,255,255,0.1); margin-top: 40px; }}
        footer a {{ color: #00d2ff; text-decoration: none; }}
        footer a:hover {{ text-decoration: underline; }}
        @media (max-width: 768px) {{
            .timeline::before {{ left: 20px; }}
            .timeline-item {{ width: 100%; padding-left: 50px; padding-right: 15px; text-align: left !important; }}
            .timeline-item::before {{ left: 11px !important; right: auto !important; }}
            .timeline-item:nth-child(odd) .timeline-date, .timeline-item:nth-child(even) .timeline-date {{ margin: 0; }}
            .timeline-item:nth-child(odd) .news-tags, .timeline-item:nth-child(even) .news-tags {{ justify-content: flex-start; }}
            h1 {{ font-size: 1.8em; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🔬 石墨烯新闻</h1>
            <p class="subtitle">{TODAY_CN} 全球石墨烯行业动态</p>
            <p class="update-info">🤖 自动采集于 {__import__("datetime").datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
            <div class="stats">
                <div class="stat-item"><div class="stat-number" id="totalCount">{len(news_items)}</div><div class="stat-label">新闻数量</div></div>
                <div class="stat-item"><div class="stat-number" id="filteredCount">{len(news_items)}</div><div class="stat-label">显示数量</div></div>
                <div class="stat-item"><div class="stat-number" id="sourceCount">{len(set(i.get("source","") for i in news_items))}</div><div class="stat-label">新闻来源</div></div>
            </div>
        </header>
        <div class="filter-section">
            <div class="filter-title"><span>🏷️</span><span>按标签筛选:</span></div>
            <div class="filter-tags">{filter_btns}</div>
        </div>
        <div class="no-results" id="noResults">没有找到匹配的新闻</div>
        <div class="timeline" id="timeline">{timeline_html}</div>
        <footer>
            <p>📡 数据来源: Graphene-Info | Graphene.tv | Google News</p>
            <p>🔗 GitHub: <a href="https://github.com/Vincent1026/graphene-news" target="_blank">Vincent1026/graphene-news</a></p>
            {'<p>🏠 <a href="../../index.html">返回首页</a> | <a href="../">查看归档目录</a></p>' if standalone else ''}
            <p>🤖 自动更新于 {__import__("datetime").datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
        </footer>
    </div>
    <script>
        function toggleContent(btn) {{
            const c = btn.nextElementSibling;
            c.style.display = c.style.display === 'none' ? 'block' : 'none';
            btn.textContent = c.style.display === 'none' ? '展开详情 ▼' : '收起详情 ▲';
        }}
        const filterBtns = document.querySelectorAll('.filter-btn');
        const timelineItems = document.querySelectorAll('.timeline-item');
        const totalCount = document.getElementById('totalCount');
        const filteredCount = document.getElementById('filteredCount');
        const noResults = document.getElementById('noResults');
        filterBtns.forEach(btn => {{
            btn.addEventListener('click', () => {{
                const tag = btn.dataset.tag;
                filterBtns.forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                let visibleCount = 0;
                timelineItems.forEach(item => {{
                    const itemTags = item.dataset.tags.split(',');
                    if (tag === 'all' || itemTags.includes(tag)) {{
                        item.classList.remove('hidden');
                        visibleCount++;
                    }} else {{
                        item.classList.add('hidden');
                    }}
                }});
                filteredCount.textContent = visibleCount;
                noResults.style.display = visibleCount === 0 ? 'block' : 'none';
            }});
        }});
    </script>
</body>
</html>'''

# ── 主程序 ────────────────────────────────────────────────────────────────────
def main():
    log("=" * 60)
    log("🤖 石墨烯新闻采集器 v2 启动")
    log(f"📅 日期: {TODAY_STR}")
    log("=" * 60)
    
    all_articles = []
    
    # 1. graphene-info.com (英文)
    try:
        articles1 = fetch_graphene_info()
        all_articles.extend(articles1)
    except Exception as e:
        err(f"graphene-info 异常: {e}")
    time.sleep(random.uniform(1, 2))
    
    # 2. graphene.tv (中文，直接用)
    try:
        articles2 = fetch_graphene_tv()
        all_articles.extend(articles2)
    except Exception as e:
        err(f"graphene.tv 异常: {e}")
    time.sleep(random.uniform(1, 2))
    
    # 3. Google News (可选)
    try:
        articles3 = fetch_google_news()
        all_articles.extend(articles3)
    except Exception as e:
        err(f"Google News 异常: {e}")
    
    log(f"\n原始文章总数: {len(all_articles)} 篇")
    
    # 去重
    seen = set()
    unique = []
    for art in all_articles:
        norm = art["url"].split("?")[0].split("#")[0]
        if norm not in seen and len(art.get("title", "")) > 10:
            seen.add(norm)
            unique.append(art)
    log(f"去重后: {len(unique)} 篇")
    
    # 处理（翻译）- 确保至少10条新闻
    processed = []
    max_process = max(25, len(unique))  # 处理所有文章，至少25篇
    for i, art in enumerate(unique[:max_process]):
        log(f"\n处理 [{i+1}/{min(len(unique),max_process)}]: {art['title'][:45]}")
        try:
            item = process_article(art)
            processed.append(item)
            log(f"  ✓ {item['title'][:40]}")
        except Exception as e:
            err(f"  处理失败: {e}")
        time.sleep(random.uniform(0.5, 1.5))
    
    # 确保至少10条新闻
    if len(processed) < 10:
        log(f"⚠ 当前只有 {len(processed)} 条新闻，尝试补充...")
    
    log(f"\n处理完成，共 {len(processed)} 篇中文新闻")
    
    # 生成主 HTML
    log("生成 HTML 页面...")
    html_content = generate_html(processed)
    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write(html_content)
    log(f"✓ HTML 已保存 ({len(html_content)//1024} KB)")
    
    # 生成每日独立 HTML 文件 (news/2026/04/YYYY-MM-DD.html)
    log("生成每日独立 HTML 文件...")
    os.makedirs(YEAR_MONTH_DIR, exist_ok=True)
    daily_html_content = generate_html(processed)
    with open(DAILY_HTML, "w", encoding="utf-8") as f:
        f.write(daily_html_content)
    log(f"✓ 每日 HTML 已保存: news/{__import__('datetime').datetime.now().strftime('%Y/%m')}/{TODAY_STR}.html")
    
    # 生成 JSON
    log("生成 JSON 数据...")
    historical = []
    if os.path.exists(OUTPUT_JSON):
        try:
            with open(OUTPUT_JSON, "r", encoding="utf-8") as f:
                historical = json.load(f)
        except:
            historical = []
    
    existing_dates = {item.get("date") for item in historical}
    all_news = [n for n in processed if n.get("date") not in existing_dates] + historical
    
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(all_news, f, ensure_ascii=False, indent=2)
    log(f"✓ JSON 已保存 (共 {len(all_news)} 篇)")
    
    # 生成每日独立 HTML 文件
    log("生成每日独立 HTML...")
    try:
        # 确保目录存在 (news/2026/04/)
        os.makedirs(YEAR_MONTH_DIR, exist_ok=True)
        
        # 生成当日 HTML
        daily_html_content = generate_html(processed)
        with open(DAILY_HTML, "w", encoding="utf-8") as f:
            f.write(daily_html_content)
        log(f"✓ 每日 HTML 已保存: news/{__import__('datetime').datetime.now().strftime('%Y/%m')}/{TODAY_STR}.html")
    except Exception as e:
        err(f"每日 HTML 生成失败: {e}")
    
    # 摘要
    log(f"\n📊 采集摘要:")
    log(f"  日期: {TODAY_STR}")
    log(f"  处理完成: {len(processed)} 篇")
    source_stats = {}
    for item in processed:
        src = item.get("source", "Unknown")
        source_stats[src] = source_stats.get(src, 0) + 1
    for src, count in sorted(source_stats.items(), key=lambda x: -x[1]):
        log(f"    {src}: {count} 篇")
    log("=" * 60)
    log("✅ 全部完成！")
    log("=" * 60)

if __name__ == "__main__":
    main()
