#!/usr/bin/env bash
# focus-game-window.sh — move the Slay the Spire 2 window onto the display
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
  echo "focus-game-window: no terminal app detected; skipping"
  exit 0
fi

POS=$(osascript -e "tell application \"System Events\" to tell process \"$APP\" to get position of window 1" 2>/dev/null || true)
TX=$(echo "$POS" | awk -F', ' '{print $1}' | tr -d ' ')
TY=$(echo "$POS" | awk -F', ' '{print $2}' | tr -d ' ')
if [ -z "${TX:-}" ] || [ -z "${TY:-}" ] || ! [[ "$TX" =~ ^-?[0-9]+$ && "$TY" =~ ^-?[0-9]+$ ]]; then
  echo "focus-game-window: could not read $APP window position; skipping"
  exit 0
fi

GX=$((TX + OFFSET_X))
GY=$((TY + OFFSET_Y))

# The game window can appear a few seconds after the bridge handshake;
# retry briefly before giving up.
for _ in 1 2 3; do
  if osascript -e "tell application \"System Events\" to tell process \"$GAME_PROCESS\" to set position of window 1 to {$GX, $GY}" >/dev/null 2>&1; then
    echo "focus-game-window: moved $GAME_PROCESS to {$GX,$GY} (session terminal $APP at {$TX,$TY})"
    exit 0
  fi
  sleep 2
done

echo "focus-game-window: could not move $GAME_PROCESS window (missing window or Accessibility permission); skipped"
exit 0
