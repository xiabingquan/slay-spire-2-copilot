#!/usr/bin/env bash
# focus_game_window.sh — move the Slay the Spire 2 window onto the display
# where this session's terminal window lives.
#
# User preference 2026-09-18: the game must NOT pop up on the work screen;
# it belongs on the screen of the Claude Code session that launched it.
# Game runs windowed (settings.save fullscreen=false), so the window is
# movable via System Events. Cosmetic only — always exits 0; never blocks
# launch when the window is missing or Accessibility permission is absent.
set -u

GAME_PROCESS="Slay the Spire 2"
OFFSET_X=50
OFFSET_Y=80
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
STATE_DIR="$SCRIPT_DIR/.cache"
STATE_FILE="$STATE_DIR/game-window-pos"

# --record: capture the CURRENT game window position to the state file.
# Invoked before every graceful game stop (spirectl stop / sl) so relaunches
# can return the window to its previous screen+position. macOS window
# coordinates are global across displays — x,y implicitly encode which
# screen. Cosmetic only: any failure just skips the record.
if [ "${1:-}" = "--record" ]; then
  RPOS=$(osascript -e "tell application \"System Events\" to tell process \"$GAME_PROCESS\" to get position of window 1" 2>/dev/null || true)
  RX=$(echo "$RPOS" | awk -F', ' '{print $1}' | tr -d ' ')
  RY=$(echo "$RPOS" | awk -F', ' '{print $2}' | tr -d ' ')
  if [ -n "${RX:-}" ] && [ -n "${RY:-}" ] && [[ "$RX" =~ ^-?[0-9]+$ && "$RY" =~ ^-?[0-9]+$ ]]; then
    mkdir -p "$STATE_DIR" 2>/dev/null || true
    printf '%s,%s\n' "$RX" "$RY" > "$STATE_FILE" 2>/dev/null || true
    echo "focus_game_window: recorded game window position {$RX,$RY}"
  else
    echo "focus_game_window: could not read game window position; record skipped"
  fi
  exit 0
fi

# Restore-first (user directive 2026-09-19): when a last-position record
# exists, relaunches return the game window to that exact screen+position.
# No record / invalid record / window unmovable → fall through to the
# terminal-relative placement below (2026-09-18 preference).
if [ -f "$STATE_FILE" ]; then
  SX=$(head -1 "$STATE_FILE" 2>/dev/null | awk -F',' '{print $1}' | tr -d ' ')
  SY=$(head -1 "$STATE_FILE" 2>/dev/null | awk -F',' '{print $2}' | tr -d ' ')
  if [[ "${SX:-}" =~ ^-?[0-9]+$ && "${SY:-}" =~ ^-?[0-9]+$ ]]; then
    for _ in 1 2 3; do
      if osascript -e "tell application \"System Events\" to tell process \"$GAME_PROCESS\" to set position of window 1 to {$SX, $SY}" >/dev/null 2>&1; then
        echo "focus_game_window: restored $GAME_PROCESS to last position {$SX,$SY}"
        exit 0
      fi
      sleep 2
    done
    echo "focus_game_window: restore to {$SX,$SY} failed; falling back to terminal-relative placement"
  fi
fi

# System Events process names for known terminal apps.
normalize_app() {
  case "$1" in
    Terminal) echo "Terminal" ;;
    iTerm|iTerm2|iTerm.app) echo "iTerm2" ;;
    Code|code) echo "Code" ;;
    WezTerm) echo "WezTerm" ;;
    kitty) echo "kitty" ;;
    alacritty|Alacritty) echo "Alacritty" ;;
    Warp|WarpTerminal) echo "Warp" ;;
    Ghostty) echo "Ghostty" ;;
    Hyper) echo "Hyper" ;;
    Tabby) echo "Tabby" ;;
    *) return 1 ;;
  esac
}

# Walk the process tree upward looking for a real terminal app (skip
# shells/tmux/login so a tmux-pane session still finds Terminal.app).
terminal_app_from_tree() {
  local pid="${PPID:-}" comm base
  while [ -n "${pid:-}" ] && [ "$pid" != "1" ] && [ "$pid" != "0" ]; do
    comm=$(ps -o comm= -p "$pid" 2>/dev/null || true)
    base=$(basename "$comm" 2>/dev/null || echo "$comm")
    if normalize_app "$base" >/dev/null 2>&1; then
      normalize_app "$base"
      return 0
    fi
    pid=$(ps -o ppid= -p "$pid" 2>/dev/null | tr -d ' ')
  done
  return 1
}

terminal_app_from_env() {
  normalize_app "${TERM_PROGRAM:-}"
}

APP=$(terminal_app_from_tree || terminal_app_from_env || true)
if [ -z "${APP:-}" ]; then
  echo "focus_game_window: no terminal app detected; skipping"
  exit 0
fi

POS=$(osascript -e "tell application \"System Events\" to tell process \"$APP\" to get position of window 1" 2>/dev/null || true)
TX=$(echo "$POS" | awk -F', ' '{print $1}' | tr -d ' ')
TY=$(echo "$POS" | awk -F', ' '{print $2}' | tr -d ' ')
if [ -z "${TX:-}" ] || [ -z "${TY:-}" ] || ! [[ "$TX" =~ ^-?[0-9]+$ && "$TY" =~ ^-?[0-9]+$ ]]; then
  echo "focus_game_window: could not read $APP window position; skipping"
  exit 0
fi

GX=$((TX + OFFSET_X))
GY=$((TY + OFFSET_Y))

# The game window can appear a few seconds after the bridge handshake;
# retry briefly before giving up.
for _ in 1 2 3; do
  if osascript -e "tell application \"System Events\" to tell process \"$GAME_PROCESS\" to set position of window 1 to {$GX, $GY}" >/dev/null 2>&1; then
    echo "focus_game_window: moved $GAME_PROCESS to {$GX,$GY} (session terminal $APP at {$TX,$TY})"
    exit 0
  fi
  sleep 2
done

echo "focus_game_window: could not move $GAME_PROCESS window (missing window or Accessibility permission); skipped"
exit 0
