// ========== 通用UI组件 ==========

// 渲染导航栏
function renderNavbar(activePage = 'home') {
  const pages = [
    { id: 'home', label: '首页', href: '../../index.html' },
    { id: 'archive', label: '归档', href: '../../archive.html' },
    { id: 'about', label: '关于', href: '../../about.html' }
  ];
  return `
  <nav class="navbar">
    <div class="navbar-inner">
      <a href="../../index.html" class="logo">
        <div class="logo-icon">⬡</div>
        <div class="logo-text"><span>Graphene</span>Daily</div>
      </a>
      <ul class="nav-links">
        ${pages.map(p => `<li><a href="${p.href}" class="${activePage===p.id?'active':''}">${p.label}</a></li>`).join('')}
      </ul>
    </div>
  </nav>`;
}

// 渲染主页导航栏
function renderNavbarHome(activePage = 'home') {
  const pages = [
    { id: 'home', label: '首页', href: 'index.html' },
    { id: 'archive', label: '归档', href: 'archive.html' },
    { id: 'about', label: '关于', href: 'about.html' }
  ];
  return `
  <nav class="navbar">
    <div class="navbar-inner">
      <a href="index.html" class="logo">
        <div class="logo-icon">⬡</div>
        <div class="logo-text"><span>Graphene</span>Daily</div>
      </a>
      <ul class="nav-links">
        ${pages.map(p => `<li><a href="${p.href}" class="${activePage===p.id?'active':''}">${p.label}</a></li>`).join('')}
      </ul>
    </div>
  </nav>`;
}

// 渲染单个新闻卡片
function renderNewsCard(news, size = 'normal') {
  const tagHtml = news.tags.map(t => {
    const cls = t === '热门' ? 'hot' : (news.category === 'research' ? 'research' : (news.category === 'funding' ? 'funding' : 'industry'));
    return `<span class="tag ${cls}">${t}</span>`;
  }).join('');

  const dateStr = news.id.substring(0, 8);
  const year = dateStr.substring(0, 4);
  const month = dateStr.substring(4, 6);
  const day = dateStr.substring(6, 8);
  const dayLink = `news/${year}/${month}/${year}${month}${day}.html`;

  return `
  <article class="news-card ${size === 'featured' ? 'featured-card' : ''}" onclick="location.href='${dayLink}'">
    <div class="card-tags">${tagHtml}</div>
    <h3 class="card-title">${news.title}</h3>
    <p class="card-summary">${news.summary}</p>
    <div class="card-footer">
      <span class="card-source">
        <span class="source-dot"></span>
        ${news.source}
      </span>
      <span class="card-read-more">${news.readTime} 阅读</span>
    </div>
  </article>`;
}

// 渲染列表项
function renderNewsListItem(news, index, dateStr) {
  const year = dateStr.substring(0, 4);
  const month = dateStr.substring(5, 7);
  const day = dateStr.substring(8, 10);
  const dayLink = `news/${year}/${month}/${year}${month}${day}.html`;

  return `
  <div class="news-list-item" onclick="location.href='${dayLink}'">
    <div class="list-number">${String(index + 1).padStart(2, '0')}</div>
    <div class="list-content">
      <div class="list-title">${news.title}</div>
      <div class="list-meta">${news.source} · ${news.readTime} 阅读 · ${getCategoryLabel(news.category)}</div>
    </div>
  </div>`;
}

// 渲染页脚
function renderFooter() {
  return `
  <footer class="footer">
    <div class="footer-inner">
      <p class="footer-text">© 2026 GrapheneDaily · 石墨烯资讯 · 数据来源：Graphene-Info、Nature、ScienceDaily</p>
      <div class="footer-links">
        <a href="https://github.com" target="_blank">GitHub</a>
        <a href="https://www.graphene-info.com" target="_blank">Graphene-Info</a>
        <a href="https://www.nature.com/subjects/graphene" target="_blank">Nature</a>
      </div>
    </div>
  </footer>`;
}

// 渲染面包屑（在主页目录下使用）
function renderBreadcrumb(items) {
  const parts = items.map((item, i) => {
    if (i === items.length - 1) return `<span>${item.label}</span>`;
    return `<a href="${item.href}">${item.label}</a><span class="breadcrumb-sep">/</span>`;
  });
  return `<div class="breadcrumb">${parts.join('')}</div>`;
}
