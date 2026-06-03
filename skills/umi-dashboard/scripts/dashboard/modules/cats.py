"""Cats diary module, daily cat logs and memories."""
import calendar
import html
import io
import json
import os
import sqlite3
from collections import Counter, defaultdict
from datetime import datetime
from urllib.parse import parse_qs

import matplotlib
matplotlib.use('Agg')
from matplotlib import font_manager
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

matplotlib.rcParams['font.sans-serif'] = ['WenQuanYi Zen Hei', 'Noto Sans CJK SC', 'Noto Sans CJK JP', 'SimHei', 'Microsoft YaHei', 'DejaVu Sans']
matplotlib.rcParams['font.family'] = 'sans-serif'
matplotlib.rcParams['axes.unicode_minus'] = False
CJK_FONT = font_manager.FontProperties(family='WenQuanYi Zen Hei')

ROUTE = '/cats'
TITLE = '🐱 Cat Diary'
ICON = '🐱'
DESCRIPTION = '猫猫日记 · 日常记录'

from common import CATS_DIARY_DB_PATH, CATS_PROFILES_DB_PATH

PROFILES_DB = str(CATS_PROFILES_DB_PATH)
DIARY_DB = str(CATS_DIARY_DB_PATH)
REQUEST_QUERY = ''
COMMON_TAGS = ['呕吐', '吐毛球', '拉肚子', '软便', '食欲差', '没精神', '打喷嚏', '咳嗽', '吃药', '看医生']


def set_request_query(query):
    global REQUEST_QUERY
    REQUEST_QUERY = query or ''


def _current_year_month():
    now = datetime.now()
    return now.strftime('%Y'), now.strftime('%Y-%m')


def _params():
    parsed = parse_qs(REQUEST_QUERY, keep_blank_values=False)
    current_year, current_month = _current_year_month()
    return {
        'cat': (parsed.get('cat') or [''])[0],
        'year': (parsed.get('year') or [current_year])[0],
        'month': (parsed.get('month') or [current_month])[0],
        'q': (parsed.get('q') or [''])[0],
        'ok': (parsed.get('ok') or [''])[0],
        'range': (parsed.get('range') or ['all'])[0],
        'prefill_content': (parsed.get('prefill_content') or [''])[0],
        'prefill_tag': (parsed.get('prefill_tag') or [''])[0],
        'prefill_date': (parsed.get('prefill_date') or [''])[0],
        'day': (parsed.get('day') or [''])[0],
    }


def _profiles():
    conn = sqlite3.connect(PROFILES_DB)
    conn.row_factory = sqlite3.Row
    rows = [dict(r) for r in conn.execute('SELECT * FROM cats ORDER BY birthday').fetchall()]
    conn.close()
    return rows


def _load_entries(cat_filter='', month_filter='', q=''):
    conn = sqlite3.connect(DIARY_DB)
    conn.row_factory = sqlite3.Row
    sql = '''
        SELECT e.*
        FROM diary_entries e
        WHERE 1=1
    '''
    args = []
    if month_filter:
        sql += ' AND substr(e.entry_date, 1, 7) = ?'
        args.append(month_filter)
    if q:
        sql += ' AND (e.content LIKE ? OR ifnull(e.symptom,"") LIKE ? OR ifnull(e.notes,"") LIKE ? OR ifnull(e.food,"") LIKE ? OR ifnull(e.stool,"") LIKE ? OR ifnull(e.medication,"") LIKE ? OR EXISTS (SELECT 1 FROM entry_tags t WHERE t.entry_id = e.id AND t.tag LIKE ?))'
        like = f'%{q}%'
        args.extend([like] * 7)
    sql += ' ORDER BY e.entry_date DESC, e.id DESC'
    rows = [dict(r) for r in conn.execute(sql, args).fetchall()]
    filtered = []
    for row in rows:
        cats = [r[0] for r in conn.execute('SELECT cat_name FROM entry_cats WHERE entry_id = ? ORDER BY cat_name', (row['id'],)).fetchall()]
        tags = [r[0] for r in conn.execute('SELECT tag FROM entry_tags WHERE entry_id = ? ORDER BY tag', (row['id'],)).fetchall()]
        row['cats'] = cats
        row['tags'] = tags
        if cat_filter and cat_filter not in cats:
            continue
        filtered.append(row)
    conn.close()
    return filtered


