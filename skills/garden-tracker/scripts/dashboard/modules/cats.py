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
COMMON_TAGS = ['呕吐', '吐毛球', '拉肚子', '软便', '食欲差', '没精神', '打喷嚏', '咳嗽', '吃药', '看医生']


def set_request_query(query):
    global REQUEST_QUERY
    REQUEST_QUERY = query or ''


def _params():
    parsed = parse_qs(REQUEST_QUERY, keep_blank_values=False)
    return {
        'cat': (parsed.get('cat') or [''])[0],
        'month': (parsed.get('month') or [''])[0],
        'q': (parsed.get('q') or [''])[0],
        'ok': (parsed.get('ok') or [''])[0],
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
                f'<div class="calendar-item">{" / ".join(html.escape(c) for c in e.get("cats", [])) or "记录"}: {html.escape((e.get("content") or "")[:16])}</div>'
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
    return '<a href="/">🖤 Kuro</a><span class="sep">›</span><span>Cat Diary</span>'


def render():
    if REQUEST_QUERY:
        _save_entry(REQUEST_QUERY)
    params = _params()
    cats_info = _profiles()
    entries = _load_entries(params['cat'], params['month'], params['q'])
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
        for tag in e.get('tags', []):
            symptom_counter[tag] += 1
        monthly_counter[(e.get('entry_date') or '')[:7]] += 1
        for cat in e.get('cats', []):
            cat_counter[cat] += 1

    non_weight_entries = [e for e in entries if '体重' not in (e.get('tags') or [])]
    weight_entries = [e for e in entries if '体重' in (e.get('tags') or []) and e.get('weight') not in (None, '')]
    stat_cards = [
        ('日常记录', str(len(non_weight_entries))),
        ('Moscar', str(sum(1 for e in non_weight_entries if 'Moscar' in e.get('cats', [])))),
        ('Nomi', str(sum(1 for e in non_weight_entries if 'Nomi（糯米）' in e.get('cats', [])))),
        ('常见标签', '、'.join(f'{k} {v}次' for k, v in symptom_counter.most_common(6) if k != '体重') or '暂无'),
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

    add_cat_checks = ''.join(
        f'<label class="check-pill"><input type="checkbox" name="cat" value="{html.escape(name)}"> <span>{html.escape(name)}</span></label>'
        for name in cat_names
    )
    tag_checks = ''.join(
        f'<label class="check-pill"><input type="checkbox" name="tag" value="{html.escape(tag)}"> <span>{html.escape(tag)}</span></label>'
        for tag in COMMON_TAGS
    )
    add_form_html = f'''<details class="entry-panel" {"open" if params['ok'] == '1' else ''}>
    <summary>➕ 添加记录 {"<span class='save-ok'>已保存 ✅</span>" if params['ok'] == '1' else ''}</summary>
    <form class="entry-form" method="get" action="/cats">
        <input type="hidden" name="action" value="add">
        <input type="hidden" name="ok" value="1">
        <div class="form-grid">
            <label><span>日期</span><input type="date" name="date" required></label>
            <label><span>心情</span><select name="mood"><option value="">-</option><option value="happy">开心</option><option value="sleepy">困</option><option value="sick">不舒服</option><option value="playful">活泼</option><option value="naughty">淘气</option></select></label>
            <label class="wide"><span>猫咪</span><div class="pill-group">{add_cat_checks}</div></label>
            <label class="wide"><span>记录内容</span><textarea name="content" rows="3" placeholder="比如：今天吐毛球，精神还可以" required></textarea></label>
            <label><span>饮食</span><input type="text" name="food" placeholder="吃了什么"></label>
            <label><span>便便</span><input type="text" name="stool" placeholder="正常/软便/拉肚子"></label>
            <label><span>体重 kg</span><input type="number" name="weight" step="0.01" placeholder="4.25"></label>
            <label><span>用药</span><input type="text" name="medication" placeholder="药名"></label>
            <label class="wide"><span>症状标签</span><div class="pill-group">{tag_checks}</div></label>
            <label class="wide"><span>补充标签</span><input type="text" name="extra_tags" placeholder="多个标签用逗号隔开"></label>
            <label class="wide"><span>备注</span><textarea name="notes" rows="2" placeholder="别的细节"></textarea></label>
        </div>
        <button class="submit-btn" type="submit">保存记录</button>
    </form>
</details>'''

    chart_html = ''
    if weight_entries:
        by_cat = defaultdict(list)
        for e in sorted(weight_entries, key=lambda x: x.get('entry_date') or ''):
            for cat in e.get('cats', []):
                by_cat[cat].append((e.get('entry_date'), float(e.get('weight'))))
        cards = []
        colors = {'Moscar': '#5b8def', 'Nomi（糯米）': '#e67aa4'}
        for cat, points in by_cat.items():
            if not points:
                continue
            weights = [p[1] for p in points]
            min_w, max_w = min(weights), max(weights)
            spread = max(max_w - min_w, 0.2)
            coords = []
            total = max(len(points) - 1, 1)
            for i, (dt, w) in enumerate(points):
                x = 40 + (320 * i / total)
                y = 180 - (130 * ((w - min_w) / spread))
                coords.append((x, y, dt, w))
            poly = ' '.join(f'{x:.1f},{y:.1f}' for x, y, _, _ in coords)
            dots = ''.join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.5" fill="{colors.get(cat, "#4a7")}"></circle><text x="{x:.1f}" y="{y+18:.1f}" font-size="10" text-anchor="middle" fill="#777">{html.escape(dt[5:])}</text><text x="{x:.1f}" y="{y-8:.1f}" font-size="10" text-anchor="middle" fill="#444">{w:.2f}</text>' for x, y, dt, w in coords)
            cards.append(f'<div class="weight-chart-card"><h3>{html.escape(cat)} 体重趋势</h3><svg viewBox="0 0 400 220" class="weight-chart"><line x1="40" y1="180" x2="370" y2="180" stroke="#ccc" /><line x1="40" y1="20" x2="40" y2="180" stroke="#ccc" /><polyline fill="none" stroke="{colors.get(cat, "#4a7")}" stroke-width="3" points="{poly}" />{dots}</svg><p class="chart-range">范围 {min_w:.2f} kg 到 {max_w:.2f} kg</p></div>')
        chart_html = '<h2>⚖️ 体重折线图</h2><div class="weight-chart-grid">' + ''.join(cards) + '</div>'

    entries_html = ''
    current_month = ''
    mood_map = {'happy': '😸', 'sleepy': '😴', 'sick': '🤒', 'playful': '😸', 'naughty': '😾'}
    for e in non_weight_entries:
        date = e.get('entry_date') or ''
        month = date[:7] if len(date) >= 7 else ''
        if month and month != current_month:
            current_month = month
            entries_html += f'<h3 class="month-header">{html.escape(month)}</h3>'
        cat_tags = ''.join(f'<span class="cat-tag-diary">{html.escape(t)}</span>' for t in e.get('cats', []))
        tag_html = ''.join(f'<span class="entry-tag">{html.escape(t)}</span>' for t in e.get('tags', []))
        mood = e.get('mood') or ''
        mood_icon = mood_map.get(mood, '')
        content = html.escape(e.get('content') or '')
        extras = []
        for label, key in [('饮食', 'food'), ('便便', 'stool'), ('用药', 'medication'), ('备注', 'notes')]:
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
            {f'<div class="entry-tag-row">{tag_html}</div>' if tag_html else ''}
            {extras_html}
        </div>'''

    calendar_html = _calendar_grid(entries, params['month'] or (months[0] if months else ''))

    return f'''<h1>🐱 Cat Diary</h1>
<p class="stats">共 {len(cats_info)} 只猫 · {len(entries)} 条匹配记录</p>
{"<h2>🐈 猫咪们</h2><div class='cat-grid'>" + profiles_html + "</div>" if profiles_html else ""}
<h2>📊 健康概览</h2><div class="stats-grid">{stats_html}</div>
{add_form_html}
{filters_html}
{chart_html}
{calendar_html}
<h2>📝 日记</h2>
<div class="diary-list">
    {entries_html if entries_html else '<p class="empty">当前筛选下还没有记录～</p>'}
</div>'''
