---
name: umi-dashboard
description: Standalone UMI dashboard app shell with modular pages for home, garden, cats, and inventory. Use when the user asks to open, launch, start, restart, or check the dashboard / 面板 / home app / UMI dashboard, view the garden/cats/inventory pages, or debug the dashboard server. 触发词如"打开面板"、"启动dashboard"、"看一下dashboard"、"重启面板"、"home app"。
---

# UMI Dashboard

This skill hosts the standalone UMI dashboard app.

- App entrypoint: `scripts/dashboard/server.py`
- Modules: `scripts/dashboard/modules/`
- Data remains in `skills/garden-tracker/data` and `skills/garden-tracker/photos`
