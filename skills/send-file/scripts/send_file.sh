#!/bin/bash
# send_file.sh - Send a file to a Telegram chat via Bot API
# Usage: bash send_file.sh <file_path> <chat_id>
#
# Bot token is read from ~/.openclaw/openclaw.json

set -e

FILE_PATH="$1"
CHAT_ID="$2"

if [[ -z "$FILE_PATH" || -z "$CHAT_ID" ]]; then
  echo "Usage: send_file.sh <file_path> <chat_id>"
  exit 1
fi

if [[ ! -f "$FILE_PATH" ]]; then
  echo "Error: file not found: $FILE_PATH"
  exit 1
fi

# Extract bot token from openclaw config
BOT_TOKEN=$(python3 -c "
import json
with open('$HOME/.openclaw/openclaw.json') as f:
    d = json.load(f)
# traverse nested dict for botToken
def find(d, key):
    if isinstance(d, dict):
        if key in d: return d[key]
        for v in d.values():
            r = find(v, key)
            if r: return r
    return None
print(find(d, 'botToken'))
")

if [[ -z "$BOT_TOKEN" || "$BOT_TOKEN" == "None" ]]; then
  echo "Error: could not find botToken in ~/.openclaw/openclaw.json"
  exit 1
fi

RESULT=$(curl -s \
  -F "document=@${FILE_PATH}" \
  "https://api.telegram.org/bot${BOT_TOKEN}/sendDocument?chat_id=${CHAT_ID}")

OK=$(echo "$RESULT" | python3 -c "import sys,json; r=json.load(sys.stdin); print(r.get('ok'))")

if [[ "$OK" == "True" ]]; then
  echo "OK: file sent successfully"
else
  echo "Error: $RESULT"
  exit 1
fi
