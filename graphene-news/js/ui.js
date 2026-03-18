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

// ========== 标签过滤系统 ==========

let currentFilter = { type: 'all', value: '' };

// 给标签添加过滤功能的样式
function injectFilterStyles() {
  if (document.getElementById('filter-styles')) return;

  const style = document.createElement('style');
  style.id = 'filter-styles';
  style.textContent = `
    .tag { cursor: pointer; transition: all 0.15s; user-select: none; }
    .tag:hover { opacity: 0.75; transform: scale(1.05); }
    .tag.active-filter { box-shadow: 0 0 0 2px #fff3; transform: scale(1.08); }

    /* 过滤器栏 */
    .filter-bar {
      background: var(--card-bg, rgba(10,14,26,0.9));
      border-bottom: 1px solid var(--card-border, #1e3a5f);
      padding: 10px 20px;
      display: flex; align-items: center; gap: 8px;
      flex-wrap: wrap;
    }
    .filter-label {
      font-size: 11px; color: var(--text-muted, #94a3b8);
      letter-spacing: 1px; text-transform: uppercase; margin-right: 4px; white-space: nowrap;
    }
    .filter-chip {
      display: inline-flex; align-items: center; gap: 5px;
      padding: 4px 12px; border-radius: 20px; font-size: 11px;
      border: 1px solid var(--card-border, #1e3a5f);
      background: transparent; color: var(--text-muted, #94a3b8);
      cursor: pointer; transition: all 0.15s; white-space: nowrap;
    }
    .filter-chip:hover { border-color: var(--accent, #00d4ff); color: var(--accent, #00d4ff); }
    .filter-chip.active { background: rgba(0,212,255,0.12); border-color: var(--accent, #00d4ff); color: var(--accent, #00d4ff); }
    .filter-chip.clear-btn { border-color: rgba(255,107,53,0.3); color: rgba(255,107,53,0.7); }
    .filter-chip.clear-btn:hover { border-color: #ff6b35; color: #ff6b35; background: rgba(255,107,53,0.1); }
    .filter-count { font-size: 11px; color: var(--text-muted, #94a3b8); margin-left: auto; white-space: nowrap; }
    .filter-count span { color: var(--accent, #00d4ff); font-weight: 600; }

    /* 被过滤隐藏的卡片 */
    .full-article.filtered-out { display: none !important; }
  `;
  document.head.appendChild(style);
}

// 初始化过滤器（在日报页面调用）
function initFilterBar(news, articleSelector = '.full-article') {
  injectFilterStyles();

  // 收集所有标签
  const allTags = new Set();
  news.forEach(n => n.tags.forEach(t => allTags.add(t)));

  // 生成标签列表（去重）
  const tagList = Array.from(allTags);

  // 构建过滤器 HTML
  const filterHtml = `
    <div class="filter-bar" id="filter-bar">
      <span class="filter-label">🔍 筛选</span>
      <span class="filter-chip active" data-filter="all" onclick="setFilter('all',this)">全部 <b>${news.length}</b></span>
      ${tagList.map(tag => {
        if (tag === '热门') {
          return `<span class="filter-chip" data-filter="hot" data-value="${tag}" onclick="setFilter('hot','${tag}',this)">🔥 ${tag}</span>`;
        }
        return `<span class="filter-chip" data-filter="tag" data-value="${tag}" onclick="setFilter('tag','${tag}',this)">${tag}</span>`;
      }).join('')}
      <span class="filter-chip clear-btn" onclick="setFilter('all',document.querySelector('[data-filter=all]'))">✕ 清除</span>
      <span class="filter-count">显示 <span id="visible-count">${news.length}</span> / ${news.length}</span>
    </div>
  `;

  // 插入到 articles-root 之前
  const articlesRoot = document.getElementById('articles-root');
  if (articlesRoot) {
    articlesRoot.insertAdjacentHTML('beforebegin', filterHtml);
  }

  // 绑定标签点击
  bindTagClicks(articleSelector);
}

// 设置过滤条件
window.setFilter = function(type, value, chipEl) {
  if (value instanceof HTMLElement) {
    chipEl = value;
    value = '';
  }

  currentFilter = { type, value };

  // 更新高亮
  document.querySelectorAll('.filter-chip').forEach(c => c.classList.remove('active'));
  if (chipEl) chipEl.classList.add('active');

  // 执行过滤
  applyFilter('.full-article');
};

// 执行过滤
function applyFilter(articleSelector) {
  const cards = document.querySelectorAll(articleSelector);
  let visibleCount = 0;

  cards.forEach(card => {
    if (currentFilter.type === 'all') {
      card.classList.remove('filtered-out');
      visibleCount++;
      return;
    }

    // 获取卡片的所有标签
    const tags = Array.from(card.querySelectorAll('.tag')).map(t => t.textContent.trim());

    let match = false;
    if (currentFilter.type === 'hot') {
      match = tags.some(t => t === '热门' || t === '重磅' || t === '突破');
    } else {
      match = tags.includes(currentFilter.value);
    }

    if (match) {
      card.classList.remove('filtered-out');
      visibleCount++;
    } else {
      card.classList.add('filtered-out');
    }
  });

  // 更新计数
  const countEl = document.getElementById('visible-count');
  if (countEl) countEl.textContent = visibleCount;
}

// 绑定标签点击
function bindTagClicks(articleSelector) {
  document.querySelectorAll('.tag').forEach(tag => {
    tag.addEventListener('click', (e) => {
      e.stopPropagation();

      const text = tag.textContent.trim();

      // 更新高亮状态
      document.querySelectorAll('.tag').forEach(t => t.classList.remove('active-filter'));

      if (currentFilter.type === 'tag' && currentFilter.value === text) {
        // 再次点击同一标签，取消过滤
        setFilter('all', '', document.querySelector('[data-filter=all]'));
      } else {
        tag.classList.add('active-filter');

        // 找到对应的 filter-chip 并高亮
        const chip = document.querySelector(`.filter-chip[data-value="${text}"]`);
        if (chip) {
          setFilter('tag', text, chip);
        } else {
          // 如果 filter-chip 不存在（比如在非日报页面），直接过滤
          currentFilter = { type: 'tag', value: text };
          applyFilter(articleSelector);
          const countEl = document.getElementById('visible-count');
          if (countEl) {
            const total = document.querySelectorAll(articleSelector).length;
            let visible = 0;
            document.querySelectorAll(articleSelector).forEach(c => {
              if (!c.classList.contains('filtered-out')) visible++;
            });
            countEl.textContent = visible + ' / ' + total;
          }
        }
      }
    });
  });
}
