"""Garden DB module, plants, care logs, observations."""
import html
import json
import os
import sqlite3
import uuid
from collections import defaultdict
from datetime import datetime
from urllib.parse import parse_qs

ROUTE = '/garden'
TITLE = '🌱 Garden DB'
ICON = '🌱'
DESCRIPTION = '花园植物管理 · 养护记录 · 健康追踪'

DB_PATH = '/home/ubuntu/.openclaw/workspace/skills/garden-tracker/data/garden.db'
INFO_PATH = '/home/ubuntu/.openclaw/workspace/skills/garden-tracker/data/garden_info.json'
PHOTOS_DIR = '/home/ubuntu/.openclaw/workspace/skills/garden-tracker/photos'
REQUEST_QUERY = ''


def set_request_query(query):
    global REQUEST_QUERY
    REQUEST_QUERY = query or ''


def _params():
    parsed = parse_qs(REQUEST_QUERY, keep_blank_values=False)
    return {
        'zone': (parsed.get('zone') or [''])[0],
        'plant': (parsed.get('plant') or [''])[0],
        'quick_action': (parsed.get('quick_action') or [''])[0],
        'save_action': (parsed.get('save_action') or [''])[0],
    }


def is_enabled():
    return os.path.exists(DB_PATH)


def nav():
    return '<a href="/">🤍 UMI</a><span class="sep">›</span><span>Garden DB</span>'


def _build_todos(plants, care, obs):
    by_plant_care = defaultdict(list)
    by_plant_obs = defaultdict(list)
    for c in care:
        by_plant_care[c['plant_id']].append(c)
    for o in obs:
        by_plant_obs[o['plant_id']].append(o)

    today = datetime.utcnow().date()
    todos = []
    for p in plants:
        pid = p['id']
        name = p['name_cn']
        latest_care = by_plant_care.get(pid, [])
        latest_obs = by_plant_obs.get(pid, [])
        last_water = next((c for c in latest_care if c['action_type'] == 'water'), None)
        last_fertilize = next((c for c in latest_care if c['action_type'] == 'fertilize'), None)
        last_prune = next((c for c in latest_care if c['action_type'] == 'prune'), None)
        last_obs = latest_obs[0] if latest_obs else None

        if p.get('watering_freq') and last_water and last_water.get('date'):
            try:
                lw = datetime.strptime(last_water['date'], '%Y-%m-%d').date()
                if (today - lw).days >= 7:
                    todos.append((1, f'💧 {name} 距上次浇水已 {(today - lw).days} 天'))
            except Exception:
                pass
        if last_fertilize and last_fertilize.get('date'):
            try:
                lf = datetime.strptime(last_fertilize['date'], '%Y-%m-%d').date()
                if (today - lf).days >= 30:
                    todos.append((2, f'🧪 {name} 可考虑补肥（距上次 {(today - lf).days} 天）'))
            except Exception:
                pass
        if p.get('status') in ('stressed', 'sick'):
            todos.append((0, f'⚠️ {name} 当前状态 {p.get("status")}，建议尽快复查'))
        if last_obs and last_obs.get('date'):
            try:
                lo = datetime.strptime(last_obs['date'], '%Y-%m-%d').date()
                if (today - lo).days >= 21:
                    todos.append((3, f'👀 {name} 已 {(today - lo).days} 天没新观察记录'))
            except Exception:
                pass
        if pid in ('P003', 'P006') and today.month in (5, 6) and not last_prune:
            todos.append((1, f'✂️ {name} 花后修剪窗口到了'))
    return [t[1] for t in sorted(todos, key=lambda x: x[0])[:8]]


def _status_meta():
    return {
        'healthy': {'icon': '😄', 'css': 'status-healthy'},
        'stressed': {'icon': '😕', 'css': 'status-stressed'},
        'sick': {'icon': '🤒', 'css': 'status-sick'},
        'dormant': {'icon': '😴', 'css': ''},
    }


def _cat_risk_meta():
    return {
        'low': {'label': '🟢 低', 'text': '低风险'},
        'medium': {'label': '🟠 中', 'text': '中风险'},
        'high': {'label': '🔴 高', 'text': '高风险'},
    }


def _photo_path(pid):
    photo_dir = os.path.join(PHOTOS_DIR, pid)
    if not os.path.isdir(photo_dir):
        return ''
    imgs = sorted([f for f in os.listdir(photo_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))], reverse=True)
    if not imgs:
        return ''
    return f'/photos/{pid}/{imgs[0]}'


