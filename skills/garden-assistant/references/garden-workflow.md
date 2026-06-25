# Garden workflow

## Typical requests this skill should handle

- “这是什么” with a plant image
- “加进 garden db”
- “改到 F区 / C区 / B区”
- “把照片换上”
- “这个对猫危险吗”
- “在 db 和 dashboard 上给我加上对猫风险等级”

## Household conventions

### Plant naming

Use practical Chinese display names in `name_cn`.
Use common English names in `name_en`.
Use botanical names in `species`.
Store cultivar in `variety` when known.

Examples:
- Patio Rose `Velvet Dream`
- Japanese Maple `Red Emperor`
- Japanese Maple `Katsura`

### Location style

Short zone labels are acceptable:
- `B区`
- `C区`
- `F区`

Longer notes can go in `notes`, for example:
- `花园右侧地栽，靠 fence，深红花`
- `地栽，靠 fence，深红叶`

### Cat risk interpretation

This garden uses a practical 3-level scale:
- `low`
- `medium`
- `high`

Prefer real-world cat safety judgment over overly theoretical toxicity alarm.

Examples already used in this household:
- acer palmatum: low
- camellia: low
- rose: low
- hydrangea: medium
- viburnum: medium
- tomato foliage: medium
- true lily / daylily: high if added later

### Change discipline

When the user asks for a garden DB update:
- make the DB change directly
- keep dashboard presentation simple unless asked for UI work
- confirm the changed row after write
- restart dashboard service if immediate UI reflection matters
