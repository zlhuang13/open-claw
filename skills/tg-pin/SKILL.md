---
name: tg-pin
description: Send a Telegram message and pin it in a chat. Use when the user asks to pin a message on Telegram, send-and-pin a message, or pin an existing message by message_id. Also use for unpin requests. Works by calling the Telegram Bot API directly since OpenClaw's built-in `message pin` action does not support Telegram.
allowed-tools: Read, Bash
---

# tg-pin

Send a Telegram message and pin it (or just pin an existing message).

## Workflow

### Send + Pin (most common)
1. Send the message with `openclaw message send --channel telegram --account default --target <chat_id> --message '<text>'`
2. Extract `messageId` from the JSON output
3. Run the pin script (see below)

### Pin existing message
Skip step 1, go directly to the pin script with the known `message_id`.

### Unpin
Call the Bot API directly:
```bash
BOT_TOKEN=$(python3 -c "import json; d=open('/home/ubuntu/.openclaw/openclaw.json').read(); print(json.loads(d)['channels']['telegram']['botToken'])")
curl -s -X POST "https://api.telegram.org/bot${BOT_TOKEN}/unpinChatMessage" \
  -H "Content-Type: application/json" \
  -d "{\"chat_id\": \"<chat_id>\", \"message_id\": <message_id>}"
```

## Pin script

Located at `scripts/pin_message.sh` (relative to this skill directory).

Resolve absolute path: `/home/ubuntu/.openclaw/workspace/skills/tg-pin/scripts/pin_message.sh`

```bash
# Get bot token from config
BOT_TOKEN=$(python3 -c "import json; print(json.loads(open('/home/ubuntu/.openclaw/openclaw.json').read())['channels']['telegram']['botToken'])")

bash /home/ubuntu/.openclaw/workspace/skills/tg-pin/scripts/pin_message.sh \
  "$BOT_TOKEN" \
  "<chat_id>" \
  "<message_id>" \
  "true"   # true = silent pin (no notification), false = notify
```

## Known chat IDs
- Jerry: `8791954608`
- Hannah: `8028400239`

## Notes
- `disable_notification: true` means the pin won't trigger a push notification on the recipient's device
- Pinning replaces the current pinned message (last one wins per chat)
- Bot must be an admin in group chats to pin; in private DMs the bot can always pin