def _save_quick_action(params):
    plant_id = params.get('plant') or ''
    action = params.get('quick_action') or ''
    if not plant_id or not action or params.get('save_action') != '1':
        return None
    mapping = {
        '已浇水': 'water',
        '已施肥': 'fertilize',
        '已修剪': 'prune',
        '发现新芽': 'other',
        '病虫害': 'pest_control',
    }
    note_map = {
        '已浇水': '快速记录：已浇水',
        '已施肥': '快速记录：已施肥',
        '已修剪': '快速记录：已修剪',
        '发现新芽': '快速记录：发现新芽',
        '病虫害': '快速记录：发现病虫害',
    }
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        'INSERT INTO care_log (id, plant_id, date, action_type, notes, photo_id, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)',
        (str(uuid.uuid4()), plant_id, datetime.utcnow().strftime('%Y-%m-%d'), mapping.get(action, 'other'), note_map.get(action, action), None, datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'))
    )
    conn.commit()
    conn.close()
    return action


def _load_state():
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    plants = [dict(r) for r in db.execute('SELECT * FROM plants ORDER BY id').fetchall()]
    care = [dict(r) for r in db.execute('SELECT * FROM care_log ORDER BY date DESC').fetchall()]
    obs = [dict(r) for r in db.execute('SELECT * FROM observations ORDER BY date DESC').fetchall()]
    db.close()
    try:
        with open(INFO_PATH) as f:
            info = json.load(f)
    except Exception:
        info = {'zones': {}}

    care_by_plant = defaultdict(list)
    obs_by_plant = defaultdict(list)
    for c in care:
        care_by_plant[c['plant_id']].append(c)
    for o in obs:
        obs_by_plant[o['plant_id']].append(o)

    status_meta = _status_meta()
    happy_icons = ['😄', '😊', '🥰', '😸', '🤗']
    enriched_plants = []
    assigned_ids = set()
    known_zones = list(info.get('zones', {}).keys())
    for p in plants:
        plant = dict(p)
        plant['photo'] = _photo_path(plant['id'])
        plant['care'] = care_by_plant.get(plant['id'], [])[:5]
        plant['observations'] = obs_by_plant.get(plant['id'], [])[:3]
        meta = status_meta.get(plant.get('status'), {})
        if plant.get('status') == 'healthy':
            plant['status_icon'] = happy_icons[sum(ord(ch) for ch in plant['id']) % len(happy_icons)]
        else:
            plant['status_icon'] = meta.get('icon', '❓')
        plant['status_css'] = meta.get('css', '')
        for zid in known_zones:
            if zid in (plant.get('location') or ''):
                assigned_ids.add(plant['id'])
        enriched_plants.append(plant)

    zones = []
    for zid, z in sorted(info.get('zones', {}).items()):
        zone_plants = [p['id'] for p in enriched_plants if zid in (p.get('location') or '')]
        zones.append({
            'id': zid,
            'name': z.get('name', ''),
            'sun': z.get('sun', ''),
            'description': z.get('description', ''),
            'plant_ids': zone_plants,
        })
    unassigned = [p['id'] for p in enriched_plants if p['id'] not in assigned_ids]
    if unassigned:
        zones.append({
            'id': 'unassigned',
            'name': '未分区',
            'sun': '📦',
            'description': '暂未归类到具体花园区',
            'plant_ids': unassigned,
        })

    return {
        'summary': {
            'plant_count': len(enriched_plants),
            'care_count': len(care),
            'obs_count': len(obs),
        },
        'todos': _build_todos(enriched_plants, care, obs),
        'zones': zones,
        'plants': enriched_plants,
    }


def render_json():
    params = _params()
    saved = _save_quick_action(params)
    state = _load_state()
    state['params'] = params
    if saved:
        state['saved_notice'] = f'已记录: {saved}'
        state['params']['save_action'] = ''
    return json.dumps(state, ensure_ascii=False).encode('utf-8')


