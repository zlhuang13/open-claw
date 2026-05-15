"""Inventory module for household storage."""
import html
import os
import sqlite3
from collections import defaultdict
from datetime import datetime
from urllib.parse import parse_qs

ROUTE = '/inventory'
TITLE = '📦 Inventory'
ICON = '📦'
DESCRIPTION = '物品收纳 · 房间归档'

DB_PATH = '/home/ubuntu/.openclaw/workspace/skills/garden-tracker/data/inventory.db'
REQUEST_QUERY = ''
DEFAULT_ZONES = [
    ('room-001', '001 主卧', 1),
    ('room-002', '002 书房（次卧）', 2),
    ('room-003', '003 Hannah书房', 3),
    ('room-004', '004 客厅', 4),
    ('room-005', '005 餐厅', 5),
    ('room-006', '006 Ensuite', 6),
    ('room-007', '007 主卫', 7),
    ('room-008', '008 楼下厕所', 8),
]

LEGACY_ZONE_MAP = {
    'bedroom-master': 'room-001',
    'bedroom-2': 'room-002',
    'bedroom-3': 'room-003',
    'living-room': 'room-004',
    'dining-room': 'room-005',
    'bathroom-master': 'room-006',
    'bathroom-2': 'room-007',
    'toilet': 'room-008',
}


def set_request_query(query):
    global REQUEST_QUERY
    REQUEST_QUERY = query or ''


def _params():
    parsed = parse_qs(REQUEST_QUERY, keep_blank_values=False)
    return {key: (parsed.get(key) or [''])[0].strip() for key in (
        'name', 'category', 'zone_id', 'location_detail', 'quantity', 'notes', 'save_action'
    )}


def _connect():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def ensure_db():
    conn = _connect()
    conn.execute('CREATE TABLE IF NOT EXISTS zones(id TEXT PRIMARY KEY, name TEXT NOT NULL, sort_order INTEGER NOT NULL)')
    conn.execute(
        'CREATE TABLE IF NOT EXISTS items('
        'id INTEGER PRIMARY KEY AUTOINCREMENT, '
        'name TEXT NOT NULL, '
        'category TEXT, '
        'zone_id TEXT NOT NULL, '
        'location_detail TEXT, '
        'quantity TEXT, '
        'notes TEXT, '
        'created_at TEXT NOT NULL)'
    )

    for old_id, new_id in LEGACY_ZONE_MAP.items():
        conn.execute('UPDATE items SET zone_id = ? WHERE zone_id = ?', (new_id, old_id))

    for zone_id, name, sort_order in DEFAULT_ZONES:
        conn.execute('INSERT OR IGNORE INTO zones(id, name, sort_order) VALUES (?, ?, ?)', (zone_id, name, sort_order))
        conn.execute('UPDATE zones SET name = ?, sort_order = ? WHERE id = ?', (name, sort_order, zone_id))

    valid_ids = [zone_id for zone_id, _, _ in DEFAULT_ZONES]
    placeholders = ','.join('?' for _ in valid_ids)
    conn.execute(f'DELETE FROM zones WHERE id NOT IN ({placeholders})', valid_ids)

    conn.commit()
    conn.close()


def is_enabled():
    ensure_db()
    return True


def nav():
    return '<a href="/">🩵 UMI</a><span class="sep">›</span><span>Inventory</span>'


