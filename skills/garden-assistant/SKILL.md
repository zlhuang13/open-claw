---
name: garden-assistant
description: Garden plant intake, identification, dashboard updates, and cat-risk tracking for Hannah and Jerry's garden database. Use when adding a new plant to Garden DB, identifying a plant from chat/photo, assigning or correcting garden zones, updating plant photos/notes, recording plant metadata, or classifying cat toxicity risk (low/medium/high plus hidden detailed rationale) for dashboard-backed garden records.
---

# Garden Assistant

## Purpose

Use this skill to keep the household garden system consistent across chat, Garden DB, photos, and the dashboard.

## When to Use

- User wants to identify a plant from text or photo
- User wants to add or update a plant in Garden DB
- User wants to assign or correct a garden zone
- User wants to update dashboard-visible garden metadata or cat risk

## Workflow

1. Identify whether the user wants to:
   - identify a plant
   - add a plant to Garden DB
   - update an existing plant
   - assign/change a zone
   - add or replace a plant photo
   - classify cat risk
2. Read the current plant records from `../garden-tracker/data/garden.db` before making changes.
3. Treat the database as the source of truth for plant records.
4. If the user provides a photo for a new plant, store it under `../garden-tracker/photos/<PLANT_ID>/`.
5. Restart the dashboard service after DB or dashboard-visible photo changes.

## Plant Intake Rules

When adding a new plant:
- Create the next sequential plant ID in `P###` format.
- Record at minimum:
  - `id`
  - `name_cn`
  - `name_en`
  - `species`
  - `variety` if known
  - `location`
  - `planted_date` if known, otherwise use current date only when explicitly doing same-day intake
  - `sun_exposure` if inferable
  - `watering_freq` if inferable
  - `status` default `healthy` unless user says otherwise
  - `notes`
- Also proactively fill, without asking the user unless truly blocked:
  - cat risk level and hidden rationale fields
  - a short pruning suggestion in notes when the plant is identifiable enough
  - photo import if an inbound image was provided
  - best-effort location/zone from the message context
- Keep uncertain facts in notes instead of pretending certainty.
- If zone is described informally (for example “花园右侧”), map it to the closest known zone and say the assumption briefly.
- Default behavior for this household: when the user says “录入db” or equivalent, do the whole intake pass instead of asking follow-up questions one by one.

## Zone Handling

Known garden zones live in `../garden-tracker/data/garden_info.json` and existing DB records.

When the user asks to move a plant:
- Update `plants.location`
- Preserve other location detail if useful, for example `F区，前院`
- Prefer the household’s current zone labels like `A区`, `B区`, `C区`, `F区`, `G区`, `I区`

## Photo Handling

For plant photos:
- Save the inbound image into the plant’s photo folder.
- Use a simple date-based filename when possible, for example `2026-05-09.jpg`.
- Keep only safe filesystem names.
- If replacing the primary visible photo, adding a newer dated image is enough because the dashboard picks the latest file.

## Cat Risk Classification

Record the public dashboard field:
- `cat_risk`: `low`, `medium`, or `high`

Also record hidden DB detail fields:
- `cat_risk_reason`
- `cat_risk_parts`
- `cat_risk_symptoms`

Dashboard should stay simple and only show the risk level.

### Risk rubric

Use `high` for plants where small exposure can be severe or life-threatening for cats, especially kidney, cardiac, or major systemic toxicity.
Examples: true lilies, daylilies, oleander, sago palm, autumn crocus.

Use `medium` for plants that are toxic and can cause meaningful illness, but are usually more consistent with oral irritation, vomiting, diarrhea, lethargy, or moderate poisoning.
Examples: hydrangea, tomato foliage, prunus, gladiolus, ranunculus.

Use `low` for plants that are generally non-toxic or mainly cause mild GI upset / physical irritation.
Examples: camellia, acer palmatum, roses.

If uncertain:
- prefer conservative but not alarmist classification
- store uncertainty in `notes` or `cat_risk_reason`
- do not upgrade everything to `high`

## Dashboard Expectations

Garden dashboard currently surfaces plant records from `../garden-tracker/scripts/dashboard/modules/garden.py`.
When changing only DB fields already supported by the dashboard, do not edit UI unnecessarily.
When adding new garden metadata, prefer storing in DB first and keep dashboard minimal unless the user asked for visible UI changes.

## Verification

After changes:
1. Verify the DB row changed as intended.
2. Restart the dashboard if the UI should reflect the change.
3. Spot-check with `curl` or equivalent when needed.
4. Tell the user briefly what was updated.

## References

Read these as needed:
- `references/garden-schema.md` for DB and file layout
- `references/garden-workflow.md` for the household-specific workflow and conventions