def render():
    state = _load_state()
    state['params'] = _params()
    risk_meta = _cat_risk_meta()
    for plant in state.get('plants', []):
        meta = risk_meta.get((plant.get('cat_risk') or '').lower(), {})
        plant['cat_risk_label'] = meta.get('label', '')
        plant['cat_risk_text'] = meta.get('text', '未标注')
    initial_state = html.escape(json.dumps(state, ensure_ascii=False))
    return f'''<div id="garden-app" data-initial-state="{initial_state}"></div>
<script>
(function() {{
const root = document.getElementById('garden-app');
if (!root) return;
const state = JSON.parse(root.dataset.initialState || '{{}}');
const quickActions = ['已浇水', '已施肥', '已修剪', '发现新芽', '病虫害'];

function esc(value) {{
  return String(value ?? '').replace(/[&<>"']/g, (ch) => ({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}}[ch]));
}}

function currentPlant() {{
  return (state.plants || []).find((p) => p.id === state.params.plant) || null;
}}

function visiblePlants() {{
  let plants = [...(state.plants || [])];
  if (state.params.zone === 'unassigned') {{
    const known = new Set((state.zones || []).filter((z) => z.id !== 'unassigned').map((z) => z.id));
    plants = plants.filter((p) => ![...known].some((zid) => (p.location || '').includes(zid)));
  }} else if (state.params.zone) {{
    plants = plants.filter((p) => (p.location || '').includes(state.params.zone));
  }}
  if (state.params.plant) {{
    plants = plants.filter((p) => p.id === state.params.plant);
  }}
  return plants;
}}

function updateUrl() {{
  const params = new URLSearchParams();
  if (state.params.zone) params.set('zone', state.params.zone);
  if (state.params.plant) params.set('plant', state.params.plant);
  if (state.params.quick_action) params.set('quick_action', state.params.quick_action);
  const qs = params.toString();
  history.replaceState(null, '', '/garden' + (qs ? '?' + qs : ''));
}}

function zoneHtml(zone) {{
  const tags = (zone.plant_ids || []).map((pid) => {{
    const p = state.plants.find((plant) => plant.id === pid);
    if (!p) return '';
    return `<button class="plant-tag" type="button" data-plant-tag="${{esc(pid)}}">${{esc(p.status_icon)}} ${{esc(p.name_cn)}} (${{esc(pid)}})</button>`;
  }}).join('') || '<span class="empty">暂无植物</span>';
  const active = state.params.zone === zone.id ? ' active' : '';
  const heading = zone.id === 'unassigned'
    ? '<h3>未分区</h3><p class="zone-info">📦 暂未归类到具体花园区</p>'
    : `<h3>${{esc(zone.id)}}区 — ${{esc(zone.name)}}</h3><p class="zone-info">☀️ ${{esc(zone.sun)}} · ${{esc(zone.description)}}</p>`;
  return `<button class="zone-card-link" type="button" data-zone="${{esc(zone.id)}}"><div class="zone-card${{active}}">${{heading}}<div class="plant-tags">${{tags}}</div></div></button>`;
}}

function plantHtml(p) {{
  const active = state.params.plant === p.id ? ' active' : '';
  const selected = state.params.plant === p.id ? '<span class="entry-tag">当前目标</span>' : '';
  const photo = p.photo ? `<img class="plant-photo" src="${{esc(p.photo)}}" alt="${{esc(p.name_cn)}}" loading="lazy">` : '';
  const catRisk = p.cat_risk_label ? `<span class="entry-tag cat-risk-tag">猫咪风险 ${{esc(p.cat_risk_label)}}</span>` : '<span class="entry-tag cat-risk-tag">猫咪风险 ⚪ 未标注</span>';
  const lifespan = p.lifespan ? `<span class="entry-tag lifespan-tag">${{esc(p.lifespan)}}</span>` : '';
  const care = (p.care || []).map((c) => `<li>${{esc(c.date)}} · ${{esc(c.action_type)}} · ${{esc(c.notes || '')}}</li>`).join('');
  const obs = (p.observations || []).map((o) => `<li>${{esc(o.date)}} · ${{esc(o.health_status)}} · ${{esc(o.notes || '')}}</li>`).join('');
  return `<button class="plant-card-link" type="button" data-plant="${{esc(p.id)}}"><div class="plant-card ${{esc(p.status_css || '')}}${{active}}">
    ${{photo}}
    <h3>${{esc(p.name_cn)}} <small>${{esc(p.name_en || '')}}</small> ${{selected}}</h3>
    <div class="entry-tag-row">${{lifespan}}${{catRisk}}</div>
    <table>
      <tr><td>ID</td><td>${{esc(p.id)}}</td></tr>
      <tr><td>学名</td><td><em>${{esc(p.species || '-')}}</em></td></tr>
      <tr><td>品种</td><td>${{esc(p.variety || '-')}}</td></tr>
      <tr><td>位置</td><td>${{esc(p.location || '-')}}</td></tr>
      <tr><td>种植日</td><td>${{esc(p.planted_date || '-')}}</td></tr>
      <tr><td>生命周期</td><td>${{esc(p.lifespan || '-')}}</td></tr>
      <tr><td>光照</td><td>${{esc(p.sun_exposure || '-')}}</td></tr>
      <tr><td>浇水</td><td>${{esc(p.watering_freq || '-')}}</td></tr>
      <tr><td>状态</td><td><strong>${{esc(p.status || '')}}</strong></td></tr>
      <tr><td>对猫风险</td><td>${{esc(p.cat_risk_text || '未标注')}}</td></tr>
      <tr><td>备注</td><td>${{esc(p.notes || '-')}}</td></tr>
    </table>
    ${{care ? '<h4>📋 养护记录</h4><ul>' + care + '</ul>' : ''}}
    ${{obs ? '<h4>👁 观察</h4><ul>' + obs + '</ul>' : ''}}
  </div></button>`;
}}

function renderQuickActions() {{
  const plant = currentPlant();
  if (!plant) {{
    return '<h2>⚡ 快速记录</h2><p class="cat-detail">先点一株植物，下面会出现快速记录按钮。</p>';
  }}
  const buttons = quickActions.map((action) => `<button class="quick-action-btn${{state.params.quick_action === action ? ' active' : ''}}" type="button" data-quick-action="${{esc(action)}}">${{esc(action)}}</button>`).join('');
  const notice = state.params.quick_action ? `<div class="stat-card"><div class="stat-label">待记录</div><div class="stat-value">${{esc(plant.name_cn)}} · ${{esc(state.params.quick_action)}}</div></div>` : '';
  const saveBtn = state.params.quick_action ? `<button class="submit-btn" type="button" id="garden-save-action">保存这条记录</button>` : '';
  const saved = state.saved_notice ? `<div class="stat-card"><div class="stat-label">已保存</div><div class="stat-value">${{esc(state.saved_notice)}}</div></div>` : '';
  return `<h2>⚡ 快速记录</h2><div class="pill-group quick-actions">${{buttons}}</div><p class="cat-detail">当前目标：${{esc(plant.name_cn)}}。再点一次植物卡可取消选择。</p>${{notice}}${{saveBtn}}${{saved}}<p class="cat-detail">选动作后点保存，会直接写入 Garden DB。</p>`;
}}

function render() {{
  const summary = state.summary || {{}};
  const todos = (state.todos || []).length
    ? '<h2>🪴 本周待办</h2><div class="stats-grid">' + state.todos.map((item) => `<div class="stat-card"><div class="stat-value">${{esc(item)}}</div></div>`).join('') + '</div>'
    : '<h2>🪴 本周待办</h2><p class="empty">目前没有明显待办 🎉</p>';
  const zoneText = state.params.zone ? `<p class="cat-detail">当前筛选：${{esc(state.params.zone)}}区</p>` : '';
  root.innerHTML = `<h1>🌱 Jerry's Garden</h1>
<p class="stats">共 ${{summary.plant_count || 0}} 棵植物 · ${{summary.care_count || 0}} 条养护记录 · ${{summary.obs_count || 0}} 条观察</p>
${{todos}}
<h2>🗺️ 花园区域</h2><div class="zone-grid">${{(state.zones || []).map(zoneHtml).join('')}}</div>
${{zoneText}}
${{renderQuickActions()}}
<h2>🌿 植物详情</h2><div class="plant-grid">${{visiblePlants().map(plantHtml).join('') || '<p class="empty">当前筛选下没有植物。</p>'}}</div>`;
}}

root.addEventListener('click', async (event) => {{
  const zoneButton = event.target.closest('[data-zone]');
  if (zoneButton) {{
    const nextZone = zoneButton.dataset.zone || '';
    state.params.zone = state.params.zone === nextZone ? '' : nextZone;
    state.params.plant = '';
    state.params.quick_action = '';
    updateUrl();
    render();
    return;
  }}
  const plantTag = event.target.closest('[data-plant-tag]');
  if (plantTag) {{
    state.params.plant = plantTag.dataset.plantTag || '';
    state.params.quick_action = '';
    updateUrl();
    render();
    return;
  }}
  const plantButton = event.target.closest('[data-plant]');
  if (plantButton) {{
    const nextPlant = plantButton.dataset.plant || '';
    state.params.plant = state.params.plant === nextPlant ? '' : nextPlant;
    state.params.quick_action = '';
    updateUrl();
    render();
    return;
  }}
  const actionButton = event.target.closest('[data-quick-action]');
  if (actionButton) {{
    state.params.quick_action = actionButton.dataset.quickAction || '';
    state.saved_notice = '';
    updateUrl();
    render();
    return;
  }}
  const saveButton = event.target.closest('#garden-save-action');
  if (saveButton && state.params.plant && state.params.quick_action) {{
    const p = new URLSearchParams({{ zone: state.params.zone || '', plant: state.params.plant || '', quick_action: state.params.quick_action || '', save_action: '1' }});
    const resp = await fetch('/api/garden?' + p.toString(), {{ cache: 'no-store' }});
    const next = await resp.json();
    Object.assign(state, next);
    state.params.quick_action = '';
    updateUrl();
    render();
  }}
}});

render();
}})();
</script>'''