def _save_item(params):
    if params.get('save_action') != '1' or not params.get('name') or not params.get('zone_id'):
        return False, '名称和房间不能为空'
    conn = _connect()
    exists = conn.execute('SELECT 1 FROM zones WHERE id = ?', (params['zone_id'],)).fetchone()
    if not exists:
        conn.close()
        return False, '房间不存在，请重新选择'
    conn.execute(
        'INSERT INTO items(name, category, zone_id, location_detail, quantity, notes, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)',
        (params['name'], params.get('category') or None, params['zone_id'],
         params.get('location_detail') or None, params.get('quantity') or None,
         params.get('notes') or None, datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'))
    )
    conn.commit()
    conn.close()
    return True, '已保存'


def _load_state():
    conn = _connect()
    zones = [dict(r) for r in conn.execute('SELECT * FROM zones ORDER BY sort_order, name').fetchall()]
    items = [dict(r) for r in conn.execute('SELECT * FROM items ORDER BY id DESC').fetchall()]
    conn.close()
    by_zone = defaultdict(list)
    for item in items:
        by_zone[item['zone_id']].append(item)
    return zones, by_zone, items


def _esc(s):
    return html.escape(s or '')


def render():
    ensure_db()
    params = _params()
    saved = False
    message = ''
    if params.get('save_action') == '1':
        saved, message = _save_item(params)
        if saved:
            params = {k: '' for k in params}

    zones, by_zone, all_items = _load_state()

    # Zone dropdown options
    sel_zone = params.get('zone_id', '')
    zone_opts = ''
    for z in zones:
        sel = ' selected' if sel_zone == z['id'] else ''
        zone_opts += '<option value="' + _esc(z['id']) + '"' + sel + '>' + _esc(z['name']) + '</option>\n'

    # Zone cards with items
    zone_cards = ''
    for z in zones:
        zi = by_zone.get(z['id'], [])
        body = ''
        if zi:
            body = '<ul>'
            for item in zi:
                cat_html = '<span class="inventory-pill">' + _esc(item['category']) + '</span>' if item.get('category') else ''
                loc_html = '<div class="inventory-meta">📍 ' + _esc(item['location_detail']) + '</div>' if item.get('location_detail') else ''
                qty_html = '<div class="inventory-meta">🔢 ' + _esc(item['quantity']) + '</div>' if item.get('quantity') else ''
                notes_html = '<div class="inventory-notes">' + _esc(item['notes']) + '</div>' if item.get('notes') else ''
                body += ('<li class="inventory-item">'
                         '<div class="inventory-item-head"><strong>' + _esc(item['name']) + '</strong>' + cat_html + '</div>'
                         + loc_html + qty_html + notes_html + '</li>\n')
            body += '</ul>'
        else:
            body = '<p class="empty">这个房间还没有记录物品。</p>'

        zone_cards += ('<div class="inventory-zone-card">'
                       '<div class="inventory-zone-head"><h3>' + _esc(z['name']) + '</h3>'
                       '<span class="inventory-count">' + str(len(zi)) + ' 件</span></div>'
                       '<div class="inventory-zone-body">' + body + '</div></div>\n')

    status_html = ''
    if message:
        cls = 'ok' if saved else 'error'
        status_html = '<p class="inventory-status ' + cls + '">' + _esc(message) + '</p>'

    return ('<h1>📦 Inventory</h1>'
            '<p class="stats">按房间归档常用物品，方便收纳和查找</p>'
            '<div class="stats-grid inventory-summary-grid">'
            '<div class="stat-card"><div class="stat-label">房间数</div><div class="stat-value">' + str(len(zones)) + '</div></div>'
            '<div class="stat-card"><div class="stat-label">已录入物品</div><div class="stat-value">' + str(len(all_items)) + '</div></div>'
            '</div>'
            '<details class="entry-panel" open><summary>➕ 录入物品</summary>'
            '<form class="entry-form" method="get" action="/inventory">'
            '<input type="hidden" name="save_action" value="1">'
            '<div class="form-grid inventory-form-grid">'
            '<label>名称<input type="text" name="name" required value="' + _esc(params.get('name')) + '" placeholder="例如：备用毛巾"></label>'
            '<label>分类<input type="text" name="category" value="' + _esc(params.get('category')) + '" placeholder="例如：清洁 / 床品 / 工具"></label>'
            '<label>房间<select name="zone_id" required><option value="">请选择房间</option>' + zone_opts + '</select></label>'
            '<label>数量<input type="text" name="quantity" value="' + _esc(params.get('quantity')) + '" placeholder="例如：2 包 / 1 台"></label>'
            '<label class="wide">具体位置<input type="text" name="location_detail" value="' + _esc(params.get('location_detail')) + '" placeholder="例如：衣柜上层左侧收纳箱"></label>'
            '<label class="wide">备注<textarea name="notes" rows="3" placeholder="补充说明、购买时间等">' + _esc(params.get('notes')) + '</textarea></label>'
            '</div>'
            '<button class="submit-btn" type="submit">保存物品</button>'
            + status_html +
            '</form></details>'
            '<h2>🗂️ 房间浏览</h2>'
            '<div class="inventory-zone-grid">' + zone_cards + '</div>')
