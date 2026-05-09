---
name: send-file
description: Send a file from the server to a Telegram user. Use when Jerry or any user asks to send, share, or deliver a file via Telegram. Triggers on phrases like "send me the file", "发文件给我", "把这个文件发过来", "share this file", or any request to deliver a workspace file to a chat.
---

# Send File

## Purpose

Sends a file from the server to a Telegram chat using the Bot API.

## When to Use

- User asks to send or share a file in Telegram
- User wants a workspace file delivered to a chat
- A workflow needs to hand off a generated file to Jerry or Hannah

## Commands

```bash
bash skills/send-file/scripts/send_file.sh <file_path> <chat_id>
```

**Examples:**
```bash
bash skills/send-file/scripts/send_file.sh /home/ubuntu/.openclaw/workspace/USER.md 8791954608
bash skills/send-file/scripts/send_file.sh /home/ubuntu/.openclaw/workspace/SOUL.md 8791954608
```

## Rules

- Bot token is auto-read from `~/.openclaw/openclaw.json` (key: `botToken`)
- `chat_id` is the Telegram user ID (Jerry: `8791954608`, Hannah: `8028400239`)
- Works with any file type: `.md`, `.json`, `.py`, `.log`, `.png`, etc.
- Always confirm to the user after sending
