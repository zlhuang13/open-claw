# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

### Custom Skills

- `skills/bin-collection/` - 垃圾收集查询（Playwright）
- `skills/movie-finder/` - 电影片源搜索
- `skills/send-file/` - Telegram 发文件

### Key Paths

- Playwright: `./node_modules/playwright`
- Chromium: `~/.cache/ms-playwright/chromium_headless_shell-1217/`
- Node: `/home/ubuntu/.nvm/versions/node/v24.14.1/bin/node`
- OpenClaw config: `~/.openclaw/openclaw.json`

### Dashboard (Garden DB)

- Service: `kuro-dashboard.service` (systemd, enabled)
- Port: 80, bind: 100.86.143.43 (Tailscale only)
- URL: http://kuro-app.tail4dc7fc.ts.net/
- Path: /home/ubuntu/.openclaw/workspace/skills/garden-tracker/scripts/dashboard/

### OpenClaw Gateway

- Port: 18789, bind: loopback
- Tailscale serve: **未启用**（port 80 给 Garden DB 用）
- Default model: zai/glm-5.1 (fallback: claude-sonnet)

---

Add whatever helps you do your job. This is your cheat sheet.
