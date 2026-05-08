"""Cats diary module - daily cat logs and memories."""
import calendar
import html
import os
import sqlite3
from collections import Counter, defaultdict
from urllib.parse import parse_qs

ROUTE = '/cats'
TITLE = '🐱 Cat Diary'
ICON = '🐱'
DESCRIPTION = '猫猫日记 · 日常记录'

DATA_DIR = '/home/ubuntu/.openclaw/workspace/skills/garden-tracker/data'
PROFILES_DB = os.path.join(DATA_DIR, 'cats_profiles.db')
DIARY_DB = os.path.join(DATA_DIR, 'cats_diary.db')
REQUEST_QUERY = ''


def set_request_query(query):
    global REQUEST_QUERY
    REQUEST_QUERY = query or ''


def _params():
    parsed = parse_qs(REQUEST_QUERY, keep_blank_values=False)
    return {
        'cat': (parsed.get('cat') or [''])[0],
        'month': (parsed.get('month') or [''])[0],
        'q': (parsed.get('q') or [''])[0],
    }


def _profiles():
    conn = sqlite3.connect(PROFILES_DB)
    conn.row_factory = sqlite3.Row
    rows = [dict(r) for r in conn.execute('SELECT * FROM cats ORDER BY birthday').fetchall()]
    conn.close()
    return rows


def _entries(cat_filter='', month_filter='', q=''):
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
        sql += ' AND (e.content LIKE ? OR ifnull(e.symptom,"") LIKE ? OR ifnull(e.notes,"") LIKE ? OR ifnull(e.food,"") LIKE ? OR ifnull(e.stool,"") LIKE ? OR ifnull(e.medication,"") LIKE ?)'
        like = f'%{q}%'
        args.extend([like] * 6)
    sql += ' ORDER BY e.entry_date DESC, e.id DESC'
    rows = [dict(r) for r in conn.execute(sql, args).fetchall()]
    filtered = []
    for row in rows:
        cats = [r[0] for r in conn.execute('SELECT cat_name FROM entry_cats WHERE entry_id = ? ORDER BY cat_name', (row['id'],)).fetchall()]
        row['cats'] = cats
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
            items = ''.join(
                f'<div class="calendar-item">{" / ".join(html.escape(c) for c in e.get("cats", [])) or "记录"}: {html.escape((e.get("content") or "")[:16])}</div>'
                for e in day_map.get(day, [])[:3]
            )
            more = ''
            if len(day_map.get(day, [])) > 3:
                more = f'<div class="calendar-more">+{len(day_map.get(day, [])) - 3} 条</div>'
            cells += f'<div class="calendar-cell"><div class="calendar-day">{day}</div>{items}{more}</div>'
    return f'<h2>🗓️ 月历视图</h2><div class="calendar-grid">{header}{cells}</div>'


def is_enabled():
    return os.path.exists(PROFILES_DB) and os.path.exists(DIARY_DB)


def nav():
    return '<a href="/">🖤 Kuro</a><span class="sep">›</span><span>Cat Diary</span>'