def _all_months():
    conn = sqlite3.connect(DIARY_DB)
    rows = [r[0] for r in conn.execute('SELECT DISTINCT substr(entry_date, 1, 7) AS ym FROM diary_entries WHERE entry_date IS NOT NULL AND entry_date != "" ORDER BY ym DESC').fetchall()]
    conn.close()
    return rows


def _all_years(months):
    years = sorted({m[:4] for m in months if m and len(m) >= 4}, reverse=True)
    current_year, _ = _current_year_month()
    if current_year not in years:
        years.insert(0, current_year)
    return years


def _calendar_grid(entries, month_filter):
    if not month_filter:
        return ''
    year, month = month_filter.split('-')
    cal = calendar.monthcalendar(int(year), int(month))
    day_map = defaultdict(list)
    for e in entries:
        if (e.get('entry_date') or '').startswith(month_filter):
            day = int(e['entry_date'][-2:])
            day_map[day].append(e)
    cells = ''
    weekday_names = ['一', '二', '三', '四', '五', '六', '日']
    header = ''.join(f'<div class="calendar-head">{d}</div>' for d in weekday_names)
    for week in cal:
        for day in week:
            if day == 0:
                cells += '<div class="calendar-cell empty-cell"></div>'
                continue
            visible_entries = [e for e in day_map.get(day, []) if '体重' not in (e.get('tags') or [])]
            items = ''.join(
                f'<div class="calendar-item {("cat-moscar" if "Moscar" in e.get("cats", []) else "cat-nomi")}">'
                f'<span class="calendar-note">{html.escape((e.get("tags") or [e.get("content") or "记录"])[0])}</span></div>'
                for e in visible_entries[:3]
            )
            more = ''
            if len(visible_entries) > 3:
                more = f'<div class="calendar-more">+{len(visible_entries) - 3} 条</div>'
            cells += f'<div class="calendar-cell"><div class="calendar-day">{day}</div>{items}{more}</div>'
    return f'<h2>🗓️ 月历视图</h2><div class="calendar-grid">{header}{cells}</div>'


def _save_entry(query):
    parsed = parse_qs(query, keep_blank_values=True)
    if parsed.get('action', [''])[0] != 'add':
        return
    date = (parsed.get('date') or [''])[0].strip()
    cats = [c for c in parsed.get('cat') if c.strip()]
    content = (parsed.get('content') or [''])[0].strip()
    if not date or not cats or not content:
        return
    mood = (parsed.get('mood') or [''])[0].strip()
    food = (parsed.get('food') or [''])[0].strip()
    stool = (parsed.get('stool') or [''])[0].strip()
    weight = (parsed.get('weight') or [''])[0].strip()
    medication = (parsed.get('medication') or [''])[0].strip()
    notes = (parsed.get('notes') or [''])[0].strip()
    tags = [t.strip() for t in parsed.get('tag') if t.strip()]
    extra_tags = [t.strip() for t in (parsed.get('extra_tags') or [''])[0].split(',') if t.strip()]
    all_tags = sorted(set(tags + extra_tags))
    symptom = '、'.join(all_tags)
    conn = sqlite3.connect(DIARY_DB)
    cur = conn.execute(
        'INSERT INTO diary_entries (entry_date, content, mood, symptom, food, stool, weight, medication, notes) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
        (date, content, mood, symptom, food, stool, float(weight) if weight else None, medication, notes)
    )
    entry_id = cur.lastrowid
    for cat in cats:
        conn.execute('INSERT OR IGNORE INTO entry_cats (entry_id, cat_name) VALUES (?, ?)', (entry_id, cat))
    for tag in all_tags:
        conn.execute('INSERT OR IGNORE INTO entry_tags (entry_id, tag) VALUES (?, ?)', (entry_id, tag))
    conn.commit()
    conn.close()


def is_enabled():
    return os.path.exists(PROFILES_DB) and os.path.exists(DIARY_DB)


def nav():
    return '<a href="/">🩵 UMI</a><span class="sep">›</span><span>Cat Diary</span>'


