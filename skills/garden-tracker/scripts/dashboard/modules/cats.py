"""Cats diary module - daily cat logs and memories."""
import html
import os
import sqlite3

ROUTE = '/cats'
TITLE = '🐱 Cat Diary'
ICON = '🐱'
DESCRIPTION = '猫猫日记 · 日常记录'

DATA_DIR = '/home/ubuntu/.openclaw/workspace/skills/garden-tracker/data'
PROFILES_DB = os.path.join(DATA_DIR, 'cats_profiles.db')
DIARY_DB = os.path.join(DATA_DIR, 'cats_diary.db')


def _profiles():
    conn = sqlite3.connect(PROFILES_DB)
    conn.row_factory = sqlite3.Row
    rows = [dict(r) for r in conn.execute('SELECT * FROM cats ORDER BY birthday').fetchall()]
    conn.close()
    return rows


def _entries():
    conn = sqlite3.connect(DIARY_DB)
    conn.row_factory = sqlite3.Row
    rows = [dict(r) for r in conn.execute('SELECT * FROM diary_entries ORDER BY entry_date DESC, id DESC').fetchall()]
    for row in rows:
        cats = [r[0] for r in conn.execute('SELECT cat_name FROM entry_cats WHERE entry_id = ? ORDER BY cat_name', (row['id'],)).fetchall()]
        row['cats'] = cats
    conn.close()
    return rows


def is_enabled():
    return os.path.exists(PROFILES_DB) and os.path.exists(DIARY_DB)


def nav():
    return '<a href="/">🖤 Kuro</a><span class="sep">›</span><span>Cat Diary</span>'


def render():
    cats_info = _profiles()
    entries = _entries()

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

    total = len(entries)
    return f'''<h1>🐱 Cat Diary</h1>
<p class="stats">共 {len(cats_info)} 只猫 · {total} 条记录</p>
{"<h2>🐈 猫咪们</h2><div class='cat-grid'>" + profiles_html + "</div>" if profiles_html else ""}
<h2>📝 日记</h2>
<div class="diary-list">
    {entries_html if entries_html else '<p class="empty">还没有记录，告诉 Kuro 开始记录吧～</p>'}
</div>'''
