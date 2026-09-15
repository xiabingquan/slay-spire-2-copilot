#!/bin/bash
# slay-spire-2-copilot external liveness watchdog — runs independently of any Claude session.
# Installed in user crontab (5-min interval). Feishu-notifies ONLY while ARMED:
#   python3 bridge/spirectl.py watchdog enable    # arm (skill session start)
#   python3 bridge/spirectl.py watchdog disable   # disarm (user stopped play)
# Armed alerts: game down / bridge down / play-loop log stale >10min.
#
# Run-log dir comes ONLY from env SPIREBRIDGE_LOG_DIR (set it on the crontab
# line to track the active session dir); otherwise the per-user runtime
# fallback is used. No pointer files, no personal paths inside the repo.

set -u
REPO="$HOME/projects/slay-spire-2-copilot"
SPIRECTL="$REPO/bridge/spirectl.py"
NOTIFY="$HOME/.claude/skills/notify/scripts/notify_feishu.py"
STATE_DIR="$HOME/.local/share/slay-spire-2-copilot"
DISARM_FLAG="$STATE_DIR/watchdog.disabled"
STATE_FILE="$STATE_DIR/watchdog-last-notify"   # fixed path: rate-limit bookkeeping
STALE_SEC=600
MIN_NOTIFY_GAP=1800
mkdir -p "$STATE_DIR" 2>/dev/null || true

# Muted whenever play is intentionally stopped — cron keeps running silently.
if [[ -f "$DISARM_FLAG" ]]; then
  echo "[$(date '+%F %T')] watchdog DISARMED ($(cat "$DISARM_FLAG" 2>/dev/null)); exit"
  exit 0
fi

LOG_DIR="${SPIREBRIDGE_LOG_DIR:-$STATE_DIR/logs}"

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
  if [[ -f "$NOTIFY" ]]; then
    python3 "$NOTIFY" --title "$title" --content "$content" --color "$color" >/dev/null 2>&1 || true
  fi
  echo "$now" > "$STATE_FILE"
  echo "NOTIFIED: $title"
}

game_running=0
if pgrep -f "Slay the Spire 2" >/dev/null 2>&1; then
  game_running=1
fi

# Bridge probe must not append to run logs (keeps stale-loop detection honest).
bridge_ok=0
bridge_msg=""
if bridge_msg=$(SPIREBRIDGE_NO_RUNLOG=1 python3 "$SPIRECTL" state 2>&1 | head -3); then
  if echo "$bridge_msg" | grep -q "screen="; then
    bridge_ok=1
  fi
fi

newest_log=""
newest_mtime=0
if newest=$(ls -t "$LOG_DIR"/run-*.log 2>/dev/null | head -1); then
  newest_log="$newest"
  newest_mtime=$(stat -f %m "$newest_log" 2>/dev/null || echo 0)
fi
log_age=$(( now - newest_mtime ))
screen_line=$(echo "$bridge_msg" | head -1)

if (( game_running == 0 )); then
  echo "[$(date '+%F %T')] game DOWN; bridge_ok=$bridge_ok log_dir=$LOG_DIR"
  notify "slay-spire-2-copilot watchdog：游戏未运行" \
    "game process down while watchdog ARMED. If you stopped play on purpose, disarm:
python3 $SPIRECTL watchdog disable
To resume: invoke skill slay-spire-2-copilot with SPIREBRIDGE_LOG_DIR set.
log_dir: $LOG_DIR
last log: ${newest_log:-none} age=${log_age}s
$screen_line" \
    "red"
elif (( bridge_ok == 0 )); then
  echo "[$(date '+%F %T')] game UP but bridge DOWN; log_age=${log_age}s"
  notify "slay-spire-2-copilot watchdog：桥接断开" \
    "game running but bridge not answering (mod id spire-copilot-bridge).
doctor: python3 $SPIRECTL doctor
log_dir: $LOG_DIR
last log: ${newest_log:-none} age=${log_age}s" \
    "red"
elif (( newest_mtime > 0 && log_age > STALE_SEC )); then
  idle_min=$(( log_age / 60 ))
  echo "[$(date '+%F %T')] play loop STALE: log_age=${log_age}s screen=$screen_line"
  notify "slay-spire-2-copilot watchdog：循环停滞" \
    "bridge OK but no run-log activity for ${idle_min}min — play loop appears dead.
screen: $screen_line
log_dir: $LOG_DIR
last log: ${newest_log} age=${log_age}s
Resume: invoke skill slay-spire-2-copilot with SPIREBRIDGE_LOG_DIR set." \
    "orange"
else
  echo "[$(date '+%F %T')] healthy game=$game_running bridge=$bridge_ok log_age=${log_age}s $screen_line log_dir=$LOG_DIR"
fi
