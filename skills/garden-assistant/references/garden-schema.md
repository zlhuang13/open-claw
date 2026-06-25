# Garden schema

## Main database

Path: `/home/ubuntu/.openclaw/workspace/skills/garden-tracker/data/garden.db`

Primary table used in chat-driven plant management:
- `plants`

Important plant fields currently in use:
- `id`
- `name_cn`
- `name_en`
- `species`
- `variety`
- `location`
- `planted_date`
- `sun_exposure`
- `watering_freq`
- `status`
- `notes`
- `cat_risk`
- `cat_risk_reason`
- `cat_risk_parts`
- `cat_risk_symptoms`

Related tables used by dashboard:
- `care_log`
- `observations`

## Plant photos

Path: `/home/ubuntu/.openclaw/workspace/skills/garden-tracker/photos/<PLANT_ID>/`

The dashboard shows the latest filename in the folder, sorted descending.
Using date-based filenames is recommended.

## Dashboard

Module path:
`/home/ubuntu/.openclaw/workspace/skills/garden-tracker/scripts/dashboard/modules/garden.py`

Service:
- `kuro-dashboard.service`

After DB or photo updates that should show immediately, restart the service.

## Cat risk fields

Visible in dashboard:
- `cat_risk`

Stored for detailed lookup only:
- `cat_risk_reason`
- `cat_risk_parts`
- `cat_risk_symptoms`
