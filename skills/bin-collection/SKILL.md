---
name: bin-collection
description: Query South Oxfordshire bin/rubbish collection schedule for 26 Oak Hill Lane, Didcot OX11 6AP. Use when Jerry asks about bin collection, rubbish collection, recycling day, when to put bins out, what bins are collected this week or next week, or any question about waste collection dates or bin types.
---

# Bin Collection

## Purpose

Queries the South Oxfordshire Binzone website for bin collection schedule at Jerry's address.

## When to Use

- User asks when bins are collected
- User asks what bin goes out this week or next week
- User asks about rubbish, recycling, food waste, or holiday collection changes

## Default Address

- House: 26 Oak Hill Lane, Didcot
- Postcode: OX11 6AP

## Commands

Run the script and read the output:

```bash
node skills/bin-collection/scripts/query_bins.js "OX11 6AP" "26"
```

The script returns a formatted summary with:
- This week's collection date and bin types
- Next week's collection date and bin types
- ⚠️ Warning if collection day has been changed (e.g., due to bank holidays)

## Output Reference

| English | Chinese |
|---------|---------|
| Grey bin | 🩶 灰桶（一般垃圾） |
| Green bin | 💚 绿桶（回收物） |
| Food bin | 🍂 厨余桶 |
| Garden waste bin | 🌿 花园废物桶 |
| Textiles | 👕 纺织品 |
| Small electrical items | 🔌 小型电器 |

## Rules

- Script requires `playwright` npm package in `/home/ubuntu/.openclaw/workspace/node_modules`
- Playwright Chromium must be installed (`npx playwright install chromium`)
- The website blocks non-browser requests; the script uses headless Chromium to bypass this
- Always reply to Jerry in Chinese with the formatted result
