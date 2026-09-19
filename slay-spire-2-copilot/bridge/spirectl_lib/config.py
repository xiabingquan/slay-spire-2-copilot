"""Shared constants: paths, ports, env keys, watchdog and info-gate state files."""
import os
from pathlib import Path

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 17612
MOD_ID = "spire-copilot-bridge"
STEAM_APP_ID = "2868840"
GAME_MODS_DIR = Path(
    os.environ.get(
        "GAME_MODS_DIR",
        os.path.expanduser(
            "~/Library/Application Support/Steam/steamapps/common/"
            "Slay the Spire 2/SlayTheSpire2.app/Contents/MacOS/mods"
        ),
    )
)
GAME_LOG = Path(
    os.path.expanduser("~/Library/Application Support/SlayTheSpire2/logs/godot.log")
)
# REPO_ROOT is the skill folder (<repo>/slay-spire-2-copilot): config.py sits
# at bridge/spirectl/config.py, so three parents up.
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
REF_DIR = Path(__file__).resolve().parent / "data"
CODEX_BASE = "https://spire-codex.com"
CODEX_API = "https://spire-codex.com/api"

# Watchdog arm/notify state lives outside the repo (per-user runtime dir).
WATCHDOG_STATE_DIR = Path(os.path.expanduser("~/.local/share/slay-spire-2-copilot"))
WATCHDOG_DISARM = WATCHDOG_STATE_DIR / "watchdog.disabled"
WATCHDOG_LAST_NOTIFY = WATCHDOG_STATE_DIR / "watchdog-last-notify"

# Information-completeness contract: incomplete server payloads hard-stop the
# CLI (exit INFO_STOP_EXIT) with a Feishu notification until the flag is cleared.
INFO_STOP_FLAG = WATCHDOG_STATE_DIR / "info-incomplete-stop"
INFO_NOTIFY_SCRIPT = "/Users/xiabingquan/.claude/skills/notify/scripts/notify_feishu.py"
INFO_STOP_EXIT = 78