def render():
    params = _params()
    cats_info = _profiles()
    entries = _entries(params['cat'], params['month'], params['q'])
    months = _all_months()
    cat_names = [c.get('display_name') or c.get('name') for c in cats_info]

    profiles_html = ''
    for info in cats_info:
        name = html.escape(info.get('display_name') or info.get('name') or '')
        emoji = html.escape(info.get('emoji') or '🐱')
        breed = html.escape(info.get('breed') or '')
        birthday = html.escape(info.get('birthday') or '')
        photo = info.get('photo') or ''
        avatar_html = f'<img class="cat-photo" src="/cat-photos/{html.escape(photo)}" alt="{name}" loading="lazy">' if photo else f'<div class="cat-avatar">{emoji}</div>'
        profiles_html += f'''<div class="cat-profile">
            {avatar_html}
            <h3>{name}</h3>
            <p>{breed}</p>
            <p class="cat-detail">{birthday}</p>
        </div>'''

    symptom_counter = Counter()
    monthly_counter = Counter()
    cat_counter = Counter()
    for e in entries:
        if e.get('symptom'):
            symptom_counter[e['symptom']] += 1
        content = e.get('content') or ''
        if '吐' in content:
            symptom_counter['呕吐/吐毛球'] += 1
        if '拉肚子' in content or '腹泻' in content:
            symptom_counter['拉肚子'] += 1
        monthly_counter[(e.get('entry_date') or '')[:7]] += 1
        for cat in e.get('cats', []):
            cat_counter[cat] += 1

    stat_cards = [
        ('总记录', str(len(entries))),
        ('Moscar', str(cat_counter.get('Moscar', 0))),
        ('Nomi', str(cat_counter.get('Nomi（糯米）', 0))),
        ('常见症状', '、'.join(f'{k} {v}次' for k, v in symptom_counter.most_common(3)) or '暂无'),
    ]
    stats_html = ''.join(f'<div class="stat-card"><div class="stat-label">{html.escape(k)}</div><div class="stat-value">{html.escape(v)}</div></div>' for k, v in stat_cards)

    cat_options = '<option value="">全部猫咪</option>' + ''.join(
        f'<option value="{html.escape(name)}" {"selected" if params["cat"] == name else ""}>{html.escape(name)}</option>'
        for name in cat_names
    )
    month_options = '<option value="">全部月份</option>' + ''.join(
        f'<option value="{html.escape(m)}" {"selected" if params["month"] == m else ""}>{html.escape(m)}</option>'
        for m in months
    )
    filters_html = f'''<h2>🔎 快速筛选</h2>
<form class="filter-bar" method="get" action="/cats">
    <select name="cat">{cat_options}</select>
    <select name="month">{month_options}</select>
    <input type="text" name="q" placeholder="搜症状、饮食、备注" value="{html.escape(params['q'])}">
    <button type="submit">筛选</button>
    <a class="filter-reset" href="/cats">重置</a>
</form>'''

    trend_html = ''
    if monthly_counter:
        trend_html = '<h2>📈 月度记录</h2><div class="trend-list">' + ''.join(
            f'<div class="trend-item"><span>{html.escape(month)}</span><strong>{count} 条</strong></div>'
            for month, count in sorted(monthly_counter.items(), reverse=True)
        ) + '</div>'

    entries_html = ''
    current_month = ''
    mood_map = {'happy': '😸', 'sleepy': '😴', 'sick': '🤒', 'playful': '😸', 'naughty': '😾'}
    for e in entries:
        date = e.get('entry_date') or ''
        month = date[:7] if len(date) >= 7 else ''
        if month and month != current_month:
            current_month = month
            entries_html += f'<h3 class="month-header">{html.escape(month)}</h3>'
        cat_tags = ''.join(f'<span class="cat-tag-diary">{html.escape(t)}</span>' for t in e.get('cats', []))
        mood = e.get('mood') or ''
        mood_icon = mood_map.get(mood, '')
        content = html.escape(e.get('content') or '')
        extras = []
        for label, key in [('症状', 'symptom'), ('饮食', 'food'), ('便便', 'stool'), ('体重', 'weight'), ('用药', 'medication'), ('备注', 'notes')]:
            val = e.get(key)
            if val not in (None, ''):
                extras.append(f'<li><strong>{label}</strong> {html.escape(str(val))}</li>')
        extras_html = f'<ul>{"".join(extras)}</ul>' if extras else ''
        entries_html += f'''<div class="diary-entry">
            <div class="diary-header">
                <span class="diary-date">{html.escape(date)}</span>
                {cat_tags}
                {f'<span class="diary-mood">{mood_icon}</span>' if mood else ''}
            </div>
            <p class="diary-content">{content}</p>
            {extras_html}
        </div>'''

    calendar_html = _calendar_grid(entries, params['month'] or (months[0] if months else ''))

    return f'''<h1>🐱 Cat Diary</h1>
<p class="stats">共 {len(cats_info)} 只猫 · {len(entries)} 条匹配记录</p>
{"<h2>🐈 猫咪们</h2><div class='cat-grid'>" + profiles_html + "</div>" if profiles_html else ""}
<h2>📊 健康概览</h2><div class="stats-grid">{stats_html}</div>
{filters_html}
{calendar_html}
{trend_html}
<h2>📝 日记</h2>
<div class="diary-list">
    {entries_html if entries_html else '<p class="empty">当前筛选下还没有记录～</p>'}
</div>'''