def render_weight_chart(params=None):
    params = params or _params()
    entries = _load_entries(params.get('cat', ''), params.get('month', ''), params.get('q', ''))
    weight_entries = [e for e in entries if '体重' in (e.get('tags') or []) and e.get('weight') not in (None, '')]
    if not weight_entries:
        return None

    range_map = {'3m': 3, '1y': 12, 'all': None}
    selected_range = params.get('range') or 'all'
    months_limit = range_map.get(selected_range)

    rows = []
    for e in sorted(weight_entries, key=lambda x: x.get('entry_date') or ''):
        for cat in e.get('cats', []):
            rows.append({'date': e.get('entry_date'), 'cat': cat, 'weight': float(e.get('weight'))})
    if not rows:
        return None

    df = pd.DataFrame(rows)
    df['date'] = pd.to_datetime(df['date'])
    if months_limit is not None and not df.empty:
        max_date = df['date'].max()
        cutoff = max_date - pd.DateOffset(months=months_limit)
        df = df[df['date'] >= cutoff].copy()
    sns.set_theme(style='whitegrid')
    fig, ax = plt.subplots(figsize=(8, 4.8), dpi=140)
    palette = {'Moscar': '#5b8def', 'Nomi': '#e67aa4', 'Nomi（糯米）': '#e67aa4'}
    sns.lineplot(data=df, x='date', y='weight', hue='cat', marker='o', linewidth=2.2, palette=palette, ax=ax)
    ax.set_xlabel('日期', fontproperties=CJK_FONT)
    ax.set_ylabel('体重 (kg)', fontproperties=CJK_FONT)
    ax.tick_params(axis='x', rotation=45)
    legend = ax.legend(title='猫咪')
    if legend:
        legend.get_title().set_fontproperties(CJK_FONT)
        for text in legend.get_texts():
            text.set_fontproperties(CJK_FONT)
    fig.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight')
    plt.close(fig)
    return buf.getvalue()


def _build_state():
    cats_info = _profiles()
    entries = _load_entries('', '', '')
    months = _all_months()
    cat_names = [c.get('display_name') or c.get('name') for c in cats_info]
    return {
        'profiles': cats_info,
        'entries': entries,
        'months': months,
        'years': _all_years(months),
        'cat_names': cat_names,
    }


def render_json():
    state = _build_state()
    state['params'] = _params()
    return json.dumps(state, ensure_ascii=False).encode('utf-8')


