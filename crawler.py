#!/usr/bin/env python3
"""
石墨烯新闻爬虫脚本
自动爬取三个来源的最新石墨烯新闻，翻译为中文，按日期存储HTML

用法: python3 crawler.py

来源:
1. https://www.graphene-info.com/
2. http://www.graphene.tv/
3. Google News (石墨烯搜索)
"""

import requests
from bs4 import BeautifulSoup
import json
import re
import os
import html
import time
import random
from urllib.parse import urljoin, quote_plus
from datetime import datetime

# ── 配置 ──────────────────────────────────────────────────────────────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "news")
DATA_FILE = os.path.join(SCRIPT_DIR, "news_data.json")

# 创建输出目录
os.makedirs(os.path.join(OUTPUT_DIR, "daily"), exist_ok=True)

# 当前日期
TODAY = datetime.now()
TODAY_STR = TODAY.strftime("%Y-%m-%d")
TODAY_CN = TODAY.strftime("%Y年%m月%d日")
TODAY_FILE = os.path.join(OUTPUT_DIR, "daily", f"{TODAY_STR.replace('-','')}.html")

# HTTP 配置
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Accept-Encoding": "gzip, deflate",
    "Connection": "keep-alive",
}

SESSION = requests.Session()
SESSION.headers.update(HEADERS)
SESSION.timeout = 15

# VPN 代理配置 (WestWorldSS Trojan)
VPN_PROXY = "socks5h://127.0.0.1:10886"
if VPN_PROXY:
    SESSION.proxies = {
        "http": VPN_PROXY,
        "https": VPN_PROXY,
    }
    print(f"[INFO] VPN 代理已启用: {VPN_PROXY}")

# ── 石墨烯专业词典（翻译用）──────────────────────────────────────────────────
GLOSSARY = {
    "graphene": "石墨烯",
    "graphene-based": "石墨烯基",
    "graphene-enhanced": "石墨烯增强",
    "battery": "电池",
    "anode": "阳极",
    "cathode": "阴极",
    "semiconductor": "半导体",
    "sensor": "传感器",
    "chip": "芯片",
    "composite": "复合材料",
    "membrane": "膜",
    "thermal": "导热",
    "flexible": "柔性",
    "nanoparticle": "纳米颗粒",
    "nanotube": "纳米管",
    "oxide": "氧化物",
    "conductive": "导电",
    "electrode": "电极",
    "lithium": "锂",
    "silicon": "硅",
    "polymer": "聚合物",
    "coating": "涂层",
    "supercapacitor": "超级电容",
    "energy storage": "储能",
    "electric vehicle": "电动汽车",
    "wearable": "可穿戴",
    "medical": "医疗",
    "aerospace": "航空航天",
    "automotive": "汽车",
    "additive manufacturing": "增材制造",
    "3D printing": "3D打印",
    "researchers": "研究人员",
    "scientists": "科学家",
    "breakthrough": "突破",
    "discovery": "发现",
    "announces": "宣布",
    "launches": "推出",
    "raises": "获得融资",
    "investment": "投资",
    "funding": "融资",
    "million": "百万",
    "billion": "十亿",
    "collaboration": "合作",
    "partnership": "合作伙伴关系",
}

def log(msg, level="INFO"):
    """日志输出"""
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] [{level}] {msg}", flush=True)

def http_get(url, timeout=15, retries=2):
    """HTTP GET 请求"""
    for attempt in range(retries):
        try:
            r = SESSION.get(url, timeout=timeout, allow_redirects=True)
            r.raise_for_status()
            return r.text
        except Exception as e:
            log(f"请求失败 ({attempt+1}/{retries}): {str(e)[:80]}", "WARN")
            if attempt < retries - 1:
                time.sleep(random.uniform(1, 3))
    return None

