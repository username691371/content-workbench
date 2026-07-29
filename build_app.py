"""
爆款素材工作台 - 生成单文件HTML APP
把daily_data.json内嵌进HTML，浏览器打开即用。
支持：博主筛选Tab、关键词搜索、按播放/点赞排序、详情弹窗、创作灵感侧栏。
"""
import json
import urllib.parse
from pathlib import Path


def generate_html(data):
    data_json = json.dumps(data, ensure_ascii=False)

    html = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<meta name="theme-color" content="#0f1117">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="爆款工作台">
<meta name="mobile-web-app-capable" content="yes">
<link rel="manifest" href="data:application/json;charset=utf-8,__MANIFEST__">
<link rel="apple-touch-icon" href="data:image/svg+xml;utf8,__ICON__">
<link rel="icon" href="data:image/svg+xml;utf8,__ICON__">
<title>爆款素材工作台 · __DATE__</title>
<style>
:root {
  --bg: #0f1117;
  --card: #1a1d28;
  --card-hover: #22263a;
  --border: #2a2e3f;
  --text: #e4e6ef;
  --text-dim: #8b8fa3;
  --primary: #6c5ce7;
  --primary-dim: #5247d6;
  --accent: #00d4aa;
  --hot: #ff6b6b;
  --warm: #ffa94d;
  --tag-bg: #2d3150;
}
* { margin:0; padding:0; box-sizing:border-box; }
body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif;
  background: var(--bg); color: var(--text); line-height: 1.6;
}
/* ===== Header ===== */
.header {
  position: sticky; top: 0; z-index: 100;
  background: rgba(15,17,23,0.95); backdrop-filter: blur(12px);
  border-bottom: 1px solid var(--border); padding: 16px 24px;
}
.header-top { display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:12px; }
.header h1 { font-size: 20px; font-weight: 700; }
.header h1 .icon { margin-right: 8px; }
.header .date { color: var(--accent); font-size: 14px; font-weight: 600; }
.header .stats { display:flex; gap:16px; font-size:13px; color: var(--text-dim); }
.header .stats span b { color: var(--text); }
.search-box { flex: 1; max-width: 320px; }
.search-box input {
  width:100%; padding:8px 14px; border-radius:20px;
  border: 1px solid var(--border); background: var(--card);
  color: var(--text); font-size: 14px; outline: none;
  transition: border-color .2s;
}
.search-box input:focus { border-color: var(--primary); }
/* ===== Tabs ===== */
.tabs {
  display: flex; gap: 8px; margin-top: 14px; flex-wrap: wrap;
}
.tab {
  padding: 6px 16px; border-radius: 16px; cursor: pointer;
  font-size: 13px; background: var(--card); border: 1px solid var(--border);
  color: var(--text-dim); transition: all .2s; user-select: none;
}
.tab:hover { border-color: var(--primary); color: var(--text); }
.tab.active {
  background: var(--primary); border-color: var(--primary); color: #fff;
}
.tab .count { font-size: 11px; opacity: 0.7; margin-left: 4px; }
/* ===== Layout ===== */
.layout {
  display: grid; grid-template-columns: 1fr 340px; gap: 20px;
  padding: 20px 24px; max-width: 1600px; margin: 0 auto;
}
@media (max-width: 900px) { .layout { grid-template-columns: 1fr; } }
/* ===== Sort bar ===== */
.sort-bar {
  display: flex; gap: 8px; align-items: center; margin-bottom: 14px;
  font-size: 13px; color: var(--text-dim);
}
.sort-bar .sort-opt {
  padding: 4px 12px; border-radius: 12px; cursor: pointer;
  border: 1px solid var(--border); transition: all .2s;
}
.sort-bar .sort-opt.active { background: var(--tag-bg); color: var(--text); border-color: var(--primary); }
.sort-bar .sort-opt:hover { color: var(--text); }
/* ===== Card grid ===== */
.card-grid {
  display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 14px;
}
.card {
  background: var(--card); border: 1px solid var(--border);
  border-radius: 12px; overflow: hidden; cursor: pointer;
  transition: all .2s; display: flex; flex-direction: column;
}
.card:hover { background: var(--card-hover); border-color: var(--primary); transform: translateY(-2px); }
.card .thumb {
  position: relative; width: 100%; padding-top: 56.25%; overflow: hidden;
  background: #111;
}
.card .thumb img {
  position: absolute; top:0; left:0; width:100%; height:100%; object-fit: cover;
}
.card .thumb .duration {
  position: absolute; bottom: 6px; right: 6px;
  background: rgba(0,0,0,0.75); color:#fff; font-size:11px;
  padding: 2px 6px; border-radius: 4px;
}
.card .thumb .rank-badge {
  position: absolute; top: 6px; left: 6px;
  background: var(--hot); color:#fff; font-size:11px; font-weight:700;
  padding: 3px 8px; border-radius: 4px;
}
.card .body { padding: 12px 14px; flex: 1; display: flex; flex-direction: column; }
.card .title {
  font-size: 14px; font-weight: 600; line-height: 1.4;
  display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical;
  overflow: hidden; margin-bottom: 8px;
}
.card .summary {
  font-size: 12px; color: var(--text-dim); line-height: 1.5;
  display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical;
  overflow: hidden; margin-bottom: 8px;
}
.card .meta {
  display: flex; gap: 10px; font-size: 11px; color: var(--text-dim);
  margin-top: auto;
}
.card .meta .stat { display: flex; align-items: center; gap: 3px; }
.card .author {
  font-size: 12px; color: var(--accent); margin-bottom: 6px; font-weight: 500;
}
.card .tags { display: flex; gap: 4px; flex-wrap: wrap; }
.card .tag {
  font-size: 10px; padding: 2px 8px; border-radius: 10px;
  background: var(--tag-bg); color: var(--text-dim);
}
.card .tag.topic { background: var(--primary-dim); color: #fff; }
.card .tag.core { background: var(--hot); color: #fff; }
/* ===== Sidebar ===== */
.sidebar { position: sticky; top: 180px; align-self: start; max-height: calc(100vh - 200px); overflow-y: auto; }
.sidebar h2 {
  font-size: 16px; margin-bottom: 12px; display: flex; align-items: center; gap: 8px;
}
.sidebar h2 .dot { width:8px; height:8px; border-radius:50%; background: var(--accent); }
.insp-list { display: flex; flex-direction: column; gap: 10px; }
.insp-card {
  background: var(--card); border: 1px solid var(--border);
  border-radius: 10px; padding: 12px 14px; border-left: 3px solid var(--primary);
}
.insp-card.topic-职场 { border-left-color: #00d4aa; }
.insp-card.topic-认知 { border-left-color: #6c5ce7; }
.insp-card.topic-学业 { border-left-color: #ffa94d; }
.insp-card.topic-情感 { border-left-color: #ff6b9d; }
.insp-card.topic-金钱 { border-left-color: #ffd43b; }
.insp-card.topic-人生 { border-left-color: #4dabf7; }
.insp-card .insp-text { font-size: 13px; line-height: 1.5; }
.insp-card .insp-meta { font-size: 11px; color: var(--text-dim); margin-top: 6px; }
.insp-card .insp-meta .src { color: var(--accent); }
/* ===== Topic chart ===== */
.topic-chart { margin-bottom: 18px; }
.topic-bar { display: flex; align-items: center; gap: 8px; margin-bottom: 6px; font-size: 12px; }
.topic-bar .label { width: 40px; text-align: right; color: var(--text-dim); }
.topic-bar .bar-bg { flex: 1; height: 18px; background: var(--card); border-radius: 9px; overflow: hidden; }
.topic-bar .bar-fill { height: 100%; border-radius: 9px; transition: width .5s; }
.topic-bar .num { width: 28px; font-size: 11px; color: var(--text-dim); }
/* ===== Modal ===== */
.modal-overlay {
  position: fixed; top:0; left:0; width:100%; height:100%;
  background: rgba(0,0,0,0.7); z-index: 200; display: none;
  justify-content: center; align-items: center; padding: 20px;
}
.modal-overlay.show { display: flex; }
.modal {
  background: var(--card); border-radius: 16px; max-width: 640px; width: 100%;
  max-height: 85vh; overflow-y: auto; border: 1px solid var(--border);
}
.modal-header { position: relative; }
.modal-header img { width: 100%; max-height: 280px; object-fit: cover; border-radius: 16px 16px 0 0; }
.modal-close {
  position: absolute; top: 12px; right: 12px; width: 32px; height: 32px;
  border-radius: 50%; background: rgba(0,0,0,0.6); color:#fff;
  border: none; cursor: pointer; font-size: 18px; display: flex;
  align-items: center; justify-content: center;
}
.modal-body { padding: 20px 24px; }
.modal-body h3 { font-size: 18px; margin-bottom: 12px; line-height: 1.4; }
.modal-body .meta-row { display: flex; gap: 16px; margin-bottom: 16px; font-size: 13px; color: var(--text-dim); }
.modal-body .meta-row .stat b { color: var(--text); }
.modal-body .section { margin-bottom: 16px; }
.modal-body .section-label {
  font-size: 12px; color: var(--accent); margin-bottom: 6px; font-weight: 600;
  text-transform: uppercase; letter-spacing: 0.5px;
}
.modal-body .section-content { font-size: 14px; color: var(--text); }
.modal-body .quote-box {
  background: var(--tag-bg); padding: 10px 14px; border-radius: 8px;
  border-left: 3px solid var(--accent); font-style: italic; font-size: 14px;
}
.modal-body .insp-list { gap: 8px; }
.modal-body .insp-item {
  padding: 8px 12px; background: var(--tag-bg); border-radius: 8px; font-size: 13px;
}
.modal-body .open-link {
  display: inline-block; margin-top: 12px; padding: 8px 20px;
  background: var(--primary); color: #fff; border-radius: 8px;
  text-decoration: none; font-size: 14px; font-weight: 500;
}
.modal-body .open-link:hover { background: var(--primary-dim); }
/* ===== Empty ===== */
.empty { text-align: center; padding: 60px 20px; color: var(--text-dim); }
.empty .emoji { font-size: 48px; margin-bottom: 12px; }
/* scrollbar */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--primary); }
</style>
</head>
<body>

<div class="header">
  <div class="header-top">
    <h1><span class="icon">🔥</span>爆款素材工作台</h1>
    <div class="search-box"><input id="searchInput" placeholder="搜索标题、博主、关键词..." /></div>
    <div class="stats" id="statsBox"></div>
  </div>
  <div class="date" id="dateStr"></div>
  <div class="tabs" id="tabsBox"></div>
</div>

<div class="layout">
  <div class="main">
    <div class="sort-bar">
      <span>排序：</span>
      <span class="sort-opt active" data-sort="hot">综合热度</span>
      <span class="sort-opt" data-sort="play">播放量</span>
      <span class="sort-opt" data-sort="like">点赞数</span>
      <span class="sort-opt" data-sort="interact">互动分</span>
    </div>
    <div class="card-grid" id="cardGrid"></div>
  </div>
  <div class="sidebar">
    <h2><span class="dot"></span>今日创作灵感</h2>
    <div class="topic-chart" id="topicChart"></div>
    <div class="insp-list" id="inspList"></div>
  </div>
</div>

<div class="modal-overlay" id="modalOverlay">
  <div class="modal" id="modal"></div>
</div>

<script>
const DATA = __DATA__;

const TOPIC_COLORS = {
  '职场': '#00d4aa','认知': '#6c5ce7','学业': '#ffa94d',
  '情感': '#ff6b9d','金钱': '#ffd43b','人生': '#4dabf7'
};

let state = { blogger: '全部', sort: 'hot', search: '' };

// ===== 格式化数字 =====
function fmtNum(n) {
  if (!n) return '0';
  if (n >= 100000000) return (n/100000000).toFixed(1) + '亿';
  if (n >= 10000) return (n/10000).toFixed(1) + '万';
  return n.toString();
}
function fmtDuration(dur) {
  if (!dur) return '';
  const s = String(dur).trim();
  // B站搜索返回的duration是字符串如 "05:32" 或 "128:05"
  if (s.includes(':')) return s;
  const sec = Number(s);
  if (isNaN(sec)) return '';
  const m = Math.floor(sec/60), rm = sec%60;
  return m + ':' + (rm<10?'0':'') + rm;
}
function fmtDate(ts) {
  if (!ts) return '';
  // B站接口返回可能是秒级时间戳，也可能是字符串日期，统一处理
  let d;
  if (typeof ts === 'number') {
    d = new Date(ts * 1000);
  } else if (String(ts).length === 10 && !isNaN(Number(ts))) {
    d = new Date(Number(ts) * 1000);
  } else if (String(ts).length === 13 && !isNaN(Number(ts))) {
    d = new Date(Number(ts));
  } else if (String(ts).includes('-')) {
    d = new Date(ts);
  } else {
    return '';
  }
  if (isNaN(d.getTime())) return '';
  return (d.getMonth()+1) + '月' + d.getDate() + '日';
}

// ===== 渲染Tabs =====
function renderTabs() {
  const box = document.getElementById('tabsBox');
  const bloggers = ['全部', ...DATA.bloggers, '话题精选', 'B站热门'];
  let html = '';
  for (const b of bloggers) {
    const count = b === '全部' ? DATA.total_videos : (DATA.by_blogger[b] || 0);
    if (count === 0) continue;
    const active = state.blogger === b ? ' active' : '';
    html += `<span class="tab${active}" onclick="selectBlogger('${b}')">${b}<span class="count">${count}</span></span>`;
  }
  box.innerHTML = html;
}

function selectBlogger(b) {
  state.blogger = b;
  renderTabs();
  renderCards();
}

// ===== 排序 =====
document.addEventListener('click', e => {
  if (e.target.classList.contains('sort-opt')) {
    document.querySelectorAll('.sort-opt').forEach(el => el.classList.remove('active'));
    e.target.classList.add('active');
    state.sort = e.target.dataset.sort;
    renderCards();
  }
});

// ===== 搜索 =====
document.getElementById('searchInput').addEventListener('input', e => {
  state.search = e.target.value.toLowerCase();
  renderCards();
});

// ===== 渲染卡片 =====
function getFiltered() {
  let list = [...DATA.content];
  if (state.blogger !== '全部') {
    list = list.filter(v => v.target_blogger === state.blogger);
  }
  if (state.search) {
    const q = state.search;
    list = list.filter(v =>
      (v.title||'').toLowerCase().includes(q) ||
      (v.author||'').toLowerCase().includes(q) ||
      (v.ai_summary||'').toLowerCase().includes(q) ||
      (v.ai_topic||'').toLowerCase().includes(q)
    );
  }
  const sortKey = state.sort === 'play' ? 'play' : state.sort === 'like' ? 'like' : state.sort === 'interact' ? 'interact_score' : 'hot_score';
  list.sort((a,b) => (b[sortKey]||0) - (a[sortKey]||0));
  return list;
}

function renderCards() {
  const grid = document.getElementById('cardGrid');
  const list = getFiltered();
  const statsBox = document.getElementById('statsBox');

  if (list.length === 0) {
    grid.innerHTML = '<div class="empty"><div class="emoji">🔍</div>没有匹配的内容</div>';
    statsBox.innerHTML = '';
    return;
  }

  statsBox.innerHTML = `<span>共 <b>${list.length}</b> 条</span>`;

  let html = '';
  list.forEach((v, i) => {
    const isCore = v.blogger_weight === 1;
    const isOwner = v.is_owner;
    const rankBadge = i < 3 ? `<div class="rank-badge">TOP${i+1}</div>` : '';
    const topicTag = v.ai_topic ? `<span class="tag topic">${v.ai_topic}</span>` : '';
    const coreTag = isCore ? `<span class="tag core">核心</span>` : '';
    const ownerTag = isOwner ? `<span class="tag" style="background:#1a4731;color:#00d4aa">本人</span>` : '';
    const bloggerTag = v.target_blogger ? `<span class="tag">${v.target_blogger}</span>` : '';

    html += `<div class="card" onclick="openModal(${v._idx})">
      <div class="thumb">
        ${v.pic ? `<img src="${v.pic}" loading="lazy" onerror="this.style.display='none'">` : ''}
        ${rankBadge}
        ${v.duration ? `<div class="duration">${fmtDuration(v.duration)}</div>` : ''}
      </div>
      <div class="body">
        <div class="author">${v.author || v.target_blogger} · ${fmtDate(v.pubdate)}</div>
        <div class="title">${v.title || ''}</div>
        <div class="summary">${v.ai_summary || v.desc || ''}</div>
        <div class="tags">${coreTag}${ownerTag}${topicTag}${bloggerTag}</div>
        <div class="meta">
          <span class="stat">▶ ${fmtNum(v.play)}</span>
          <span class="stat">👍 ${fmtNum(v.like)}</span>
          <span class="stat">⭐ ${fmtNum(v.favorite)}</span>
          <span class="stat">💬 ${fmtNum(v.reply)}</span>
        </div>
      </div>
    </div>`;
  });
  grid.innerHTML = html;
}

// ===== 弹窗 =====
function openModal(idx) {
  const v = DATA.content.find(x => x._idx === idx);
  if (!v) return;
  const modal = document.getElementById('modal');
  const overlay = document.getElementById('modalOverlay');

  let inspHtml = '';
  if (v.ai_inspiration && v.ai_inspiration.length) {
    inspHtml = '<div class="section"><div class="section-label">💡 创作角度建议</div>';
    v.ai_inspiration.forEach(insp => {
      inspHtml += `<div class="insp-item">${insp}</div>`;
    });
    inspHtml += '</div>';
  }

  modal.innerHTML = `
    <div class="modal-header">
      ${v.pic ? `<img src="${v.pic}" onerror="this.style.display='none'">` : ''}
      <button class="modal-close" onclick="closeModal()">×</button>
    </div>
    <div class="modal-body">
      <h3>${v.title || ''}</h3>
      <div class="meta-row">
        <span class="stat">UP主: <b>${v.author || ''}</b></span>
        <span class="stat">发布: <b>${fmtDate(v.pubdate)}</b></span>
        <span class="stat">时长: <b>${fmtDuration(v.duration)}</b></span>
      </div>
      <div class="meta-row">
        <span class="stat">▶ 播放 <b>${fmtNum(v.play)}</b></span>
        <span class="stat">👍 点赞 <b>${fmtNum(v.like)}</b></span>
        <span class="stat">⭐ 收藏 <b>${fmtNum(v.favorite)}</b></span>
        <span class="stat">💬 评论 <b>${fmtNum(v.reply)}</b></span>
      </div>
      <div class="section">
        <div class="section-label">📋 AI摘要</div>
        <div class="section-content">${v.ai_summary || ''}</div>
      </div>
      ${v.ai_quote ? `<div class="section"><div class="section-label">💬 金句</div><div class="quote-box">"${v.ai_quote}"</div></div>` : ''}
      <div class="section">
        <div class="section-label">🏷️ 标签</div>
        <div class="tags">
          <span class="tag topic">${v.ai_topic || ''}</span>
          ${v.is_owner ? '<span class="tag" style="background:#1a4731;color:#00d4aa">博主本人</span>' : ''}
          <span class="tag">${v.target_blogger || ''}</span>
        </div>
      </div>
      ${inspHtml}
      <a class="open-link" href="${v.url || '#'}" target="_blank">在B站观看 →</a>
    </div>
  `;
  overlay.classList.add('show');
}

function closeModal() {
  document.getElementById('modalOverlay').classList.remove('show');
}
document.getElementById('modalOverlay').addEventListener('click', e => {
  if (e.target.id === 'modalOverlay') closeModal();
});
document.addEventListener('keydown', e => { if (e.key === 'Escape') closeModal(); });

// ===== 侧栏：创作灵感 =====
function renderSidebar() {
  // 主题分布图
  const chart = document.getElementById('topicChart');
  const stats = DATA.topic_stats || {};
  const maxVal = Math.max(...Object.values(stats), 1);
  let chartHtml = '';
  for (const [topic, count] of Object.entries(stats).sort((a,b) => b[1]-a[1])) {
    const color = TOPIC_COLORS[topic] || '#8b8fa3';
    const pct = (count / maxVal * 100).toFixed(0);
    chartHtml += `<div class="topic-bar">
      <span class="label">${topic}</span>
      <div class="bar-bg"><div class="bar-fill" style="width:${pct}%;background:${color}"></div></div>
      <span class="num">${count}</span>
    </div>`;
  }
  chart.innerHTML = chartHtml ? '<div style="font-size:12px;color:var(--text-dim);margin-bottom:8px;">主题分布</div>' + chartHtml : '';

  // 灵感列表
  const inspList = document.getElementById('inspList');
  const insps = DATA.daily_inspirations || [];
  let inspHtml = '';
  insps.forEach(insp => {
    inspHtml += `<div class="insp-card topic-${insp.topic}">
      <div class="insp-text">${insp.inspiration}</div>
      <div class="insp-meta">来源: <span class="src">${insp.source}</span> · ${insp.topic}</div>
    </div>`;
  });
  inspList.innerHTML = inspHtml || '<div class="empty"><div>暂无灵感</div></div>';
}

// ===== 初始化 =====
function init() {
  document.getElementById('dateStr').textContent = '📅 ' + DATA.date + ' · 数据抓取于 ' + DATA.fetched_at.slice(11,16);
  // 给每条content加_idx方便弹窗查找
  DATA.content.forEach((v, i) => { v._idx = i; });
  renderTabs();
  renderCards();
  renderSidebar();
}
init();
</script>
<script>
if ('serviceWorker' in navigator) {
  const swCode = `
    const CACHE='workbench-v1';
    self.addEventListener('install',e=>{self.skipWaiting()});
    self.addEventListener('activate',e=>{e.waitUntil(self.clients.claim())});
    self.addEventListener('fetch',e=>{
      if(e.request.method!=='GET')return;
      e.respondWith(
        caches.match(e.request).then(r=>r||fetch(e.request).then(res=>{
          try{const clone=res.clone();caches.open(CACHE).then(c=>c.put(e.request,clone))}catch(err){}
          return res;
        }).catch(()=>r))
      );
    });
  `;
  const blob = new Blob([swCode], {type:'application/javascript'});
  const swUrl = URL.createObjectURL(blob);
  navigator.serviceWorker.register(swUrl).catch(()=>{});
}
</script>
</body>
</html>
"""

    # PWA manifest 和 icon
    svg_raw = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"><rect width="512" height="512" rx="112" fill="#0f1117"/><text x="256" y="370" font-size="300" text-anchor="middle">🔥</text></svg>'
    icon_encoded = urllib.parse.quote(svg_raw, safe='')

    manifest = json.dumps({
        "name": "爆款素材工作台",
        "short_name": "爆款工作台",
        "description": "每日抓取B站高赞爆款素材，为创作提供灵感",
        "start_url": "/",
        "display": "standalone",
        "orientation": "portrait",
        "background_color": "#0f1117",
        "theme_color": "#0f1117",
        "icons": [{"src": "data:image/svg+xml;utf8," + icon_encoded, "sizes": "any", "type": "image/svg+xml", "purpose": "any maskable"}]
    }, ensure_ascii=False)
    manifest_encoded = urllib.parse.quote(manifest, safe='')

    html = (html
            .replace("__DATA__", data_json)
            .replace("__DATE__", data["date"])
            .replace("__MANIFEST__", manifest_encoded)
            .replace("__ICON__", icon_encoded)
    )
    return html


if __name__ == "__main__":
    data = json.load(open(Path(__file__).parent / "daily_data.json", encoding="utf-8"))
    html = generate_html(data)
    out = Path(__file__).parent / "工作台.html"
    out.write_text(html, encoding="utf-8")
    print(f"已生成: {out}  ({len(html)//1024}KB)")
