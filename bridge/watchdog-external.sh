#!/bin/bash
# mimo-spire external liveness watchdog — runs independently of any Claude session.
# Checks game/bridge/log freshness every invocation; Feishu-notifies when the
# autonomous play loop appears dead. Installed in user crontab (5-min interval).

set -u
REPO="$HOME/projects/mimo-spire"
SPIRECTL="$REPO/bridge/spirectl.py"
NOTIFY="$HOME/.claude/skills/notify/scripts/notify_feishu.py"
STALE_SEC=600          # no run-log activity for 10 min while game up => stalled
STATE_FILE="$REPO/logs/.watchdog-last-notify"
MIN_NOTIFY_GAP=1800    # don't spam Feishu more than once per 30 min

now=$(date +%s)
last_notify=0
if [[ -f "$STATE_FILE" ]]; then
  last_notify=$(cat "$STATE_FILE" 2>/dev/null || echo 0)
fi

notify() {
  local title="$1" content="$2" color="$3"
  if (( now - last_notify < MIN_NOTIFY_GAP )); then
    echo "skip notify (gap $((now - last_notify))s): $title"
    return
  fi
  if [[ -x "$NOTIFY" || -f "$NOTIFY" ]]; then
    python3 "$NOTIFY" --title "$title" --content "$content" --color "$color" >/dev/null 2>&1 || true
  fi
  echo "$now" > "$STATE_FILE"
  echo "NOTIFIED: $title"
}

game_running=0
if pgrep -f "Slay the Spire 2" >/dev/null 2>&1; then
  game_running=1
fi

bridge_ok=0
bridge_msg=""
if bridge_msg=$(python3 "$SPIRECTL" state 2>&1 | head -3); then
  if echo "$bridge_msg" | grep -q "screen="; then
    bridge_ok=1
  fi
fi

# Newest run-log mtime
newest_log=""
newest_mtime=0
if newest=$(ls -t "$REPO"/logs/run-*.log 2>/dev/null | head -1); then
  newest_log="$newest"
  newest_mtime=$(stat -f %m "$newest_log" 2>/dev/null || echo 0)
fi
log_age=$(( now - newest_mtime ))

screen_line=$(echo "$bridge_msg" | head -1)

if (( game_running == 0 )); then
  echo "[$(date '+%F %T')] game DOWN; bridge_ok=$bridge_ok"
  notify "mimo-spire watchdog：游戏未运行" \
    "game process down. bridge_ok=$bridge_ok. Claude session may have died — restart with: python3 $SPIRECTL launch
last log: ${newest_log:-none} age=${log_age}s
$screen_line" \
    "red"
elif (( bridge_ok == 0 )); then
  echo "[$(date '+%F %T')] game UP but bridge DOWN; log_age=${log_age}s"
  notify "mimo-spire watchdog：桥接断开" \
    "game running but bridge not answering. Mod may need re-accept or relaunch.
doctor: python3 $SPIRECTL doctor
last log: ${newest_log:-none} age=${log_age}s" \
    "red"
elif (( newest_mtime > 0 && log_age > STALE_SEC )); then
  idle_min=$(( log_age / 60 ))
  echo "[$(date '+%F %T')] play loop STALE: log_age=${log_age}s screen=$screen_line"
  notify "mimo-spire watchdog：循环停滞" \
    "bridge OK but no run-log activity for ${idle_min}min — Claude play loop appears dead.
screen: $screen_line
last log: ${newest_log} age=${log_age}s
Resume: open Claude session and run the mimo-spire watchdog takeover." \
    "orange"
else
  echo "[$(date '+%F %T')] healthy game=$game_running bridge=$bridge_ok log_age=${log_age}s $screen_line"
fi
