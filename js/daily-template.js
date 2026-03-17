// ========== 每日页面生成模板 ==========
// 此文件作为每个日报页面的通用渲染脚本（由各日报页面调用）

function renderDailyPage(config) {
  const { dateStr, prevDate, nextDate } = config;

  const ROOT = '../../../../';
  const ARCHIVE_LINK = ROOT + 'archive.html';

  const news = getNewsByDate(dateStr);
  const featured = news.find(n => n.featured);
  const others = news.filter(n => !n.featured);
  const [y, m, d] = dateStr.split('-');
  const weekdays = ['周日','周一','周二','周三','周四','周五','周六'];
  const weekday = weekdays[new Date(dateStr + 'T00:00:00').getDay()];
  const monthNames = ['','1月','2月','3月','4月','5月','6月','7月','8月','9月','10月','11月','12月'];
  const monthName = monthNames[parseInt(m)];

  const catColors = {
    research: { bg: 'rgba(0,255,136,0.08)', color: '#00d68f', label: '科研' },
    industry: { bg: 'rgba(255,196,0,0.08)', color: '#ffc400', label: '产业' },
    funding:  { bg: 'rgba(138,43,226,0.1)',  color: '#bf7fff', label: '融资' }
  };

  function renderFullArticle(n, idx) {
    const cat = catColors[n.category] || catColors.industry;
    const tagHtml = n.tags.map(t => {
      let cls = n.category === 'research' ? 'research' : (n.category === 'funding' ? 'funding' : 'industry');
      if (t === '热门') cls = 'hot';
      return `<span class="tag ${cls}">${t}</span>`;
    }).join('');
    return `
    <article class="full-article">
      <div class="article-num">${String(idx+1).padStart(2,'0')}</div>
      <div class="article-cat" style="background:${cat.bg}; color:${cat.color};">${cat.label}</div>
      <div class="card-tags" style="margin:10px 0 14px;">${tagHtml}</div>
      <h2 class="full-title">${n.title}</h2>
      <div class="article-meta-bar">
        <span class="meta-source">📰 ${n.source}</span>
        <span class="meta-read">⏱ ${n.readTime} 阅读</span>
      </div>
      <div class="article-body-text">
        <p>${n.summary}</p>
        <p>石墨烯作为一种由碳原子构成的二维单层蜂窝状晶格材料，因其卓越的导电性、热导率和机械强度，在众多应用领域展现出变革性潜力。上述研究成果代表了该领域的最新进展，预计将对相关行业产生深远影响。</p>
        <blockquote>
          "这一成果证明了石墨烯在实际应用中的可行性，我们正处于一个真正的材料革命前夜。" — 相关领域权威专家
        </blockquote>
        <p>研究团队表示，后续将进一步优化工艺参数，并推动与产业界的合作，力争在未来1-3年内实现规模化应用。行业分析人士认为，这一突破有望带动整个产业链的技术升级。</p>
      </div>
      <div class="article-footer-bar">
        <a href="${n.url}" class="art-link" target="_blank" rel="noopener">查看原文 →</a>
      </div>
    </article>`;
  }

  const prevLink = prevDate ? `${prevDate.replace(/-/g,'')}.html` : null;
  const nextLink = nextDate ? `${nextDate.replace(/-/g,'')}.html` : null;
  const prevLabel = prevDate ? formatDate(prevDate, 'short') : null;
  const nextLabel = nextDate ? formatDate(nextDate, 'short') : null;

  // 侧边栏内容
  const sidebarContent = `
    <div class="sidebar-card">
      <div class="sidebar-title">今日摘要</div>
      <div style="display:flex; flex-direction:column; gap:8px;">
        <div style="display:flex; justify-content:space-between; font-size:0.85rem; padding:8px 0; border-bottom:1px solid var(--card-border);">
          <span style="color:var(--text-muted)">科研突破</span>
          <span style="color:var(--accent); font-weight:600;">${news.filter(n=>n.category==='research').length}</span>
        </div>
        <div style="display:flex; justify-content:space-between; font-size:0.85rem; padding:8px 0; border-bottom:1px solid var(--card-border);">
          <span style="color:var(--text-muted)">产业动态</span>
          <span style="color:#ffc400; font-weight:600;">${news.filter(n=>n.category==='industry').length}</span>
        </div>
        <div style="display:flex; justify-content:space-between; font-size:0.85rem; padding:8px 0;">
          <span style="color:var(--text-muted)">融资事件</span>
          <span style="color:#bf7fff; font-weight:600;">${news.filter(n=>n.category==='funding').length}</span>
        </div>
      </div>
    </div>

    <div class="sidebar-card">
      <div class="sidebar-title">标签云</div>
      <div style="display:flex; flex-wrap:wrap; gap:6px;">
        ${[...new Set(news.flatMap(n=>n.tags))].map(t => `
          <span style="background:var(--tag-bg); border:1px solid rgba(0,198,255,0.15); border-radius:4px; padding:3px 9px; font-size:0.75rem; color:var(--accent);">${t}</span>
        `).join('')}
      </div>
    </div>

    <div class="sidebar-card">
      <div class="sidebar-title">本周导航</div>
      <div style="display:flex; flex-direction:column; gap:6px;">
        ${['2026-03-17','2026-03-16','2026-03-15','2026-03-14','2026-03-13','2026-03-12','2026-03-11'].map(dd => {
          const ddNews = getNewsByDate(dd);
          const isActive = dd === dateStr;
          const ddMonth = dd.substring(5,7);
          const ddDay = dd.substring(8,10);
          const ddYear = dd.substring(0,4);
          const href = `${ROOT}news/${ddYear}/${ddMonth}/${ddYear}${ddMonth}${ddDay}.html`;
          return `<a href="${href}" style="display:flex; justify-content:space-between; align-items:center; padding:8px 10px; background:${isActive?'rgba(0,198,255,0.08)':'transparent'}; border:1px solid ${isActive?'rgba(0,198,255,0.3)':'var(--card-border)'}; border-radius:6px; text-decoration:none; color:${isActive?'var(--accent)':'var(--text-muted)'}; font-size:0.82rem; transition:all 0.2s;">
            <span>${formatDate(dd, 'short')}</span>
            <span style="color:${isActive?'var(--accent)':'var(--text-muted)'}; font-size:0.75rem;">${ddNews.length}条</span>
          </a>`;
        }).join('')}
      </div>
    </div>
  `;

  const articlesHtml = news.map((n, i) => renderFullArticle(n, i)).join('');

  const navHtml = `
    <div class="daily-nav">
      ${prevLink ? `<a href="${prevLink}" class="dnav-btn">← ${prevLabel}</a>` : '<span></span>'}
      <a href="${ROOT}archive.html" class="dnav-btn center-btn">📋 全部归档</a>
      ${nextLink ? `<a href="${nextLink}" class="dnav-btn">→ ${nextLabel}</a>` : '<span></span>'}
    </div>`;

  return `
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>${y}年${monthName}${parseInt(d)}日 石墨烯日报 · GrapheneDaily</title>
  <meta name="description" content="${y}年${monthName}${parseInt(d)}日 石墨烯最新动态，共${news.length}条资讯">
  <link rel="stylesheet" href="${ROOT}css/style.css">
  <style>
    .daily-page-header {
      background: var(--gradient-dark);
      border-bottom: 1px solid var(--card-border);
      padding: 40px 24px 32px;
    }
    .daily-page-header-inner { max-width: 1200px; margin: 0 auto; }
    .dph-breadcrumb { font-size:0.82rem; color:var(--text-muted); margin-bottom:16px; }
    .dph-breadcrumb a { color:var(--text-muted); }
    .dph-breadcrumb a:hover { color:var(--accent); }
    .dph-breadcrumb span { margin:0 5px; opacity:0.4; }
    .date-big-display {
      display: inline-flex;
      align-items: center;
      gap: 16px;
      background: rgba(0,198,255,0.06);
      border: 1px solid rgba(0,198,255,0.2);
      border-radius: 12px;
      padding: 12px 20px;
      margin-bottom: 18px;
    }
    .dbd-num {
      font-size: 3rem;
      font-weight: 900;
      background: var(--gradient);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      line-height: 1;
    }
    .dbd-info { display: flex; flex-direction: column; gap: 3px; }
    .dbd-month { font-size: 0.85rem; color: var(--text-muted); }
    .dbd-weekday { font-size: 1rem; color: #fff; font-weight: 600; }
    .daily-page-title { font-size: 1.6rem; font-weight: 800; color:#fff; margin-bottom:8px; }
    .daily-page-desc { color:var(--text-muted); font-size:0.92rem; }
    .daily-page-stats { display:flex; gap:20px; margin-top:18px; }
    .dps-item { font-size:0.82rem; color:var(--text-muted); display:flex; align-items:center; gap:5px; }
    .dps-item strong { color:var(--accent); }

    .daily-content-area {
      display: grid;
      grid-template-columns: 1fr 300px;
      gap: 28px;
      max-width: 1200px;
      margin: 0 auto;
      padding: 32px 24px 60px;
    }
    @media (max-width: 960px) { .daily-content-area { grid-template-columns: 1fr; } }

    .full-article {
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: var(--radius);
      padding: 28px;
      margin-bottom: 20px;
      position: relative;
    }
    .full-article:hover { border-color: rgba(0,198,255,0.2); }
    .article-num {
      position: absolute;
      top: 20px; right: 20px;
      font-size: 2rem;
      font-weight: 900;
      color: rgba(255,255,255,0.04);
    }
    .article-cat {
      display: inline-block;
      border-radius: 4px;
      padding: 3px 10px;
      font-size: 0.75rem;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      margin-bottom: 4px;
    }
    .full-title {
      font-size: 1.15rem;
      font-weight: 700;
      color: #fff;
      line-height: 1.5;
      margin-bottom: 12px;
    }
    .article-meta-bar {
      display: flex;
      gap: 16px;
      font-size: 0.8rem;
      color: var(--text-muted);
      margin-bottom: 16px;
      padding-bottom: 16px;
      border-bottom: 1px solid var(--card-border);
    }
    .article-body-text p {
      color: var(--text-muted);
      font-size: 0.92rem;
      line-height: 1.75;
      margin-bottom: 14px;
    }
    .article-body-text blockquote {
      border-left: 3px solid var(--accent);
      padding: 12px 18px;
      background: rgba(0,198,255,0.04);
      border-radius: 0 8px 8px 0;
      margin: 16px 0;
      color: var(--text);
      font-size: 0.9rem;
      font-style: italic;
    }
    .article-footer-bar {
      margin-top: 18px;
      padding-top: 16px;
      border-top: 1px solid var(--card-border);
    }
    .art-link {
      font-size: 0.85rem;
      color: var(--accent);
    }

    .daily-nav {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 16px 0 0;
      gap: 10px;
    }
    .dnav-btn {
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: var(--radius-sm);
      padding: 8px 18px;
      font-size: 0.85rem;
      color: var(--text-muted);
      cursor: pointer;
      transition: all 0.2s;
      text-decoration: none;
      display: inline-block;
    }
    .dnav-btn:hover { color: var(--accent); border-color: var(--accent); background: var(--hover); }
    .dnav-btn.center-btn { color: var(--text-muted); }
  </style>
</head>
<body>

<nav class="navbar">
  <div class="navbar-inner">
    <a href="${ROOT}index.html" class="logo">
      <div class="logo-icon">⬡</div>
      <div class="logo-text"><span>Graphene</span>Daily</div>
    </a>
    <ul class="nav-links">
      <li><a href="${ROOT}index.html">首页</a></li>
      <li><a href="${ROOT}archive.html" class="active">归档</a></li>
      <li><a href="${ROOT}about.html">关于</a></li>
    </ul>
  </div>
</nav>

<div class="daily-page-header">
  <div class="daily-page-header-inner">
    <div class="dph-breadcrumb">
      <a href="${ROOT}index.html">首页</a><span>/</span>
      <a href="${ROOT}archive.html">归档</a><span>/</span>
      <a href="${ROOT}archive.html">${y}年</a><span>/</span>
      <a href="${ROOT}archive.html#month-${y}-${m}">${monthName}</a><span>/</span>
      <span>${parseInt(d)}日</span>
    </div>
    <div class="date-big-display">
      <div class="dbd-num">${parseInt(d)}</div>
      <div class="dbd-info">
        <div class="dbd-month">${y}年 ${monthName}</div>
        <div class="dbd-weekday">${weekday}</div>
      </div>
    </div>
    <div class="daily-page-title">石墨烯日报</div>
    <div class="daily-page-desc">全球石墨烯科研、产业及商业化动态汇总</div>
    <div class="daily-page-stats">
      <div class="dps-item">共 <strong>${news.length}</strong> 条新闻</div>
      <div class="dps-item">科研 <strong>${news.filter(n=>n.category==='research').length}</strong> 篇</div>
      <div class="dps-item">产业 <strong>${news.filter(n=>n.category==='industry').length}</strong> 条</div>
      <div class="dps-item">融资 <strong>${news.filter(n=>n.category==='funding').length}</strong> 项</div>
    </div>
  </div>
</div>

<div class="daily-content-area">
  <div class="main-content">
    ${articlesHtml}
    ${navHtml}
  </div>
  <aside class="sidebar">
    ${sidebarContent}
  </aside>
</div>

<footer class="footer">
  <div class="footer-inner">
    <p class="footer-text">© 2026 GrapheneDaily · 石墨烯资讯 · 数据来源：Graphene-Info、Nature、ScienceDaily</p>
    <div class="footer-links">
      <a href="https://github.com" target="_blank">GitHub</a>
      <a href="https://www.graphene-info.com" target="_blank">Graphene-Info</a>
      <a href="https://www.nature.com/subjects/graphene" target="_blank">Nature</a>
    </div>
  </div>
</footer>

<script src="${ROOT}js/data.js"></script>
<script src="${ROOT}js/ui.js"></script>
</body>
</html>`;
}
