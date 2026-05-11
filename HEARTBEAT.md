# HEARTBEAT.md

# News digest is handled by cron job "daily-news-digest"

## 📝 Daily Memory Summary

At the **end of each day** (after 22:00 UTC), if there were conversations today:

1. Review today's conversation history
2. Check if `memory/YYYY-MM-DD.md` exists for today
3. If not, create it with a summary of key points
4. If it exists, update it with anything new from recent conversations

### Summary priorities:
- **Dev/technical work**: Record in detail — what was changed, file paths, config changes, commands used, decisions made, root causes
- **Other topics**: Keep brief — who said what, key decisions, action items
- Skip small talk and routine Q&A

### Tracking
- In `memory/heartbeat-state.json`, track: `"last_daily_summary": "YYYY-MM-DD"`
- Only run once per day (check the tracking field)

## 🔍 Daily Style & Persona Review

At the **end of each day** (after 22:00 UTC), after writing the daily memory summary:

1. 读当天的 `memory/YYYY-MM-DD.md`，找出所有来自 Jerry 的纠正、偏好反馈、风格意见
2. 对照 `STYLE.md`、`SOUL.md`、`AGENTS.md`、`USER.md` 四个文件，判断是否需要更新
3. 如有改动：
   - 直接修改对应文件
   - git commit，message 格式：`Daily review: update [文件名] based on conversation`
   - 通过 telegram:8791954608 发一条简短总结，说明改了什么、为什么改
4. 如无需改动：静默跳过，不发通知

### Tracking
- 在 `memory/heartbeat-state.json` 里记录：`"last_style_review": "YYYY-MM-DD"`
- 每天只跑一次

---

## Garden Care Reminders

When heartbeat fires, also check Garden DB seasonal care windows. If a reminder is due, send it to:
- Jerry: telegram:8791954608
- Hannah: telegram:8028400239

Keep reminders short and practical. Track sent flags in `memory/heartbeat-state.json` so each seasonal reminder is only sent once per window.

## Garden Pruning Reminders for Hannah

When heartbeat fires in the following months, check if Hannah's plants need pruning and send her a reminder via telegram:8028400239:

### 🌺红茶藨子 (P006) + 🌸雪球荚蒾 (P003) — 5-6月（花后）
- If month is May-June and not yet reminded: send reminder
- Track in memory/heartbeat-state.json: "pruning_reminder_2026_spring": true

### 💙绣球 Zorro (P004) + 💗绣球 You&Me (P005) — 7-8月（花后）
- If month is July-August and not yet reminded: send reminder
- Track: "pruning_reminder_2026_summer": true

### 🍁日本红枫 (P001) + 🌸樱花 Ruby (P007) — 7-8月（花后）
- Same timing as above hydrangea reminder, can combine

### 🌿日本冬青 (P002) — 5月或8月
- Light pruning reminder
