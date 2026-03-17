# GrapheneDaily · 石墨烯资讯网站

> 每日追踪全球石墨烯最新科研突破与产业动态

[![GitHub Pages](https://img.shields.io/badge/Deploy-GitHub%20Pages-blue?logo=github)](https://github.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

## 功能特点

- 🏠 **主页** — 展示当日最新石墨烯新闻，本周日历速览
- 📅 **年归档** — 按年份浏览全年所有动态
- 🗓 **月归档** — 按月查看每日汇总，快速定位目标日期
- 📋 **周归档** — 以周为单位的新闻概览
- 📰 **日报** — 每天独立子页面，包含完整新闻详情
- 🏷 **分类标签** — 科研 / 产业 / 融资三大分类
- 🌙 **深色主题** — 精心设计的深色科技风界面

## 项目结构

```
graphene-news/
├── index.html              # 主页（当日新闻）
├── archive.html            # 归档总览（年/月/周）
├── about.html              # 关于页面
├── css/
│   └── style.css           # 全站样式
├── js/
│   ├── data.js             # 新闻数据库
│   ├── ui.js               # 通用UI组件
│   └── daily-template.js   # 日报页面模板
└── news/
    └── 2026/
        └── 03/             # 年/月目录
            ├── 20260317.html  # 每日子页面
            ├── 20260316.html
            └── ...
```

## 部署到 GitHub Pages

1. Fork 本仓库
2. 进入 Settings → Pages
3. Source 选择 `main` 分支，目录选择 `/(root)`
4. 保存后等待几分钟，即可访问 `https://你的用户名.github.io/graphene-news`

## 添加新闻数据

编辑 `js/data.js` 文件，在对应日期下添加新闻条目：

```javascript
"2026-03-18": [
  {
    id: "20260318-001",
    title: "新闻标题",
    summary: "新闻摘要...",
    source: "来源机构",
    category: "research", // research | industry | funding
    tags: ["标签1", "标签2"],
    url: "原文链接",
    readTime: "3 min",
    featured: false  // true 表示置顶
  }
]
```

然后在 `news/2026/03/` 目录下创建对应的 `20260318.html` 日报页面。

## 数据来源

- [Graphene-Info](https://www.graphene-info.com)
- [Nature - Graphene](https://www.nature.com/subjects/graphene)
- [ScienceDaily - Graphene](https://www.sciencedaily.com/news/matter_energy/graphene/)
- [IDTechEx](https://www.idtechex.com)
- EU Graphene Flagship Project

## License

MIT © 2026 GrapheneDaily
