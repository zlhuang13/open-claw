#!/usr/bin/env bash
# Pin a Telegram message via Bot API
# Usage: pin_message.sh <bot_token> <chat_id> <message_id> [disable_notification=true]
set -euo pipefail

BOT_TOKEN="${1:?Usage: pin_message.sh <bot_token> <chat_id> <message_id> [disable_notification]}"
CHAT_ID="${2:?chat_id required}"
MESSAGE_ID="${3:?message_id required}"
SILENT="${4:-true}"

RESPONSE=$(curl -s -X POST "https://api.telegram.org/bot${BOT_TOKEN}/pinChatMessage" \
  -H "Content-Type: application/json" \
  -d "{\"chat_id\": \"${CHAT_ID}\", \"message_id\": ${MESSAGE_ID}, \"disable_notification\": ${SILENT}}")

echo "$RESPONSE"

if echo "$RESPONSE" | grep -q '"ok":true'; then
  echo "✅ Message ${MESSAGE_ID} pinned in chat ${CHAT_ID}"
  exit 0
else
  echo "❌ Pin failed"
  exit 1
fi
