#!/usr/bin/env python3
"""Garden Tracker - SQLite database for plants, photos, care logs, and observations."""

import sqlite3
import os
import json
from datetime import datetime, timezone

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'garden.db')

SCHEMA = """
CREATE TABLE IF NOT EXISTS plants (
    id TEXT PRIMARY KEY,
    name_cn TEXT,
    name_en TEXT,
    species TEXT,
    variety TEXT,
    location TEXT,
    planted_date TEXT,
    source TEXT,
    price REAL,
    sun_exposure TEXT,
    watering_freq TEXT,
    soil_type TEXT,
    hardiness_zone TEXT,
    status TEXT DEFAULT 'healthy',
    notes TEXT,
    created_at TEXT,
    updated_at TEXT
);

CREATE TABLE IF NOT EXISTS photos (
    id TEXT PRIMARY KEY,
    plant_id TEXT REFERENCES plants(id),
    file_path TEXT,
    taken_date TEXT,
    season TEXT,
    description TEXT,
    created_at TEXT
);

CREATE TABLE IF NOT EXISTS care_log (
    id TEXT PRIMARY KEY,
    plant_id TEXT REFERENCES plants(id),
    date TEXT,
    action_type TEXT,
    notes TEXT,
    photo_id TEXT,
    created_at TEXT
);

CREATE TABLE IF NOT EXISTS observations (
    id TEXT PRIMARY KEY,
    plant_id TEXT REFERENCES plants(id),
    date TEXT,
    health_status TEXT,
    photo_id TEXT,
    notes TEXT,
    created_at TEXT
);
"""

def _connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = _connect()
    conn.executescript(SCHEMA)
    conn.commit()
    conn.close()

def _next_id(conn, table='plants'):
    prefix = 'P' if table == 'plants' else table[0].upper()
    row = conn.execute(f"SELECT id FROM {table} ORDER BY id DESC LIMIT 1").fetchone()
    if row:
        num = int(row['id'][1:]) + 1
    else:
        num = 1
    return f"{prefix}{num:03d}"

def _now():
    return datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')

# --- Plants ---

def add_plant(data: dict) -> dict:
    init_db()
    conn = _connect()
    plant_id = _next_id(conn)
    now = _now()
    conn.execute("""
        INSERT INTO plants (id, name_cn, name_en, species, variety, location,
            planted_date, source, price, sun_exposure, watering_freq,
            soil_type, hardiness_zone, status, notes, created_at, updated_at)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, (
        plant_id, data.get('name_cn'), data.get('name_en'), data.get('species'),
        data.get('variety'), data.get('location'), data.get('planted_date'),
        data.get('source'), data.get('price'), data.get('sun_exposure'),
        data.get('watering_freq'), data.get('soil_type'), data.get('hardiness_zone'),
        data.get('status', 'healthy'), data.get('notes'), now, now
    ))
    conn.commit()
    plant = get_plant(plant_id)
    conn.close()
    return plant

def get_plant(plant_id: str) -> dict | None:
    init_db()
    conn = _connect()
    row = conn.execute("SELECT * FROM plants WHERE id = ?", (plant_id,)).fetchone()
    conn.close()
    return dict(row) if row else None

def list_plants() -> list:
    init_db()
    conn = _connect()
    rows = conn.execute("SELECT * FROM plants ORDER BY id").fetchall()
    conn.close()
    return [dict(r) for r in rows]

def update_plant(plant_id: str, data: dict) -> bool:
    init_db()
    conn = _connect()
    fields = [k for k in data if k in ('name_cn','name_en','species','variety','location',
        'planted_date','source','price','sun_exposure','watering_freq',
        'soil_type','hardiness_zone','status','notes')]
    if not fields:
        conn.close()
        return False
    sets = ', '.join(f"{f}=?" for f in fields)
    vals = [data[f] for f in fields] + [_now(), plant_id]
    conn.execute(f"UPDATE plants SET {sets}, updated_at=? WHERE id=?", vals)
    conn.commit()
    conn.close()
    return True

def search_plants(keyword: str) -> list:
    init_db()
    conn = _connect()
    q = f"%{keyword}%"
    rows = conn.execute("""
        SELECT * FROM plants WHERE name_cn LIKE ? OR name_en LIKE ?
        OR species LIKE ? OR location LIKE ? OR variety LIKE ?
        ORDER BY id
    """, (q, q, q, q, q)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_plants_needing_care() -> list:
    init_db()
    conn = _connect()
    rows = conn.execute("""
        SELECT * FROM plants WHERE status IN ('healthy', 'sick')
        AND watering_freq IS NOT NULL AND watering_freq != ''
        ORDER BY location, id
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]

# --- Photos ---

def add_photo(plant_id: str, file_path: str, description: str = '', season: str = '') -> dict:
    init_db()
    conn = _connect()
    photo_id = _next_id(conn, 'photos')
    now = _now()
    conn.execute("""
        INSERT INTO photos (id, plant_id, file_path, taken_date, season, description, created_at)
        VALUES (?,?,?,?,?,?,?)
    """, (photo_id, plant_id, file_path, datetime.now(timezone.utc).strftime('%Y-%m-%d'), season, description, now))
    conn.commit()
    row = conn.execute("SELECT * FROM photos WHERE id = ?", (photo_id,)).fetchone()
    conn.close()
    return dict(row) if row else None

