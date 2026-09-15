#!/bin/bash
# External liveness watchdog for the play loop; installed in user crontab.
# Status-only: prints health lines to stdout; no notification side effects.
# Disarmed via `spirectl watchdog disable` (flag under STATE_DIR).
#
# Paths are resolved from this script's real location: the script lives inside
# the skill folder, which is reached through the Claude skill symlink
# (~/.claude/skills/slay-spire-2-copilot). realpath resolves that symlink to
# the true project path — nothing is hardcoded to a checkout location.

set -u
SCRIPT_PATH="$(python3 -c 'import os,sys; print(os.path.realpath(sys.argv[1]))' "$0")"
SKILL_DIR="$(dirname "$(dirname "$SCRIPT_PATH")")"   # <repo>/slay-spire-2-copilot
REPO="$(dirname "$SKILL_DIR")"                        # repo root
SPIRECTL="$SKILL_DIR/bridge/spirectl.py"
STATE_DIR="$HOME/.local/share/slay-spire-2-copilot"
DISARM_FLAG="$STATE_DIR/watchdog.disabled"
STALE_SEC=600
mkdir -p "$STATE_DIR" 2>/dev/null || true

if [[ ! -f "$SPIRECTL" ]]; then
  echo "[$(date '+%F %T')] bridge CLI not found: $SPIRECTL (script=$SCRIPT_PATH)"
  exit 1
fi

# Disarm flag present → exit immediately; the crontab entry stays installed.
if [[ -f "$DISARM_FLAG" ]]; then
  echo "[$(date '+%F %T')] watchdog DISARMED ($(cat "$DISARM_FLAG" 2>/dev/null)); skill=$SKILL_DIR"
  exit 0
fi

# Run-log dir comes ONLY from env SPIREBRIDGE_LOG_DIR; unset → log-age check skipped.
LOG_DIR="${SPIREBRIDGE_LOG_DIR:-}"

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
if [[ -z "$LOG_DIR" ]]; then
  :
elif newest=$(ls -t "$LOG_DIR"/run-*.log 2>/dev/null | head -1); then
  newest_log="$newest"
  newest_mtime=$(stat -f %m "$newest_log" 2>/dev/null || echo 0)
fi
now=$(date +%s)
if (( newest_mtime == 0 )); then
  log_age_note="n/a"
else
  log_age_note="$(( now - newest_mtime ))s"
fi
screen_line=$(echo "$bridge_msg" | head -1)
log_dir_note="${LOG_DIR:-unset (log-age check skipped)}"

if (( game_running == 0 )); then
  echo "[$(date '+%F %T')] status=game_down bridge_ok=$bridge_ok skill=$SKILL_DIR log_dir=$log_dir_note last_log=${newest_log:-none} age=${log_age_note}"
elif (( bridge_ok == 0 )); then
  echo "[$(date '+%F %T')] status=bridge_down skill=$SKILL_DIR log_dir=$log_dir_note last_log=${newest_log:-none} age=${log_age_note}"
elif [[ -n "$LOG_DIR" ]] && (( newest_mtime > 0 && now - newest_mtime > STALE_SEC )); then
  echo "[$(date '+%F %T')] status=loop_stale log_age=${log_age_note} screen=$screen_line skill=$SKILL_DIR log_dir=$LOG_DIR last_log=$newest_log"
else
  echo "[$(date '+%F %T')] status=healthy game=$game_running bridge=$bridge_ok log_age=${log_age_note} $screen_line skill=$SKILL_DIR log_dir=$log_dir_note"
fi