def translate_text(text, source_lang="en"):
    """
    翻译文本 (使用 MyMemory API)
    如果 API 不可用，使用词典辅助翻译
    """
    if not text or len(text.strip()) < 3:
        return text
    
    # 检测是否已经是中文
    zh_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
    if zh_chars > len(text) * 0.3:
        return text  # 已经是中文
    
    clean = re.sub(r"\s+", " ", text.strip())[:800]
    
    # 尝试 MyMemory API
    try:
        encoded = quote_plus(clean)
        api_url = f"https://api.mymemory.translated.net/get?q={encoded}&langpair={source_lang}|zh-CN"
        resp = SESSION.get(api_url, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            if data.get("responseStatus") == 200:
                translated = data["responseData"]["translatedText"]
                if "MYMEMORY WARNING" not in translated:
                    return translated
    except:
        pass
    
    # 备用：词典翻译
    return glossary_translate(text)

def glossary_translate(text):
    """基于词典的翻译"""
    if not text:
        return text
    result = text
    for eng, chn in sorted(GLOSSARY.items(), key=lambda x: -len(x[0])):
        result = re.sub(r'\b' + re.escape(eng) + r'\b', chn, result, flags=re.I)
    return result

def extract_content(url):
    """提取文章正文内容"""
    html_content = http_get(url)
    if not html_content:
        return None
    
    soup = BeautifulSoup(html_content, "html.parser")
    
    # 移除无关标签
    for tag in soup(["script", "style", "nav", "footer", "header", "aside", "iframe", "advertisement"]):
        tag.decompose()
    
    # 尝试多种方式提取内容
    content = ""
    
    # 方式1: article 标签
    article = soup.find("article") or soup.find("main")
    if article:
        content = article.get_text(separator="\n", strip=True)
    
    # 方式2: 特定 class
    if not content or len(content) < 100:
        for cls in ["article-content", "post-content", "entry-content", "content", "article-body"]:
            elem = soup.find(class_=re.compile(cls, re.I))
            if elem:
                content = elem.get_text(separator="\n", strip=True)
                break
    
    # 方式3: 找最多段落的 div
    if not content or len(content) < 100:
        best_div, max_p = None, 0
        for div in soup.find_all("div"):
            p_count = len(div.find_all("p"))
            if p_count > max_p:
                max_p = p_count
                best_div = div
        if best_div and max_p > 2:
            content = best_div.get_text(separator="\n", strip=True)
    
    # 清理内容
    if content:
        content = re.sub(r"\n{3,}", "\n\n", content)
        content = content[:3000]  # 限制长度
    
    return content if content and len(content) > 50 else None

def auto_tag(title, description):
    """自动生成标签"""
    text = f"{title} {description}".lower()
    tags = []
    
    tag_rules = [
        ("电池技术", ["battery", "anode", "cathode", "lithium", "储能", "电池"]),
        ("传感器", ["sensor", "detect", "monitor", "传感", "检测"]),
        ("半导体/芯片", ["semiconductor", "chip", "transistor", "半导体", "芯片"]),
        ("复合材料", ["composite", "reinforced", "polymer", "复合", "增强"]),
        ("散热技术", ["thermal", "heat", "cooling", "散热", "导热"]),
        ("柔性电子", ["flexible", "wearable", "柔性", "可穿戴"]),
        ("医疗应用", ["medical", "health", "bio", "医疗", "生物"]),
        ("航空航天", ["aerospace", "aircraft", "aviation", "航空", "航天"]),
        ("汽车应用", ["automotive", "vehicle", "electric vehicle", "汽车", "电动车"]),
        ("环保技术", ["environmental", "water", "filtration", "环保", "净化"]),
        ("投资/融资", ["investment", "funding", "raises", "million", "billion", "投资", "融资", "万"]),
        ("产能扩张", ["expansion", "production", "capacity", "产能", "扩建"]),
        ("科研进展", ["research", "study", "discovery", "breakthrough", "研究", "发现", "突破"]),
        ("专利技术", ["patent", "专利", "发明"]),
        ("行业资讯", ["industry", "market", "announce", "行业", "市场", "发布"]),
    ]
    
    for tag, keywords in tag_rules:
        for kw in keywords:
            if kw in text:
                if tag not in tags:
                    tags.append(tag)
                break
    
    return tags[:5] if tags else ["行业资讯"]

def find_articles_graphene_info():
    """从 graphene-info.com 提取文章"""
    log("爬取 graphene-info.com...")
    url = "https://www.graphene-info.com/"
    html_content = http_get(url)
    
    if not html_content:
        log("graphene-info.com 爬取失败", "ERROR")
        return []
    
    soup = BeautifulSoup(html_content, "html.parser")
    articles = []
    
    # 提取文章链接
    seen_urls = set()
    skip_patterns = ["/category/", "/tag/", "/author/", "/page/", "/services", 
                     "/contact", "/about", "/search", "facebook", "twitter", "linkedin"]
    
    for a in soup.find_all("a", href=True):
        href = a["href"]
        text = a.get_text(strip=True)
        
        if len(text) < 25:
            continue
        
        full_url = urljoin(url, href)
        
        # 跳过无关链接
        if any(p in full_url.lower() for p in skip_patterns):
            continue
        
        # 只要包含 graphene 或日期的文章
        if "graphene" in full_url.lower() or ("/20" in href and "graphene-info" in full_url):
            norm_url = full_url.split("?")[0].split("#")[0]
            if norm_url not in seen_urls:
                seen_urls.add(norm_url)
                articles.append({
                    "url": full_url,
                    "title": html.unescape(text),
                    "source": "Graphene-Info",
                    "lang": "en"
                })
    
    log(f"发现 {len(articles)} 篇文章")
    return articles[:15]  # 限制数量

def find_articles_graphene_tv():
    """从 graphene.tv 提取文章"""
    log("爬取 graphene.tv...")
    url = "http://www.graphene.tv/"
    html_content = http_get(url)
    
    if not html_content:
        log("graphene.tv 爬取失败", "ERROR")
        return []
    
    soup = BeautifulSoup(html_content, "html.parser")
    articles = []
    
    seen_urls = set()
    for a in soup.find_all("a", href=True):
        href = a["href"]
        text = a.get_text(strip=True)
        
        if len(text) < 25:
            continue
        
        full_url = urljoin(url, href)
        norm_url = full_url.split("?")[0].split("#")[0]
        
        if norm_url not in seen_urls:
            seen_urls.add(norm_url)
            # graphene.tv 是中文站
            lang = "zh" if any('\u4e00' <= c <= '\u9fff' for c in text) else "en"
            articles.append({
                "url": full_url,
                "title": html.unescape(text),
                "source": "Graphene.tv",
                "lang": lang
            })
    
    log(f"发现 {len(articles)} 篇文章")
    return articles[:15]

def find_articles_google_news():
    """从 Google News RSS 提取文章"""
    log("爬取 Google News RSS...")
    
    try:
        from xml.etree import ElementTree as ET
        url = "https://news.google.com/rss/search?q=graphene&hl=en&gl=US&ceid=US:en"
        content = http_get(url)
        
        if not content:
            log("Google News 爬取失败", "WARN")
            return []
        
        root = ET.fromstring(content)
        articles = []
        
        for item in root.findall(".//item")[:10]:
            title = html.unescape(item.findtext("title", ""))
            link = item.findtext("link", "")
            if title and link:
                articles.append({
                    "url": link,
                    "title": title,
                    "source": "Google News",
                    "lang": "en"
                })
        
        log(f"发现 {len(articles)} 篇文章")
        return articles
    except Exception as e:
        log(f"Google News 解析失败: {str(e)[:60]}", "WARN")
        return []

def process_article(article):
    """处理单篇文章：抓取内容、翻译、打标签"""
    url = article["url"]
    title = article["title"]
    source = article["source"]
    lang = article.get("lang", "en")
    
    log(f"处理: {title[:45]}...")
    
    # 抓取正文
    content = extract_content(url)
    time.sleep(random.uniform(0.3, 0.8))
    
    # 翻译
    if lang == "en":
        title_cn = translate_text(title)
        desc = (content or "")[:200].split("\n")[0].strip() if content else ""
        desc_cn = translate_text(desc) if desc else title_cn
        content_cn = translate_text(content) if content and len(content) > 50 else None
    else:
        # 中文直接使用
        title_cn = title
        desc_cn = (content or "")[:200].split("\n")[0].strip() if content else title[:200]
        content_cn = content
    
    # 自动打标签
    tags = auto_tag(title_cn, desc_cn)
    
    return {
        "title": title_cn,
        "description": desc_cn[:200] + "..." if len(desc_cn) > 200 else desc_cn,
        "content": content_cn,
        "url": url,
        "source": source,
        "date": TODAY_STR,
        "tags": tags,
        "original_title": title if lang == "en" else None,
    }

def generate_html(articles, output_file):
    """生成 HTML 页面"""
    all_tags = sorted({t for a in articles for t in a.get('tags', [])})
    
    filter_btns = '<button class="filter-btn active" data-tag="all">全部</button>'
    for tag in all_tags:
        filter_btns += f'<button class="filter-btn" data-tag="{html.escape(tag)}">{html.escape(tag)}</button>'
    
    timeline = ""
    for item in articles:
        tags_html = "".join(f'<span class="news-tag">{html.escape(t)}</span>' for t in item.get('tags', []))
        
        if item.get('content'):
            content_html = f'<p class="news-desc">{html.escape(item["description"])}</p>'
            expand_btn = f'<button class="expand-btn" onclick="toggleContent(this)">展开详情</button><div class="news-full-content" style="display:none">{html.escape(item["content"]).replace(chr(10), "<br>")}</div>'
        else:
            content_html = ""
            expand_btn = ""
        
        timeline += f'''
        <div class="timeline-item" data-tags="{",".join(html.escape(t) for t in item.get("tags", []))}">
            <span class="timeline-date">{item.get("date","")}</span>
            <div class="timeline-content">
                <span class="news-source">{html.escape(item.get("source", ""))}</span>
                <div class="news-tags">{tags_html}</div>
                <h3 class="news-title">{html.escape(item["title"])}</h3>
                {content_html}
                <a href="{html.escape(item["url"])}" target="_blank" class="news-link">阅读原文</a>
                {expand_btn}
            </div>
        </div>'''
    
    html_content = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>石墨烯新闻 - {TODAY_CN}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Microsoft YaHei", sans-serif; background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); min-height: 100vh; padding: 20px; }}
        .container {{ max-width: 900px; margin: 0 auto; }}
        header {{ text-align: center; padding: 40px 0; color: #fff; }}
        h1 {{ font-size: 2.5em; margin-bottom: 10px; background: linear-gradient(90deg, #00d2ff, #3a7bd5); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; }}
        .subtitle {{ font-size: 1.1em; color: #8ba4c7; margin-bottom: 5px; }}
        .update-info {{ font-size: 0.85em; color: #5a7a9a; margin-top: 5px; }}
        .stats {{ display: flex; justify-content: center; gap: 30px; margin: 20px 0 40px; }}
        .stat-item {{ background: rgba(255,255,255,0.1); padding: 15px 30px; border-radius: 10px; color: #fff; }}
        .stat-number {{ font-size: 2em; font-weight: bold; color: #00d2ff; }}
        .stat-label {{ font-size: 0.9em; color: #8ba4c7; }}
        .filter-section {{ background: rgba(255,255,255,0.1); border-radius: 15px; padding: 20px; margin: 20px 0; }}
        .filter-title {{ color: #fff; font-size: 1.1em; margin-bottom: 15px; display: flex; align-items: center; gap: 8px; }}
        .filter-tags {{ display: flex; flex-wrap: wrap; gap: 10px; }}
        .filter-btn {{ background: rgba(255,255,255,0.15); border: 1px solid rgba(255,255,255,0.2); color: #fff; padding: 8px 16px; border-radius: 20px; cursor: pointer; transition: all 0.3s; font-size: 0.9em; }}
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
        .news-full-content {{ margin-top: 12px; padding: 12px; background: #f8fafc; border-radius: 8px; color: #333; font-size: 0.9em; line-height: 1.7; text-align: left; border-left: 3px solid #00d2ff; max-height: 300px; overflow-y: auto; }}
        .timeline-item.hidden {{ display: none; }}
        footer {{ text-align: center; padding: 40px 0; color: #8ba4c7; border-top: 1px solid rgba(255,255,255,0.1); margin-top: 40px; }}
        footer a {{ color: #00d2ff; text-decoration: none; }}
        @media (max-width: 768px) {{ .timeline::before {{ left: 20px; }} .timeline-item {{ width: 100%; padding-left: 50px; padding-right: 15px; text-align: left !important; }} .timeline-item::before {{ left: 11px !important; right: auto !important; }} h1 {{ font-size: 1.8em; }} }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>石墨烯新闻</h1>
            <p class="subtitle">{TODAY_CN} 全球石墨烯行业动态</p>
            <p class="update-info">自动采集于 {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
            <div class="stats">
                <div class="stat-item"><div class="stat-number" id="totalCount">{len(articles)}</div><div class="stat-label">新闻数量</div></div>
                <div class="stat-item"><div class="stat-number" id="filteredCount">{len(articles)}</div><div class="stat-label">显示数量</div></div>
                <div class="stat-item"><div class="stat-number" id="sourceCount">{len(set(a.get("source","") for a in articles))}</div><div class="stat-label">新闻来源</div></div>
            </div>
        </header>
        <div class="filter-section">
            <div class="filter-title"><span></span><span>按标签筛选:</span></div>
            <div class="filter-tags">{filter_btns}</div>
        </div>
        <div class="no-results" id="noResults">没有找到匹配的新闻</div>
        <div class="timeline" id="timeline">{timeline}</div>
        <footer>
            <p>数据来源: Graphene-Info | Graphene.tv | Google News</p>
            <p>GitHub: <a href="https://github.com/Vincent1026/graphene-news" target="_blank">Vincent1026/graphene-news</a></p>
            <p>自动更新于 {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
        </footer>
    </div>
    <script>
        function toggleContent(btn) {{ const c = btn.nextElementSibling; c.style.display = c.style.display === 'none' ? 'block' : 'none'; btn.textContent = c.style.display === 'none' ? '展开详情' : '收起详情'; }}
        const filterBtns = document.querySelectorAll('.filter-btn');
        const timelineItems = document.querySelectorAll('.timeline-item');
        const totalCount = document.getElementById('totalCount');
        const filteredCount = document.getElementById('filteredCount');
        const noResults = document.getElementById('noResults');
        filterBtns.forEach(btn => {{ btn.addEventListener('click', () => {{ const tag = btn.dataset.tag; filterBtns.forEach(b => b.classList.remove('active')); btn.classList.add('active'); let visibleCount = 0; timelineItems.forEach(item => {{ const itemTags = item.dataset.tags.split(','); if (tag === 'all' || itemTags.includes(tag)) {{ item.classList.remove('hidden'); visibleCount++; }} else {{ item.classList.add('hidden'); }} }}); filteredCount.textContent = visibleCount; noResults.style.display = visibleCount === 0 ? 'block' : 'none'; }}); }});
    </script>
</body>
</html>'''
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    log(f"HTML 已保存: {output_file}")

def main():
    """主函数"""
    log("=" * 60)
    log("石墨烯新闻爬虫启动")
    log(f"日期: {TODAY_STR}")
    log("=" * 60)
    
    all_articles = []
    
    # 1. 爬取 graphene-info.com
    try:
        articles1 = find_articles_graphene_info()
        all_articles.extend(articles1)
        log(f"graphene-info.com: {len(articles1)} 篇")
    except Exception as e:
        log(f"graphene-info.com 异常: {e}", "ERROR")
    
    time.sleep(random.uniform(1, 2))
    
    # 2. 爬取 graphene.tv
    try:
        articles2 = find_articles_graphene_tv()
        all_articles.extend(articles2)
        log(f"graphene.tv: {len(articles2)} 篇")
    except Exception as e:
        log(f"graphene.tv 异常: {e}", "ERROR")
    
    time.sleep(random.uniform(1, 2))
    
    # 3. 爬取 Google News
    try:
        articles3 = find_articles_google_news()
        all_articles.extend(articles3)
        log(f"Google News: {len(articles3)} 篇")
    except Exception as e:
        log(f"Google News 异常: {e}", "ERROR")
    
    log(f"\n发现文章总数: {len(all_articles)} 篇")
    
    # 去重
    seen_urls = set()
    unique_articles = []
    for article in all_articles:
        norm_url = article["url"].split("?")[0].split("#")[0]
        if norm_url not in seen_urls:
            seen_urls.add(norm_url)
            unique_articles.append(article)
    
    log(f"去重后: {len(unique_articles)} 篇")
    
    # 处理文章（抓取内容 + 翻译）
    processed = []
    for i, article in enumerate(unique_articles[:20]):  # 限制处理数量
        log(f"\n[{i+1}/{min(len(unique_articles), 20)}] 处理中...")
        try:
            result = process_article(article)
            processed.append(result)
            log(f"完成: {result['title'][:40]}")
        except Exception as e:
            log(f"处理失败: {e}", "ERROR")
        
        time.sleep(random.uniform(0.5, 1.5))
    
    log(f"\n成功处理: {len(processed)} 篇")
    
    # 生成 HTML
    if processed:
        generate_html(processed, TODAY_FILE)
        
        # 同时更新 news_data.json
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, 'r', encoding='utf-8') as f:
                    existing_data = json.load(f)
            except:
                existing_data = []
        else:
            existing_data = []
        
        # 合并（新的在前）
        existing_urls = {d["url"].split("?")[0].split("#")[0] for d in existing_data}
        new_items = [p for p in processed if p["url"].split("?")[0].split("#")[0] not in existing_urls]
        all_data = new_items + existing_data
        
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(all_data, f, ensure_ascii=False, indent=2)
        
        log(f"数据已保存: {DATA_FILE} (总计 {len(all_data)} 篇)")
    
    # 统计
    log("\n" + "=" * 60)
    log("爬取摘要")
    log(f"  日期: {TODAY_STR}")
    log(f"  处理完成: {len(processed)} 篇")
    
    source_stats = {}
    for item in processed:
        src = item.get("source", "Unknown")
        source_stats[src] = source_stats.get(src, 0) + 1
    
    for src, count in sorted(source_stats.items(), key=lambda x: -x[1]):
        log(f"    {src}: {count} 篇")
    
    log("=" * 60)
    log("爬取完成！")
    log(f"HTML 文件: {TODAY_FILE}")
    log("=" * 60)

if __name__ == "__main__":
    main()