# --- Care Log ---

def add_care(plant_id: str, action_type: str, notes: str = '', photo_id: str = None) -> dict:
    init_db()
    conn = _connect()
    care_id = _next_id(conn, 'care_log')
    now = _now()
    conn.execute("""
        INSERT INTO care_log (id, plant_id, date, action_type, notes, photo_id, created_at)
        VALUES (?,?,?,?,?,?,?)
    """, (care_id, plant_id, datetime.now(timezone.utc).strftime('%Y-%m-%d'), action_type, notes, photo_id, now))
    conn.commit()
    row = conn.execute("SELECT * FROM care_log WHERE id = ?", (care_id,)).fetchone()
    conn.close()
    return dict(row) if row else None

def get_care_history(plant_id: str, days: int = 30) -> list:
    init_db()
    conn = _connect()
    rows = conn.execute("""
        SELECT * FROM care_log WHERE plant_id = ?
        AND date >= date('now', ?)
        ORDER BY date DESC, created_at DESC
    """, (plant_id, f"-{days} days")).fetchall()
    conn.close()
    return [dict(r) for r in rows]

# --- Observations ---

def add_observation(plant_id: str, health_status: str, notes: str = '', photo_id: str = None) -> dict:
    init_db()
    conn = _connect()
    obs_id = _next_id(conn, 'observations')
    now = _now()
    conn.execute("""
        INSERT INTO observations (id, plant_id, date, health_status, photo_id, notes, created_at)
        VALUES (?,?,?,?,?,?,?)
    """, (obs_id, plant_id, datetime.now(timezone.utc).strftime('%Y-%m-%d'), health_status, photo_id, notes, now))
    conn.commit()
    row = conn.execute("SELECT * FROM observations WHERE id = ?", (obs_id,)).fetchone()
    conn.close()
    return dict(row) if row else None

# --- CLI ---

if __name__ == '__main__':
    import sys
    init_db()
    action = sys.argv[1] if len(sys.argv) > 1 else 'test'

    if action == 'test':
        # Add test plant
        p = add_plant({
            'name_cn': '日本红枫',
            'name_en': 'Japanese Red Maple',
            'species': 'Acer palmatum',
            'variety': 'Atropurpureum',
            'location': '后院',
            'planted_date': '2026-04-15',
            'source': '购买',
            'price': 45.00,
            'sun_exposure': '半阴',
            'watering_freq': '每2-3天',
            'soil_type': '酸性腐殖土',
            'hardiness_zone': '6',
            'notes': '春天叶色鲜红，夏天转绿'
        })
        print(f"✅ Added plant: {json.dumps(p, ensure_ascii=False, default=str)}")

        # List
        plants = list_plants()
        print(f"📋 Total plants: {len(plants)}")
        for pl in plants:
            print(f"  {pl['id']} - {pl['name_cn']} ({pl['name_en']}) @ {pl['location']}")

        # Search
        results = search_plants('红枫')
        print(f"🔍 Search '红枫': {len(results)} results")

        # Care
        c = add_care(p['id'], 'water', '浇透了')
        print(f"💧 Care logged: {c['id']}")

        # Observation
        o = add_observation(p['id'], 'healthy', '新叶展开，颜色鲜艳')
        print(f"👁 Observation: {o['id']}")

        # Care history
        history = get_care_history(p['id'])
        print(f"📝 Care history: {len(history)} entries")

    elif action == 'add':
        data = json.loads(sys.argv[2])
        result = add_plant(data)
        print(json.dumps(result, ensure_ascii=False, default=str))
    elif action == 'list':
        plants = list_plants()
        print(json.dumps(plants, ensure_ascii=False, default=str))
    elif action == 'get':
        plant = get_plant(sys.argv[2])
        print(json.dumps(plant, ensure_ascii=False, default=str) if plant else 'null')
    elif action == 'search':
        results = search_plants(sys.argv[2])
        print(json.dumps(results, ensure_ascii=False, default=str))
    elif action == 'care':
        plant_id, action_type = sys.argv[2], sys.argv[3]
        notes = sys.argv[4] if len(sys.argv) > 4 else ''
        result = add_care(plant_id, action_type, notes)
        print(json.dumps(result, ensure_ascii=False, default=str))
    elif action == 'history':
        plant_id = sys.argv[2]
        days = int(sys.argv[3]) if len(sys.argv) > 3 else 30
        history = get_care_history(plant_id, days)
        print(json.dumps(history, ensure_ascii=False, default=str))
    elif action == 'observe':
        plant_id, status = sys.argv[2], sys.argv[3]
        notes = sys.argv[4] if len(sys.argv) > 4 else ''
        result = add_observation(plant_id, status, notes)
        print(json.dumps(result, ensure_ascii=False, default=str))
    elif action == 'update':
        plant_id = sys.argv[2]
        data = json.loads(sys.argv[3])
        ok = update_plant(plant_id, data)
        print('ok' if ok else 'failed')
    elif action == 'needs-care':
        results = get_plants_needing_care()
        print(json.dumps(results, ensure_ascii=False, default=str))
