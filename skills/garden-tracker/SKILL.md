---
name: garden-tracker
description: Track garden plants with SQLite. Record plants, photos, care logs, observations, and garden zone metadata. Use when users ask to identify a plant, add or update a garden record, log care, search plants, inspect garden zones, or query plant history/status.
---

# Garden Tracker Skill

## Purpose

Track garden plants with SQLite. Record plants, photos, care logs, and observations.

## When to Use

- User sends a plant photo asking for identification
- User mentions garden, planting, watering, fertilizing
- User explicitly asks to record/query garden plants

## Commands

`scripts/garden_db.py` — Python 3, no external dependencies.

### CLI Usage

```bash
# Add plant
python3 scripts/garden_db.py add '{"name_cn":"日本红枫","name_en":"Japanese Red Maple","species":"Acer palmatum","location":"后院","planted_date":"2026-04-15","source":"购买","watering_freq":"每2-3天"}'

# List all
python3 scripts/garden_db.py list

# Get single
python3 scripts/garden_db.py get P001

# Search
python3 scripts/garden_db.py search 红枫

# Log care
python3 scripts/garden_db.py care P001 water "浇透了"
python3 scripts/garden_db.py care P001 fertilize "用了缓释肥"

# Observation
python3 scripts/garden_db.py observe P001 healthy "新叶展开"

# Care history
python3 scripts/garden_db.py history P001 30

# Update
python3 scripts/garden_db.py update P001 '{"status":"sick","notes":"叶尖发黄"}'

# Plants needing care
python3 scripts/garden_db.py needs-care
```

## Workflow

### A. Identify & Record New Plant (Most Important)

When user sends a photo or mentions a new plant:
1. Use image tool to identify the plant
2. Collect info: names, species, location, planted date, etc.
3. **Location matching (MANDATORY):**
   - Read `data/garden_info.json` zones and their `keywords`
   - If user mentions a specific zone (e.g. "A区", "G区") → match directly, no confirmation needed
   - If user describes location (e.g. "温室", "前院", "后院围栏") → match by keywords
   - **Exactly one match → use directly, don't ask** (e.g. "前院" → F区, "温室" → G区)
   - Multiple zones match → list them and ask user to choose
   - No match → list all zones with descriptions and ask user to pick
   - Format location as: "{zone_id}区-{zone_name}" (e.g. "C区-右侧阳光区")
4. **MUST confirm ALL data with user before saving** — list name, species, location, date, etc.
5. After confirmation: `python3 scripts/garden_db.py add '{...}'`
6. If there's a photo, save to `photos/{plant_id}/` and add_photo

### Zone Reference (read from garden_info.json)

| Zone | Name | Sun | Keywords |
|------|------|-----|----------|
| A | 西南阳光区 | 全日照 | 中心、交汇、西南 |
| B | 左侧偏阴区 | 半阴 | 左侧、偏阴 |
| C | 右侧阳光区 | 全日照 | 右侧、后方围栏 |
| D | L形下段 | 半阴 | 下段 |
| F | 前院偏阴区 | 偏阴 | 前院、门口 |
| G | 温室 | 可控 | 温室、greenhouse |
| I | 室内育苗区 | 室内 | 室内、培育盒 |

### B. Query Garden Status

- "花园里有什么" → `list`
- "P001 怎么样了" → `get` + `history`
- "哪些植物该浇水了" → `needs-care`

### C. Record Care

- "今天给红枫浇水了" → identify plant → `care P001 water "..."` 
- Supported: water / fertilize / prune / pest_control / repot / other

### D. Observations

- User sends photo of plant status → `observe` + `care` (add_photo if applicable)

## Output Format

- Lists: concise, one line per plant with emoji indicators
- Single plant: full info card
- Care reminders: emoji markers (💧 fertilize, ✂️ prune, 🐛 pest_control)

## Rules

- **Always confirm before adding a new plant** — never auto-add
- Photos saved to `photos/{plant_id}/`
- All dates in YYYY-MM-DD format
- Jerry's times default to UK time (BST/GMT)