def render():
    if REQUEST_QUERY:
        _save_entry(REQUEST_QUERY)
    params = _params()
    state = _build_state()
    state['params'] = params
    initial_state = html.escape(json.dumps(state, ensure_ascii=False))

    cat_names = state['cat_names']
    add_cat_checks = ''.join(
        f'<label class="check-pill"><input type="checkbox" name="cat" value="{html.escape(name)}"> <span>{html.escape(name)}</span></label>'
        for name in cat_names
    )
    tag_checks = ''.join(
        f'<label class="check-pill"><input type="checkbox" name="tag" value="{html.escape(tag)}"> <span>{html.escape(tag)}</span></label>'
        for tag in COMMON_TAGS
    )
    today = pd.Timestamp.now().strftime('%Y-%m-%d')
    add_form_html = f'''<details class="entry-panel" {'open' if params['ok'] == '1' else ''}>
    <summary>➕ 添加记录 {"<span class='save-ok'>已保存 ✅</span>" if params['ok'] == '1' else ''}</summary>
    <form class="entry-form" method="get" action="/cats">
        <input type="hidden" name="action" value="add">
        <input type="hidden" name="ok" value="1">
        <div class="form-grid">
            <label><span>日期</span><input type="date" name="date" value="{html.escape(params['prefill_date'])}" required></label>
            <label><span>心情</span><select name="mood"><option value="">-</option><option value="happy">开心</option><option value="sleepy">困</option><option value="sick">不舒服</option><option value="playful">活泼</option><option value="naughty">淘气</option></select></label>
            <label class="wide"><span>猫咪</span><div class="pill-group">{add_cat_checks}</div></label>
            <label class="wide"><span>记录内容</span><textarea name="content" rows="3" placeholder="比如：今天吐毛球，精神还可以" required>{html.escape(params['prefill_content'])}</textarea></label>
            <label><span>饮食</span><input type="text" name="food" placeholder="吃了什么"></label>
            <label><span>便便</span><input type="text" name="stool" placeholder="正常/软便/拉肚子"></label>
            <label><span>体重 kg</span><input type="number" name="weight" step="0.01" placeholder="4.25"></label>
            <label><span>用药</span><input type="text" name="medication" placeholder="药名"></label>
            <label class="wide"><span>症状标签</span><div class="pill-group">{tag_checks}</div></label>
            {f'<input type="hidden" name="tag" value="{html.escape(params["prefill_tag"])}">' if params['prefill_tag'] else ''}
            <label class="wide"><span>补充标签</span><input type="text" name="extra_tags" placeholder="多个标签用逗号隔开"></label>
            <label class="wide"><span>备注</span><textarea name="notes" rows="2" placeholder="别的细节"></textarea></label>
        </div>
        <button class="submit-btn" type="submit">保存记录</button>
    </form>
</details>'''

    return f'''<h1>🐱 Cat Diary</h1>
<div id="cats-app" data-initial-state="{initial_state}"></div>
<div id="cats-add-form">{add_form_html}</div>
<script>
(function() {{
const root = document.getElementById('cats-app');
if (!root) return;
const state = JSON.parse(root.dataset.initialState || '{{}}');
const moodMap = {{happy: '😸', sleepy: '😴', sick: '🤒', playful: '😸', naughty: '😾'}};
const quickActions = [
  {{label: '吐毛球', content: '吐毛球', tag: '吐毛球'}},
  {{label: '软便', content: '软便', tag: '软便'}},
  {{label: '食欲差', content: '食欲差', tag: '食欲差'}},
  {{label: '称重', content: '称重', tag: '体重'}},
];

function esc(value) {{
  return String(value ?? '').replace(/[&<>"']/g, (ch) => ({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}}[ch]));
}}

function formatAge(birthdayRaw) {{
  if (!birthdayRaw) return '';
  const bday = new Date(birthdayRaw);
  if (Number.isNaN(bday.getTime())) return '';
  const now = new Date();
  let months = (now.getFullYear() - bday.getFullYear()) * 12 + (now.getMonth() - bday.getMonth());
  if (now.getDate() < bday.getDate()) months -= 1;
  months = Math.max(months, 0);
  const years = Math.floor(months / 12);
  const rem = months % 12;
  if (years > 0 && rem > 0) return `${{years}}岁${{rem}}个月`;
  if (years > 0) return `${{years}}岁`;
  return `${{rem}}个月`;
}}

function currentParams() {{
  return state.params || {{cat:'',year:'',month:'',q:'',range:'all'}};
}}

function monthsForYear(year) {{
  return (state.months || []).filter((month) => !year || month.startsWith(year + '-'));
}}

function syncMonthForYear() {{
  const p = currentParams();
  const months = monthsForYear(p.year);
  if (p.month && months.includes(p.month)) return;
  p.month = months[0] || '';
}}

function filteredEntries() {{
  const p = currentParams();
  return (state.entries || []).filter((entry) => {{
    if (p.cat && !(entry.cats || []).includes(p.cat)) return false;
    if (p.month && !(entry.entry_date || '').startsWith(p.month)) return false;
    if (p.q) {{
      const blob = [entry.content, entry.symptom, entry.notes, entry.food, entry.stool, entry.medication, String(entry.weight || ''), ...(entry.tags || [])].join(' ');
      if (!blob.includes(p.q)) return false;
    }}
    return true;
  }});
}}

function nonWeightEntries(entries) {{
  return entries.filter((entry) => !(entry.tags || []).includes('体重'));
}}

function weightEntries(entries) {{
  return entries.filter((entry) => (entry.tags || []).includes('体重') && entry.weight !== null && entry.weight !== '');
}}

function updateUrl(extra = {{}}) {{
  const p = currentParams();
  const params = new URLSearchParams();
  for (const key of ['cat', 'year', 'month', 'q', 'range', 'ok', 'prefill_content', 'prefill_tag', 'prefill_date', 'day']) {{
    const value = extra[key] !== undefined ? extra[key] : p[key];
    if (value) params.set(key, value);
  }}
  history.replaceState(null, '', '/cats' + (params.toString() ? '?' + params.toString() : ''));
}}

function profileHtml(info) {{
  const catName = info.display_name || info.name || '';
  const active = currentParams().cat === catName ? ' active' : '';
  const avatar = info.photo
    ? `<img class="cat-photo" src="/cat-photos/${{esc(info.photo)}}" alt="${{esc(catName)}}" loading="lazy">`
    : `<div class="cat-avatar">${{esc(info.emoji || '🐱')}}</div>`;
  const age = formatAge(info.birthday || '');
  return `<button class="cat-profile-link" type="button" data-cat-profile="${{esc(catName)}}"><div class="cat-profile${{active}}">
    ${{avatar}}
    <h3>${{esc(catName)}}</h3>
    <p>${{esc(info.breed || '')}}</p>
    <p class="cat-detail">${{esc(info.birthday || '')}}</p>
    ${{age ? `<p class="cat-detail">${{esc(age)}}</p>` : ''}}
  </div></button>`;
}}

function statsHtml(entries) {{
  const plain = nonWeightEntries(entries);
  const weights = weightEntries(entries);
  const latestWeights = new Map();
  const alerts = [];
  for (const cat of state.cat_names || []) {{
    const points = weights
      .filter((entry) => (entry.cats || []).includes(cat))
      .map((entry) => [entry.entry_date || '', Number(entry.weight)])
      .sort((a, b) => a[0].localeCompare(b[0]));
    if (points.length) latestWeights.set(cat, `${{points[points.length - 1][1].toFixed(2)}} kg`);
    if (points.length >= 2) {{
      const delta = points[points.length - 1][1] - points[points.length - 2][1];
      if (delta <= -0.15) alerts.push(`${{cat}} 最近一次下降 ${{Math.abs(delta).toFixed(2)}} kg`);
    }}
  }}
  const cards = [
    ['Moscar 记录', String(plain.filter((entry) => (entry.cats || []).includes('Moscar')).length)],
    ['Nomi 记录', String(plain.filter((entry) => (entry.cats || []).includes('Nomi（糯米）')).length)],
    ['最新体重', [...latestWeights.entries()].map(([k, v]) => `${{k}} ${{v}}`).join(' · ') || '暂无'],
    ['异常提醒', alerts.join('；') || '暂无明显异常'],
  ];
  return `<h2>📊 健康概览</h2><div class="stats-grid">${{cards.map(([k, v]) => `<div class="stat-card"><div class="stat-label">${{esc(k)}}</div><div class="stat-value">${{esc(v)}}</div></div>`).join('')}}</div>`;
}}

function quickActionsHtml() {{
  const p = currentParams();
  const today = new Date().toISOString().slice(0, 10);
  const buttons = quickActions.map((item) => `<button class="quick-action-btn" type="button" data-quick-content="${{esc(item.content)}}" data-quick-tag="${{esc(item.tag)}}" data-quick-date="${{today}}">${{esc(item.label)}}</button>`).join('');
  return `<h2>⚡ 快速记录</h2><div class="pill-group quick-actions">${{buttons}}</div><p class="cat-detail">点按钮会自动填今天日期和常用内容，你补细节再保存。</p>`;
}}

function filterBarHtml() {{
  const p = currentParams();
  const catOptions = ['<option value="">全部猫咪</option>'].concat((state.cat_names || []).map((name) => `<option value="${{esc(name)}}" ${{p.cat === name ? 'selected' : ''}}>${{esc(name)}}</option>`)).join('');
  const yearOptions = ['<option value="">全部年份</option>'].concat((state.years || []).map((year) => `<option value="${{esc(year)}}" ${{p.year === year ? 'selected' : ''}}>${{esc(year)}}</option>`)).join('');
  const monthOptions = ['<option value="">全部月份</option>'].concat(monthsForYear(p.year).map((month) => `<option value="${{esc(month)}}" ${{p.month === month ? 'selected' : ''}}>${{esc(month)}}</option>`)).join('');
  return `<h2>🔎 快速筛选</h2>
  <form class="filter-bar" id="cats-filter-form">
    <select name="cat">${{catOptions}}</select>
    <select name="year">${{yearOptions}}</select>
    <select name="month">${{monthOptions}}</select>
    <input type="text" name="q" placeholder="搜症状、饮食、备注" value="${{esc(p.q || '')}}">
    <button type="submit">筛选</button>
    <button class="filter-reset" type="button" data-filter-reset>重置</button>
  </form>`;
}}

function symptomHtml(entries) {{
  const counter = new Map();
  for (const entry of entries) {{
    for (const tag of entry.tags || []) {{
      if (tag === '体重') continue;
      counter.set(tag, (counter.get(tag) || 0) + 1);
    }}
  }}
  const top = [...counter.entries()].sort((a, b) => b[1] - a[1]).slice(0, 6);
  if (!top.length) return '';
  return '<h2>📈 症状统计</h2><div class="stats-grid">' + top.map(([tag, count]) => `<div class="stat-card"><div class="stat-label">${{esc(tag)}}</div><div class="stat-value">${{count}} 次</div></div>`).join('') + '</div>';
}}

function chartHtml(entries) {{
  const weights = weightEntries(entries);
  if (!weights.length) return '<h2>⚖️ 体重折线图</h2><div class="weight-chart-card"><p class="empty">当前月份还没有体重记录～</p></div>';
  const p = currentParams();
  const rangeButtons = [['3m', '最近3个月'], ['1y', '最近1年'], ['all', '全部']].map(([key, label]) => `<button class="range-chip ${{(p.range || 'all') === key ? 'active' : ''}}" type="button" data-range="${{key}}">${{label}}</button>`).join('');
  const chartMonth = weights.map((entry) => entry.entry_date || '').filter(Boolean).sort().slice(-1)[0]?.slice(0, 7) || '';
  const chartParams = new URLSearchParams({{cat: p.cat || '', month: chartMonth, q: p.q || '', range: p.range || 'all', v: Date.now().toString()}});
  return `<h2>⚖️ 体重折线图</h2><div class="range-chip-row">${{rangeButtons}}</div><div class="weight-chart-card"><img id="weight-chart-img" class="weight-chart" src="/cats/weight-chart.png?${{chartParams.toString()}}" alt="体重折线图"></div>`;
}}

function calendarHtml(entries) {{
  const p = currentParams();
  const month = p.month || ((state.months || [])[0] || '');
  if (!month) return '';
  const parts = month.split('-');
  if (parts.length !== 2) return '';
  const year = Number(parts[0]);
  const monthIndex = Number(parts[1]);
  if (!year || !monthIndex) return '';
  const first = new Date(year, monthIndex - 1, 1);
  const lastDay = new Date(year, monthIndex, 0).getDate();
  const jsStart = (first.getDay() + 6) % 7;
  const dayMap = new Map();
  for (const entry of entries) {{
    if ((entry.entry_date || '').startsWith(month)) {{
      const day = Number((entry.entry_date || '').slice(-2));
      if (!dayMap.has(day)) dayMap.set(day, []);
      dayMap.get(day).push(entry);
    }}
  }}
  const header = ['一','二','三','四','五','六','日'].map((d) => `<div class="calendar-head">${{d}}</div>`).join('');
  const cells = [];
  for (let i = 0; i < jsStart; i++) cells.push('<div class="calendar-cell empty-cell"></div>');
  for (let day = 1; day <= lastDay; day++) {{
    const items = (dayMap.get(day) || []).slice(0, 3).map((entry) => `<div class="calendar-item ${{(entry.cats || []).includes('Moscar') ? 'cat-moscar' : 'cat-nomi'}}"><span class="calendar-note">${{esc(((entry.tags || [])[0] || entry.content || '记录'))}}</span></div>`).join('');
    const moreCount = Math.max((dayMap.get(day) || []).length - 3, 0);
    const active = currentParams().day === String(day).padStart(2, '0') ? ' selected-day' : '';
    cells.push(`<button type="button" class="calendar-cell calendar-button${{active}}" data-calendar-day="${{String(day).padStart(2, '0')}}"><div class="calendar-day">${{day}}</div>${{items}}${{moreCount ? `<div class="calendar-more">+${{moreCount}} 条</div>` : ''}}</button>`);
  }}
  return `<h2>🗓️ 月历视图</h2><div class="calendar-grid">${{header}}${{cells.join('')}}</div>`;
}}

function diaryHtml(entries) {{
  const plain = nonWeightEntries(entries);
  const selectedDay = currentParams().day || '';
  if (!plain.length) return '<h2>📝 日记</h2><div class="diary-list"><p class="empty">当前筛选下还没有记录～</p></div>';
  let currentMonth = '';
  const rows = [];
  for (const entry of plain) {{
    const date = entry.entry_date || '';
    if (selectedDay && date.slice(-2) !== selectedDay) continue;
    const month = date.slice(0, 7);
    if (month && month !== currentMonth) {{
      currentMonth = month;
      rows.push(`<h3 class="month-header">${{esc(month)}}</h3>`);
    }}
    const catTags = (entry.cats || []).map((cat) => `<span class="cat-tag-diary">${{esc(cat)}}</span>`).join('');
    const tags = (entry.tags || []).map((tag) => `<span class="entry-tag">${{esc(tag)}}</span>`).join('');
    const extras = [['饮食', 'food'], ['便便', 'stool'], ['用药', 'medication'], ['备注', 'notes']]
      .map(([label, key]) => entry[key] ? `<li><strong>${{label}}</strong> ${{esc(entry[key])}}</li>` : '')
      .join('');
    rows.push(`<div class="diary-entry"><div class="diary-header"><span class="diary-date">${{esc(date)}}</span>${{catTags}}${{entry.mood ? `<span class="diary-mood">${{moodMap[entry.mood] || ''}}</span>` : ''}}</div><p class="diary-content">${{esc(entry.content || '')}}</p>${{tags ? `<div class="entry-tag-row">${{tags}}</div>` : ''}}${{extras ? `<ul>${{extras}}</ul>` : ''}}</div>`);
  }}
  return '<h2>📝 日记</h2><div class="diary-list">' + rows.join('') + '</div>';
}}

function render() {{
  syncMonthForYear();
  const entries = filteredEntries();
  root.innerHTML = `<p class="stats">共 ${{(state.profiles || []).length}} 只猫 · ${{entries.length}} 条匹配记录</p>
    ${{state.profiles && state.profiles.length ? `<h2>🐈 猫咪们</h2><div class="cat-grid">${{state.profiles.map(profileHtml).join('')}}</div>` : ''}}
    ${{statsHtml(entries)}}
    ${{quickActionsHtml()}}
    ${{filterBarHtml()}}
    ${{symptomHtml(entries)}}
    ${{chartHtml(entries)}}
    ${{calendarHtml(nonWeightEntries(entries))}}
    ${{diaryHtml(entries)}}`;
}}

root.addEventListener('click', (event) => {{
  const profile = event.target.closest('[data-cat-profile]');
  if (profile) {{
    const cat = profile.dataset.catProfile || '';
    state.params.cat = state.params.cat === cat ? '' : cat;
    updateUrl();
    render();
    return;
  }}
  const dayButton = event.target.closest('[data-calendar-day]');
  if (dayButton) {{
    const day = dayButton.dataset.calendarDay || '';
    state.params.day = state.params.day === day ? '' : day;
    updateUrl();
    render();
    const diaryList = document.querySelector('.diary-list');
    if (diaryList) diaryList.scrollIntoView({{behavior: 'smooth', block: 'start'}});
    return;
  }}
  const range = event.target.closest('[data-range]');
  if (range) {{
    state.params.range = range.dataset.range || 'all';
    updateUrl();
    render();
    return;
  }}
  const quick = event.target.closest('[data-quick-content]');
  if (quick) {{
    const params = currentParams();
    const url = new URL('/cats', window.location.origin);
    if (params.cat) url.searchParams.set('cat', params.cat);
    if (params.year) url.searchParams.set('year', params.year);
    if (params.month) url.searchParams.set('month', params.month);
    url.searchParams.set('ok', '1');
    url.searchParams.set('prefill_date', quick.dataset.quickDate || '');
    url.searchParams.set('prefill_content', quick.dataset.quickContent || '');
    url.searchParams.set('prefill_tag', quick.dataset.quickTag || '');
    window.location.href = url.pathname + '?' + url.searchParams.toString();
    return;
  }}
  if (event.target.closest('[data-filter-reset]')) {{
    state.params.cat = '';
    state.params.year = '';
    state.params.month = '';
    state.params.q = '';
    state.params.range = 'all';
    state.params.day = '';
    updateUrl();
    render();
  }}
}});

root.addEventListener('submit', (event) => {{
  const form = event.target.closest('#cats-filter-form');
  if (!form) return;
  event.preventDefault();
  const data = new FormData(form);
  state.params.cat = String(data.get('cat') || '');
  state.params.year = String(data.get('year') || '');
  state.params.month = String(data.get('month') || '');
  state.params.q = String(data.get('q') || '');
  state.params.day = '';
  updateUrl();
  render();
}});

root.addEventListener('change', (event) => {{
  const form = event.target.closest('#cats-filter-form');
  if (!form) return;
  const data = new FormData(form);
  state.params.cat = String(data.get('cat') || '');
  state.params.year = String(data.get('year') || '');
  state.params.month = String(data.get('month') || '');
  state.params.q = String(data.get('q') || '');
  state.params.day = '';
  updateUrl();
  render();
}});

render();
}})();
</script>'''
