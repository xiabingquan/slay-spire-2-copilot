#!/usr/bin/env python3
# spirectl: CLI bridging a Claude Code session to the SpireBridge STS2 mod.
"""spirectl — talk to the spire-copilot-bridge mod inside Slay the Spire 2."""

import argparse
import hashlib
import json
import os
import re
import secrets
import socket
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 17612
MOD_ID = "spire-copilot-bridge"
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
REPO_ROOT = Path(__file__).resolve().parent.parent
SKILL_ROOT = REPO_ROOT  # skill folder: <repo>/slay-spire-2-copilot (bridge lives here)
# Run-log directory: SPIREBRIDGE_LOG_DIR only — no pointer files, no CLI flags,
# no fallback directory. Unset → commands that write run logs fail fast.
#   export SPIREBRIDGE_LOG_DIR=/abs/dir
STEAM_APP_ID = "2868840"
BBCODE_RE = re.compile(r"\[/?[^\]]+\]")


def strip_bbcode(text):
    """Remove BBCode-style markup tags from a string.

    Args:
        text: Raw label text that may contain [tag] markup.

    Returns:
        The text with markup tags removed; non-strings pass through unchanged.
    """
    return BBCODE_RE.sub("", text) if isinstance(text, str) else text


LOG_DIR_UNSET_ERROR = (
    "SPIREBRIDGE_LOG_DIR is not set. The skill invocation must supply an "
    "absolute log folder path; set SPIREBRIDGE_LOG_DIR for the whole session. "
    "There is no fallback log directory."
)


def resolve_log_dir():
    """Resolve the run-log directory from SPIREBRIDGE_LOG_DIR.

    Returns:
        Absolute path of the log folder, created if missing.

    Raises:
        RuntimeError: If SPIREBRIDGE_LOG_DIR is unset; there is no fallback.
    """
    env = os.environ.get("SPIREBRIDGE_LOG_DIR")
    if not env:
        raise RuntimeError(LOG_DIR_UNSET_ERROR)
    path = Path(env).expanduser()
    path.mkdir(parents=True, exist_ok=True)
    return path.resolve()


def _apply_log_dir():
    """Bind RUNLOG_DIR/RUNLOG_POINTER to the env-resolved log folder.

    Returns:
        The resolved log directory, or None if the env var is unset.
    """
    global RUNLOG_DIR, RUNLOG_POINTER
    try:
        RUNLOG_DIR = resolve_log_dir()
    except RuntimeError:
        RUNLOG_DIR = None
        RUNLOG_POINTER = None
        return None
    RUNLOG_POINTER = RUNLOG_DIR / ".current_run"
    return RUNLOG_DIR


RUNLOG_DIR = None
RUNLOG_POINTER = None
_apply_log_dir()


def _require_log_dir():
    """Return the active log directory and its current-run pointer file.

    Returns:
        Tuple (log_dir, pointer_path).

    Raises:
        SystemExit: If SPIREBRIDGE_LOG_DIR was never set for this process.
    """
    if RUNLOG_DIR is None or RUNLOG_POINTER is None:
        raise SystemExit(f"error: {LOG_DIR_UNSET_ERROR}")
    return RUNLOG_DIR, RUNLOG_POINTER


def _runlog_file():
    """Return the active run-log file path, deriving one if needed.

    File names are run-<timestamp>-<hash8>.log inside SPIREBRIDGE_LOG_DIR;
    rotation is driven by the .current_run pointer in that same folder.

    Returns:
        Path of the current run log file.

    Raises:
        SystemExit: If SPIREBRIDGE_LOG_DIR is unset.
    """
    log_dir, pointer = _require_log_dir()
    log_dir.mkdir(parents=True, exist_ok=True)
    current = None
    if pointer.exists():
        current = pointer.read_text(encoding="utf-8").strip() or None
        if current:
            return log_dir / current
    stamp = time.strftime("%Y%m%d-%H%M%S")
    digest = hashlib.sha256(
        f"{stamp}|{os.getpid()}|{secrets.token_hex(8)}".encode("utf-8")
    ).hexdigest()[:8]
    current = f"run-{stamp}-{digest}.log"
    pointer.write_text(current + "\n", encoding="utf-8")
    return log_dir / current


def log_run_event(kind, data, rotate=False, finalize=False):
    """Append a timestamped JSON record to the current run log.

    Args:
        kind: Record kind (state, act, wait_change, run_end, ...).
        data: Payload merged into the JSON line.
        rotate: Drop the current-run pointer so the next write starts a new file.
        finalize: Mark the record as a run end (adds outcome).

    Returns:
        Path of the written log file, or None when logging is skipped
        (SPIREBRIDGE_NO_RUNLOG set) or the log dir is unset.

    Raises:
        SystemExit: If a write is required but SPIREBRIDGE_LOG_DIR is unset.
    """
    if os.environ.get("SPIREBRIDGE_NO_RUNLOG"):
        return None
    _, pointer = _require_log_dir()
    if rotate and pointer.exists():
        pointer.unlink(missing_ok=True)
    path = _runlog_file()
    record = {"ts": time.strftime("%Y-%m-%d %H:%M:%S"), "kind": kind, **data}
    if finalize:
        record["outcome"] = data.get("outcome") or "game_over"
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")
    return path


# Watchdog arm/notify state lives outside the repo (per-user runtime dir).
WATCHDOG_STATE_DIR = Path(os.path.expanduser("~/.local/share/slay-spire-2-copilot"))
WATCHDOG_DISARM = WATCHDOG_STATE_DIR / "watchdog.disabled"
WATCHDOG_LAST_NOTIFY = WATCHDOG_STATE_DIR / "watchdog-last-notify"

# Information-completeness contract (user directive 2026-09-19): the server
# must return exactly what a player can read in-game — no uncertainty, no
# fallbacks. Any payload with notify_user=true / info_complete=false triggers
# a hard stop here + a Feishu notification; further act/batch requests are
# refused until the user clears the stop flag.
INFO_STOP_FLAG = WATCHDOG_STATE_DIR / "info-incomplete-stop"
INFO_NOTIFY_SCRIPT = "/Users/xiabingquan/.claude/skills/notify/scripts/notify_feishu.py"
INFO_STOP_EXIT = 78


def _info_stop_flag_exists():
    return INFO_STOP_FLAG.exists()


def _info_extract_missing(obj):
    """Pull missing_info / notify reasons from an act_result or state payload."""
    missing = []
    if not isinstance(obj, dict):
        return missing
    for src in (obj, obj.get("state") if isinstance(obj.get("state"), dict) else None):
        if not isinstance(src, dict):
            continue
        mi = src.get("missing_info")
        if isinstance(mi, list):
            missing.extend(str(x) for x in mi)
        elif isinstance(mi, str) and mi:
            missing.append(mi)
    if obj.get("ok") is False and isinstance(obj.get("message"), str) and obj["message"].startswith("info incomplete"):
        missing.append(obj["message"])
    seen, out = set(), []
    for m in missing:
        if m not in seen:
            seen.add(m)
            out.append(m)
    return out


def _info_gate_triggered(obj):
    if not isinstance(obj, dict):
        return False
    if obj.get("notify_user") is True:
        return True
    st = obj.get("state") if isinstance(obj.get("state"), dict) else obj
    if isinstance(st, dict) and st.get("info_complete") is False:
        return True
    if obj.get("ok") is False and isinstance(obj.get("message"), str) and obj["message"].startswith("info incomplete"):
        return True
    return False


def _info_stop_and_notify(obj):
    """Hard-stop path: record the stop, ping Feishu once, exit 78."""
    missing = _info_extract_missing(obj)
    reason = "\n".join(f"- {m}" for m in missing) if missing else "- (unspecified incompleteness)"
    fingerprint = "\n".join(missing)
    already = INFO_STOP_FLAG.exists() and INFO_STOP_FLAG.read_text(encoding="utf-8").strip() == fingerprint
    WATCHDOG_STATE_DIR.mkdir(parents=True, exist_ok=True)
    INFO_STOP_FLAG.write_text(fingerprint, encoding="utf-8")
    print("[INFO-INCOMPLETE] server returned incomplete information — execution stopped (no fallback)", file=sys.stderr)
    print(reason, file=sys.stderr)
    print(f"[INFO-INCOMPLETE] stop flag: {INFO_STOP_FLAG}", file=sys.stderr)
    if not already and Path(INFO_NOTIFY_SCRIPT).exists():
        import subprocess
        content = (
            "spire-bridge 服务器返回信息不完整，已按契约停机（无 fallback）。\n"
            "游戏状态中的不确定字段：\n" + reason + "\n"
            "处理：检查 mod/game 状态后清除 stop flag 再继续：\n"
            f"  rm {INFO_STOP_FLAG}"
        )
        try:
            subprocess.run(
                ["python3", INFO_NOTIFY_SCRIPT,
                 "--title", "spire-bridge 信息不完整 — 已停机",
                 "--content", content, "--color", "red"],
                check=False, timeout=20,
            )
            print("[INFO-INCOMPLETE] feishu notify sent", file=sys.stderr)
        except Exception as e:
            print(f"[INFO-INCOMPLETE] feishu notify failed: {e}", file=sys.stderr)
    elif already:
        print("[INFO-INCOMPLETE] feishu already notified for this stop fingerprint", file=sys.stderr)
    sys.exit(INFO_STOP_EXIT)



def cmd_watchdog(args):
    """Arm, disarm, or report status of the external liveness watchdog.

    Args:
        args: Parsed CLI args; args.watchdog_cmd is enable|disable|status.

    Returns:
        Process exit code (0 on success).
    """
    WATCHDOG_STATE_DIR.mkdir(parents=True, exist_ok=True)
    if args.watchdog_cmd == "disable":
        WATCHDOG_DISARM.write_text(time.strftime("%Y-%m-%d %H:%M:%S") + "\n", encoding="utf-8")
        print(f"watchdog DISARMED ({WATCHDOG_DISARM}) — crontab entry stays, checks muted")
        return 0
    if args.watchdog_cmd == "enable":
        WATCHDOG_DISARM.unlink(missing_ok=True)
        WATCHDOG_LAST_NOTIFY.unlink(missing_ok=True)
        print("watchdog ARMED — alerts resume on game-down / bridge-down / stale-loop")
        return 0
    if WATCHDOG_DISARM.exists():
        print(f"watchdog: DISARMED since {WATCHDOG_DISARM.read_text(encoding='utf-8').strip()}")
    else:
        print("watchdog: ARMED")
    if WATCHDOG_LAST_NOTIFY.exists():
        print(f"last alert epoch: {WATCHDOG_LAST_NOTIFY.read_text(encoding='utf-8').strip()}")
    else:
        print("last feishu notify: (none recorded)")
    print(f"state dir: {WATCHDOG_STATE_DIR}")
    print(f"run log dir: {RUNLOG_DIR or 'UNSET'} (SPIREBRIDGE_LOG_DIR={'set' if os.environ.get('SPIREBRIDGE_LOG_DIR') else 'unset — required, no fallback'})")
    return 0


GAME_APP = Path(
    os.environ.get(
        "STS2_APP_PATH",
        os.path.expanduser(
            "~/Library/Application Support/Steam/steamapps/common/"
            "Slay the Spire 2/SlayTheSpire2.app"
        ),
    )
)


def game_process_running():
    """Return True when a Slay the Spire 2 process is present."""
    proc = subprocess.run(["pgrep", "-f", "Slay the Spire 2"], capture_output=True, text=True)
    return bool(proc.stdout.strip())


def suppress_crash_dialogs():
    """Silence the macOS CrashReporter dialog after hard kills."""
    subprocess.run(
        ["defaults", "write", "com.apple.CrashReporter", "DialogType", "-string", "none"],
        capture_output=True,
    )


def cmd_stop(args):
    """Stop the game: AppleEvent quit, then SIGTERM, then SIGKILL.

    Args:
        args: Parsed CLI args (unused).

    Returns:
        Process exit code (0 once the game process is gone).
    """
    del args
    suppress_crash_dialogs()
    if not game_process_running():
        print("game not running")
        return 0
    subprocess.run(
        ["osascript", "-e", 'tell application "Slay the Spire 2" to quit'],
        capture_output=True,
    )
    if wait_for(lambda: not game_process_running(), 8, interval=1.0):
        print("game quit gracefully")
        return 0
    subprocess.run(["pkill", "-f", "Slay the Spire 2"], capture_output=True)
    if wait_for(lambda: not game_process_running(), 5, interval=1.0):
        print("game stopped (SIGTERM)")
        return 0
    subprocess.run(["pkill", "-9", "-f", "Slay the Spire 2"], capture_output=True)
    wait_for(lambda: not game_process_running(), 5, interval=1.0)
    print("game stopped (forced)")
    return 0


def wait_for(predicate, timeout, interval=2.0):
    """Poll a predicate until it returns True or the timeout expires.

    Args:
        predicate: Zero-arg callable tested on each iteration.
        timeout: Maximum seconds to wait.
        interval: Sleep between polls, in seconds.

    Returns:
        True if the predicate succeeded, False on timeout.
    """
    deadline = time.time() + timeout
    while time.time() < deadline:
        if predicate():
            return True
        time.sleep(interval)
    return False


class BridgeClient:
    """Line-delimited JSON client for the in-game bridge TCP server."""

    def __init__(self, host=DEFAULT_HOST, port=DEFAULT_PORT, timeout=12.0):
        """Open a client for host:port with the given socket timeout."""
        self.host = host
        self.port = port
        self.timeout = timeout
        self.sock = None
        self.rfile = None
        self.wfile = None
        self.last_metrics = {}

    def connect(self):
        """Open the TCP connection and install buffered line streams."""
        self.sock = socket.create_connection((self.host, self.port), timeout=self.timeout)
        self.sock.settimeout(self.timeout)
        self.rfile = self.sock.makefile("r", encoding="utf-8")
        self.wfile = self.sock.makefile("w", encoding="utf-8")

    def close(self):
        """Close streams and the socket; ignore double-close errors."""
        for f in (self.rfile, self.wfile):
            try:
                if f:
                    f.close()
            except OSError:
                pass
        try:
            if self.sock:
                self.sock.close()
        except OSError:
            pass

    def request(self, payload):
        """Send one JSON request and read one JSON response line.

        Args:
            payload: Serializable request object.

        Returns:
            Parsed response dict.

        Raises:
            ConnectionError: If the server closes the connection.
            OSError, json.JSONDecodeError: Transport or payload failures.
        """
        t0 = time.perf_counter()
        fresh = self.sock is None
        if fresh:
            self.connect()
        t1 = time.perf_counter()
        assert self.wfile is not None and self.rfile is not None
        self.wfile.write(json.dumps(payload) + "\n")
        self.wfile.flush()
        line = self.rfile.readline()
        t2 = time.perf_counter()
        if not line:
            raise ConnectionError("bridge closed the connection")
        resp = json.loads(line.lstrip("﻿"))
        # Information-completeness gate: incomplete server info = hard stop +
        # Feishu, never play through uncertainty.
        if _info_gate_triggered(resp):
            _info_stop_and_notify(resp)
        self.last_metrics = {
            "connect_ms": int((t1 - t0) * 1000) if fresh else 0,
            "rtt_ms": int((t2 - t1) * 1000),
            "total_ms": int((t2 - t0) * 1000),
            "server_ms": resp.get("server_ms"),
            "queue_ms": resp.get("queue_ms"),
            "resp_bytes": len(line),
        }
        return resp

    def hello(self):
        """Request the handshake (type=hello)."""
        return self.request({"type": "hello"})

    def state(self):
        """Request a full state snapshot."""
        return self.request({"type": "state"})

    def act(self, action, args=None):
        """Submit one game action to the bridge.

        Args:
            action: Action name (play, end_turn, choose, ...).
            args: Optional JSON-serializable argument object.
        """
        payload = {"type": "act", "action": action}
        if args:
            payload["args"] = args
        return self.request(payload)

    def __enter__(self):
        """Connect and enter the context manager."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Close the connection on context exit."""
        del exc_val, exc_tb
        del exc_type
        self.close()


def combat_play_ready(state):
    """Return True when the client may legally act on this state.

    Args:
        state: Bridge state snapshot.

    Returns:
        True outside combat, on game_over, or in the player's Play phase.
    """
    screen = state.get("screen")
    if screen == "game_over" or (state.get("run") or {}).get("is_game_over"):
        return True
    if screen != "combat":
        return True
    combat = state.get("combat") or {}
    return combat.get("current_side") == "Player" and combat.get("turn_phase") == "Play"


def wait_for_settle(client, mode="settle", stall_s=3.0, stable_s=0.35):
    """Poll the bridge until state settles or the player turn resumes.

    Change-polling model (user directive 2026-09-16 — no timeout deadlines):
    keep polling while the fingerprint keeps changing; that is real game
    progress (animations, enemy turns) and is worth waiting through. The
    only early-out besides reaching the target condition is a FROZEN
    fingerprint: if state does not change for stall_s and the condition is
    still unmet, return the current snapshot flagged stalled=True so the
    caller can re-read and decide — never block on an idle game.

    Args:
        client: Connected BridgeClient.
        mode: "settle" waits for a stable fingerprint; "play" additionally
            requires combat_play_ready (Play phase / non-combat / game_over).
        stall_s: Frozen-fingerprint window that ends the poll as stalled.
        stable_s: Fingerprint stability window required to declare settled.

    Returns:
        Tuple (state, settle_ms, stalled): last snapshot, polling wall time,
        and whether the wait ended without reaching the target condition.

    Raises:
        ConnectionError, OSError, json.JSONDecodeError: Bridge failures are
            caught and returned as stalled=True.
    """
    t0 = time.perf_counter()
    state = client.state()
    last_fp = state.get("fingerprint")
    stable_since = time.perf_counter()
    while True:
        time.sleep(0.15)
        try:
            state = client.state()
        except (ConnectionError, OSError, json.JSONDecodeError) as exc:
            print(f"settle poll failed: {exc}")
            return state, int((time.perf_counter() - t0) * 1000), True
        now = time.perf_counter()
        fp = state.get("fingerprint")
        if fp != last_fp:
            last_fp = fp
            stable_since = now
        elapsed = now - t0
        if mode == "play":
            if combat_play_ready(state) and now - stable_since >= stable_s:
                return state, int(elapsed * 1000), False
        else:
            if now - stable_since >= stable_s:
                return state, int(elapsed * 1000), False
        if now - stable_since >= stall_s:
            return state, int(elapsed * 1000), True


def metrics_line(metrics):
    """Format timing metrics for one-line CLI output.

    Args:
        metrics: Dict with optional rtt_ms/connect_ms/server_ms/queue_ms.

    Returns:
        Space-separated key=value line, empty when metrics is falsy.
    """
    if not metrics:
        return ""
    bits = [f"rtt={metrics.get('rtt_ms')}ms"]
    if metrics.get("connect_ms"):
        bits.append(f"conn={metrics['connect_ms']}ms")
    if metrics.get("server_ms") is not None:
        bits.append(f"srv={metrics['server_ms']}ms")
    if metrics.get("queue_ms") is not None:
        bits.append(f"queue={metrics['queue_ms']}ms")
    return " ".join(bits)


def fmt_power(p):
    """Compact power label: ID or ID:amount (kill-timer amounts must be visible)."""
    pid = p.get("id", "?")
    amt = p.get("amount")
    return f"{pid}:{amt}" if amt is not None else pid


# ---------------------------------------------------------------------------
# JSON reference DB — references/game/*.json + *_zh.json (key = live game id)
# ---------------------------------------------------------------------------

REF_DIR = REPO_ROOT / "references" / "game"

# Domain priority for bare-key resolution (first match wins; --all overrides).
REF_DOMAIN_FILES = [
    ("move", "monsters"),        # flattened from monsters[*].moves[*]
    ("power", "powers"),
    ("relic", "relics"),
    ("card", "cards"),
    ("potion", "potions"),
    ("event_option", "events"),  # flattened from events[*].options[*]
    ("event", "events"),
    ("affliction", "afflictions"),
    ("status_card", "afflictions"),
    ("intent_class", "intents"),
    ("intent_type", "intents"),
    ("character", "characters"),
    ("monster", "monsters"),
]

# spire-codex.com URL patterns: https://spire-codex.com/{category}/{lowercase_id}
# (underscores work unencoded; category chosen by id shape).
CODEX_BASE = "https://spire-codex.com"

_REF_INDEX_CACHE = {}


def load_reference_index(lang="en"):
    """Load references/game/*.json (or *_zh.json) into {key: (domain, entry)}.

    Flattens nested keys: monsters[*].moves[*] -> move domain,
    events[*].options[*] -> event_option. Registers entry['id'], every
    aliases[] element, and id case-variants. Cached per lang.
    """
    if lang in _REF_INDEX_CACHE:
        return _REF_INDEX_CACHE[lang]
    index = {}
    suffix = "_zh.json" if lang == "zh" else ".json"
    if not REF_DIR.is_dir():
        print(
            f"lookup: reference dir missing: {REF_DIR} — "
            "generate it with scripts/build_game_reference_json.py",
            file=sys.stderr,
        )
        _REF_INDEX_CACHE[lang] = index
        return index

    def register(key, domain, entry):
        if not key or not isinstance(key, str):
            return
        if key not in index:
            index[key] = (domain, entry)

    for domain, stem in REF_DOMAIN_FILES:
        path = REF_DIR / f"{stem}{suffix}"
        if not path.exists():
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            print(f"lookup: failed to read {path.name}: {exc}", file=sys.stderr)
            continue
        if not isinstance(data, dict):
            continue
        for key, entry in data.items():
            if not isinstance(entry, dict):
                continue
            entry_kind = entry.get("kind") or domain
            register(key, entry_kind, entry)
            register(entry.get("id"), entry_kind, entry)
            for alias in entry.get("aliases") or []:
                if isinstance(alias, str):
                    register(alias, entry_kind, entry)
            register(key.upper(), entry_kind, entry)
            moves = entry.get("moves")
            if isinstance(moves, dict):
                for move_key, move_entry in moves.items():
                    if not isinstance(move_entry, dict):
                        continue
                    register(move_key, "move", move_entry)
                    register(move_entry.get("id"), "move", move_entry)
                    for alias in move_entry.get("aliases") or []:
                        if isinstance(alias, str):
                            register(alias, "move", move_entry)
            options = entry.get("options")
            if isinstance(options, dict):
                for opt_key, opt_entry in options.items():
                    if not isinstance(opt_entry, dict):
                        continue
                    register(opt_key, "event_option", opt_entry)
                    register(opt_entry.get("id"), "event_option", opt_entry)
                    for alias in opt_entry.get("aliases") or []:
                        if isinstance(alias, str):
                            register(alias, "event_option", opt_entry)
    _REF_INDEX_CACHE[lang] = index
    return index


def lookup_reference(key, lang="en", domain=None, match_all=False):
    """Resolve a live game id against the JSON reference DB.

    Resolution ladder: exact key -> event textKey / prefix before '.pages.'
    -> case-insensitive -> suffix probes (X+ -> X; STRIKE family).
    Returns list of (domain, entry); empty list = loud miss.
    """
    if not key:
        return []
    index = load_reference_index(lang)
    candidates = []
    seen = set()

    def consider(k):
        if not k or not isinstance(k, str) or k in seen:
            return
        seen.add(k)
        hit = index.get(k)
        if hit is None:
            return
        if domain and hit[0] != domain and not hit[0].startswith(domain):
            return
        candidates.append(hit)

    consider(key)
    if ".pages." in key:
        consider(key.split(".pages.", 1)[0])
    if "." in key:
        consider(key.split(".")[0])
    if not candidates:
        lowered = key.lower()
        for k in index:
            if k.lower() == lowered:
                consider(k)
    if not candidates and key.endswith("+"):
        consider(key[:-1])
    if not candidates and key.startswith("STRIKE"):
        for k in index:
            if k.startswith("STRIKE"):
                consider(k)
    if not candidates and not domain:
        for k in index:
            if k.endswith(key) or key.endswith(k):
                consider(k)
                if not match_all and candidates:
                    break
    return candidates if match_all else candidates[:1]


def ref_tags_enabled(explicit=None):
    """True when compact auto-lookup tags should render."""
    if explicit is not None:
        return explicit
    env = os.environ.get("SPIREBRIDGE_REF_TAGS", "").strip().lower()
    if env in ("0", "false", "off", "no"):
        return False
    return bool(load_reference_index(os.environ.get("SPIREBRIDGE_REF_LANG", "en")))


def format_intent_bits(intents, move_id=None):
    """Build compact intent descriptors from structured intent dicts."""
    bits = []
    for it in intents or []:
        label = strip_bbcode(it.get("label") or "") or None
        dmg = it.get("damage")
        hits = it.get("hits")
        card_count = it.get("card_count")
        itype = (it.get("type") or "").strip()
        iclass = it.get("class") or ""
        if dmg is not None and isinstance(hits, int) and hits > 1:
            desc = f"multi:{dmg}x{hits}"
        elif dmg is not None:
            total = it.get("total_damage")
            desc = f"atk:{dmg}"
            if total is not None and total != dmg:
                desc += f"(tot{total})"
        elif card_count is not None:
            desc = f"status:{card_count}c"
        elif itype:
            desc = itype.lower()
            if label and label.lower() not in desc and not label.replace(".", "").isdigit():
                desc = f"{desc}:{label}"
        elif label:
            desc = label
        else:
            desc = (iclass.lower() or "unknown")
        if "FORMAT_EMPTY" in desc:
            desc = (itype or iclass or "unknown").lower()
            if move_id:
                desc = f"{desc}({move_id})"
        base = it.get("base_damage")
        if base is not None and dmg is not None and base != dmg:
            desc += f"[base{base}]"
        bits.append(desc)
    return bits


CODEX_API = "https://spire-codex.com/api"
_CODEX_MOVE_INDEX = None
_CODEX_API_CACHE = {}


def codex_api_get(path, timeout=10.0):
    """GET a spire-codex.com API path, return parsed JSON or None.

    Cache-first: every successful payload is kept per-process so a burst of
    lookups on the same monster/index does not re-hit the network.
    """
    if path in _CODEX_API_CACHE:
        return _CODEX_API_CACHE[path]
    import urllib.request

    url = CODEX_API + path
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "spirectl-lookup/0.2 (+spire-copilot-bridge)",
            "Accept": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8", errors="replace"))
    except Exception:
        return None
    if isinstance(data, dict) and data.get("detail") and len(data) == 1:
        return None
    _CODEX_API_CACHE[path] = data
    return data


def codex_move_index():
    """Build {live_move_id: (monster_dict, move_dict)} from /api/monsters.

    API move ids carry no _MOVE suffix (SEA_KICK) while live state emits
    SEA_KICK_MOVE — both shapes are registered. Cached per process; the full
    monster list (~115 entries) is fetched once.
    """
    global _CODEX_MOVE_INDEX
    if _CODEX_MOVE_INDEX is not None:
        return _CODEX_MOVE_INDEX
    index = {}
    data = codex_api_get("/monsters")
    if isinstance(data, list):
        for monster in data:
            if not isinstance(monster, dict):
                continue
            for move in monster.get("moves") or []:
                if not isinstance(move, dict):
                    continue
                mid = move.get("id")
                if not mid:
                    continue
                index[mid] = (monster, move)
                index[f"{mid}_MOVE"] = (monster, move)
    _CODEX_MOVE_INDEX = index
    return index


def codex_search(kind_path, query, timeout=10.0):
    """Query the codex search endpoint, e.g. /powers?search=ravenous."""
    import urllib.parse

    q = urllib.parse.quote(query)
    data = codex_api_get(f"/{kind_path}?search={q}", timeout=timeout)
    return data if isinstance(data, list) else []


def strip_codex_markup(text):
    """Remove codex inline markup like [green]6[/green] / [sine]...[/sine]."""
    if not isinstance(text, str):
        return ""
    return BBCODE_RE.sub("", text).strip()


def _format_damage(damage):
    """Render codex damage dict: {'normal':11,'ascension':13,'hit_count':4}."""
    if damage is None:
        return None
    if isinstance(damage, (int, float)):
        return str(damage)
    if not isinstance(damage, dict):
        return str(damage)
    normal = damage.get("normal")
    asc = damage.get("ascension")
    hits = damage.get("hit_count")
    parts = []
    if hits:
        parts.append(f"{normal}x{hits}")
    elif normal is not None:
        parts.append(str(normal))
    if asc is not None:
        parts.append(f"A:{asc}")
    return " ".join(parts) or None


def describe_move_from_api(monster, move):
    """Build effect/play text for one codex move entry."""
    bits = []
    intent = move.get("intent")
    if intent:
        bits.append(str(intent))
    dmg = _format_damage(move.get("damage"))
    if dmg:
        bits.append(f"damage {dmg}")
    if move.get("block") is not None:
        bits.append(f"block {move['block']}")
    if move.get("heal") is not None:
        bits.append(f"heal {move['heal']}")
    for power in move.get("powers") or []:
        if not isinstance(power, dict):
            continue
        pid = power.get("power_id") or power.get("id") or "?"
        amt = power.get("amount")
        target = power.get("target")
        ptxt = pid if amt is None else f"{pid} {amt}"
        if target:
            ptxt += f" ({target})"
        bits.append(ptxt)
    effect = move.get("name") or move.get("id") or "move"
    if bits:
        effect = f"{effect}: " + "; ".join(bits)
    return effect


def build_monster_entry_from_api(monster, live_key=None):
    """Full monsters.json entry from a codex monster payload (live-id keys)."""
    api_id = monster.get("id") or ""
    moves = {}
    cycle = []
    for move in monster.get("moves") or []:
        if not isinstance(move, dict):
            continue
        api_move_id = move.get("id")
        if not api_move_id:
            continue
        live_move_id = f"{api_move_id}_MOVE"
        cycle.append(live_move_id)
        moves[live_move_id] = {
            "id": live_move_id,
            "kind": "move",
            "monster_id": api_id,
            "name": move.get("name") or api_move_id,
            "intents": [
                {
                    "class": (
                        "SingleAttackIntent" if (move.get("damage") or {}).get("hit_count") in (None, 1)
                        else "MultiAttackIntent"
                    ) if move.get("damage") else None,
                    "type": move.get("intent"),
                    "base_damage": (move.get("damage") or {}).get("normal") if isinstance(move.get("damage"), dict) else None,
                    "base_damage_ascension": {"ascension": (move.get("damage") or {}).get("ascension")} if isinstance(move.get("damage"), dict) and (move.get("damage") or {}).get("ascension") is not None else None,
                    "hits": (move.get("damage") or {}).get("hit_count") if isinstance(move.get("damage"), dict) else None,
                }
            ],
            "effect": describe_move_from_api(monster, move),
            "follow_up_id": f"{cycle[-2]}_MOVE" if False else None,
            "play_notes": "",
            "aliases": [move.get("name") or api_move_id, api_move_id],
            "curated": False,
            "needs_zh": True,
            "source": f"codex-api:/monsters/{api_id}#{api_move_id}",
        }
        # Drop null intent-class field
        if moves[live_move_id]["intents"][0].get("class") is None:
            moves[live_move_id]["intents"][0].pop("class", None)
    hp = {
        "base": monster.get("min_hp"),
        "max": monster.get("max_hp"),
        "notes": "",
    }
    if monster.get("min_hp_ascension") is not None:
        hp["ascension"] = {"min": monster.get("min_hp_ascension"), "max": monster.get("max_hp_ascension")}
    entry = {
        "id": api_id,
        "kind": "monster",
        "name": monster.get("name") or api_id,
        "type": monster.get("type"),
        "acts": [],
        "hp": hp,
        "is_boss": (monster.get("type") or "").lower() == "boss",
        "is_elite": (monster.get("type") or "").lower() == "elite",
        "cycle": cycle,
        "moves": moves,
        "aliases": [monster.get("name") or api_id],
        "description": (
            f"{monster.get('name') or api_id} ({monster.get('type') or 'monster'}): "
            f"HP {monster.get('min_hp')}-{monster.get('max_hp')} "
            f"(A {monster.get('min_hp_ascension')}-{monster.get('max_hp_ascension')}); "
            f"cycle {' → '.join(cycle) if cycle else 'unknown'}"
        ),
        "play_notes": "",
        "curated": False,
        "needs_zh": True,
        "source": f"codex-api:/monsters/{api_id}",
    }
    return entry


def fold_monster_entry(entry, live_key=None):
    """Merge a monster entry into monsters.json + monsters_zh.json."""
    api_id = entry.get("id")
    target_key = api_id
    for lang in ("en", "zh"):
        suffix = "_zh.json" if lang == "zh" else ".json"
        path = REF_DIR / f"monsters{suffix}"
        data = {}
        if path.exists():
            try:
                loaded = json.loads(path.read_text(encoding="utf-8"))
                if isinstance(loaded, dict):
                    data = loaded
            except (OSError, json.JSONDecodeError):
                data = {}
        existing = data.get(target_key)
        if isinstance(existing, dict) and existing.get("curated") is True:
            # Keep curated monster; still merge uncurated live-key aliases
            continue
        zh_entry = dict(entry)
        if lang == "zh":
            zh_entry["needs_zh"] = True
        data[target_key] = zh_entry
        REF_DIR.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    _REF_INDEX_CACHE.clear()


def fold_entry_into_reference(domain_stem, key, entry, lang="en"):
    """Write/merge one entry into references/game/<stem>.json (+ _zh.json)."""
    suffix = "_zh.json" if lang == "zh" else ".json"
    path = REF_DIR / f"{domain_stem}{suffix}"
    data = {}
    if path.exists():
        try:
            loaded = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(loaded, dict):
                data = loaded
        except (OSError, json.JSONDecodeError):
            data = {}
    existing = data.get(key)
    if isinstance(existing, dict) and existing.get("curated") is True:
        return path, False
    data[key] = entry
    REF_DIR.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path, True


def codex_candidate_urls(key):
    """Build spire-codex.com HTML candidate URLs (last-resort fallback)."""
    slug = key.lower().replace(" ", "_")
    candidates = []
    if "_MOVE" in key:
        stem = slug
        for suffix in ("_move",):
            if stem.endswith(suffix):
                stem = stem[: -len(suffix)]
        candidates.extend([f"{CODEX_BASE}/monsters/{slug}", f"{CODEX_BASE}/monsters/{stem}"])
    elif key.endswith("_POWER"):
        candidates.append(f"{CODEX_BASE}/powers/{slug}")
    elif key.endswith("_POTION") or "POTION" in key:
        candidates.append(f"{CODEX_BASE}/potions/{slug}")
    elif ".pages." in key:
        event = key.split(".pages.", 1)[0].lower()
        candidates.append(f"{CODEX_BASE}/events/{event}")
    elif key.isupper() or "_" in key:
        for category in ("relics", "cards", "potions", "powers", "events", "monsters", "characters"):
            candidates.append(f"{CODEX_BASE}/{category}/{slug}")
    else:
        for category in ("reference", "powers", "monsters", "cards"):
            candidates.append(f"{CODEX_BASE}/{category}/{slug}")
    deduped = []
    seen = set()
    for url in candidates:
        if url not in seen:
            seen.add(url)
            deduped.append(url)
    return deduped[:8]


def fetch_codex_text(url, timeout=12.0):
    """Best-effort HTML fetch, returned as plain text (last-resort fallback)."""
    import html as html_mod
    import re as re_mod
    import urllib.request

    req = urllib.request.Request(
        url,
        headers={"User-Agent": "spirectl-lookup/0.2 (+spire-copilot-bridge)"},
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        raw = resp.read().decode("utf-8", errors="replace")
    raw = re_mod.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", " ", raw)
    raw = re_mod.sub(r"(?is)<br\s*/?>|</p>|</div>|</li>|</h[1-6]>", "\n", raw)
    text = re_mod.sub(r"(?s)<[^>]+>", " ", raw)
    text = html_mod.unescape(text)
    text = re_mod.sub(r"[ \t]+", " ", text)
    text = re_mod.sub(r"\n\s*\n+", "\n", text)
    return text.strip()


def research_and_fold(key, domain_guess=None):
    """Lookup-miss fallback: spire-codex.com API first, HTML last.

    Returns (entry, source) when research produced data, else (None, None).
    Folded entries carry key = the LIVE id (state's shape); API ids land in
    aliases. Entries are curated:false — agent curation completes them.
    """
    source = None
    kind = domain_guess
    entry = None

    # ---------- API-first per domain ----------
    # Power ids: live shape has _POWER suffix; API ids usually don't.
    power_queries = [key]
    if key.endswith("_POWER"):
        power_queries.append(key[: -len("_POWER")])
    power_queries.append(key.replace("_", " ").lower())

    api_candidates = []
    if kind == "move" or "_MOVE" in key:
        index = codex_move_index()
        hit = index.get(key) or index.get(key.replace("_MOVE", ""))
        if hit:
            monster, move = hit
            entry = build_monster_entry_from_api(monster)
            source = f"codex-api:/monsters/{monster.get('id')}"
            kind = "move"
    if entry is None and (kind == "monster" or (kind is None and key.isupper())):
        data = codex_api_get(f"/monsters/{key.lower()}")
        if data is None:
            results = codex_search("monsters", key.replace("_", " ").lower())
            data = results[0] if results else None
        if isinstance(data, dict) and data.get("id"):
            entry = build_monster_entry_from_api(data)
            source = f"codex-api:/monsters/{data.get('id')}"
            kind = "monster"
    if entry is None and (kind in ("relic", None) or key.endswith("_PEARL") or key.isupper()):
        data = codex_api_get(f"/relics/{key.lower()}")
        if data is None:
            results = codex_search("relics", key.replace("_", " ").lower())
            data = results[0] if results else None
        if isinstance(data, dict) and data.get("id"):
            description = strip_codex_markup(data.get("description") or data.get("description_raw") or "")
            entry = {
                "id": key,
                "kind": "relic",
                "name": data.get("name") or key,
                "rarity": data.get("rarity_key") or data.get("rarity"),
                "character": data.get("pool"),
                "description": description,
                "aliases": [data.get("name"), data.get("id")],
                "play_notes": "",
                "curated": False,
                "needs_zh": True,
                "source": f"codex-api:/relics/{data.get('id')}",
            }
            source = entry["source"]
            kind = "relic"
    if entry is None and (kind in ("card", None) or key.endswith("_STRIKE") or key.endswith("_IRONCLAD")):
        data = codex_api_get(f"/cards/{key.lower()}")
        if data is None:
            results = codex_search("cards", key.replace("_", " ").lower())
            data = results[0] if results else None
        if isinstance(data, dict) and data.get("id"):
            description = strip_codex_markup(data.get("description") or data.get("description_raw") or "")
            entry = {
                "id": key,
                "kind": "card",
                "name": data.get("name") or key,
                "cost": data.get("cost"),
                "card_type": data.get("type_key") or data.get("type"),
                "rarity": data.get("rarity_key") or data.get("rarity"),
                "target_type": data.get("target"),
                "character_pool": data.get("color"),
                "description": description,
                "aliases": [data.get("name"), data.get("id")],
                "play_notes": "",
                "curated": False,
                "needs_zh": True,
                "source": f"codex-api:/cards/{data.get('id')}",
            }
            source = entry["source"]
            kind = "card"
    if entry is None and (kind in ("potion", None) or key.endswith("_POTION") or "POTION" in key):
        data = codex_api_get(f"/potions/{key.lower()}")
        if data is None:
            results = codex_search("potions", key.replace("_", " ").lower())
            data = results[0] if results else None
        if isinstance(data, dict) and data.get("id"):
            description = strip_codex_markup(data.get("description") or data.get("description_raw") or "")
            entry = {
                "id": key,
                "kind": "potion",
                "name": data.get("name") or key,
                "rarity": data.get("rarity_key") or data.get("rarity"),
                "description": description,
                "aliases": [data.get("name"), data.get("id")],
                "play_notes": "",
                "curated": False,
                "needs_zh": True,
                "source": f"codex-api:/potions/{data.get('id')}",
            }
            source = entry["source"]
            kind = "potion"
    if entry is None and kind in ("power", None):
        data = None
        for query in power_queries:
            data = codex_api_get(f"/powers/{query.lower()}")
            if data is not None:
                break
        if data is None:
            for query in power_queries:
                results = codex_search("powers", query.replace("_", " ").lower())
                if results:
                    data = results[0]
                    break
        if isinstance(data, dict) and data.get("id"):
            description = strip_codex_markup(data.get("description") or data.get("description_raw") or "")
            entry = {
                "id": key,
                "kind": "power",
                "name": data.get("name") or key,
                "power_type": data.get("type"),
                "stack_type": data.get("stack_type"),
                "counter_class": (data.get("stack_type") == "Counter"),
                "description": description,
                "aliases": [data.get("name"), data.get("id"), key.replace("_POWER", "")],
                "play_notes": "",
                "curated": False,
                "needs_zh": True,
                "source": f"codex-api:/powers/{data.get('id')}",
            }
            source = entry["source"]
            kind = "power"
    if entry is None and (kind in ("event", "event_option", None) or ".pages." in key):
        event_id = key.split(".pages.", 1)[0] if ".pages." in key else key
        data = codex_api_get(f"/events/{event_id.lower()}")
        if data is None:
            results = codex_search("events", event_id.replace("_", " ").lower())
            data = results[0] if results else None
        if isinstance(data, dict) and data.get("id"):
            description = strip_codex_markup(data.get("description") or "")
            options_blob = data.get("options") or data.get("pages") or []
            entry = {
                "id": event_id,
                "kind": "event",
                "name": data.get("name") or event_id,
                "acts": [data.get("act")] if data.get("act") else [],
                "description": description,
                "option_summary": json.dumps(options_blob, ensure_ascii=False)[:600] if options_blob else "",
                "aliases": [data.get("name"), data.get("id")],
                "play_notes": "",
                "curated": False,
                "needs_zh": True,
                "source": f"codex-api:/events/{data.get('id')}",
                "options": {},
            }
            # Fold the specific event_option key when the miss was an option.
            if ".pages." in key:
                option_entry = {
                    "id": key,
                    "kind": "event_option",
                    "event_id": event_id,
                    "title": key.rsplit(".", 1)[-1].replace("_", " ").title(),
                    "description": description,
                    "aliases": [key.rsplit(".", 1)[-1]],
                    "play_notes": "",
                    "curated": False,
                    "needs_zh": True,
                    "source": f"codex-api:/events/{data.get('id')}",
                }
                entry["options"][key] = option_entry
            source = entry["source"]
            kind = kind or "event"

    # ---------- HTML last resort ----------
    if entry is None:
        urls = codex_candidate_urls(key)
        best_text = ""
        best_url = None
        for url in urls:
            try:
                text = fetch_codex_text(url)
            except Exception:
                continue
            if not text or len(text) < 80:
                continue
            human = key.replace("_", " ").lower()
            if key.lower() not in text.lower() and human not in text.lower():
                continue
            best_text = text
            best_url = url
            break
        if not best_text:
            return None, None
        nav_markers = (
            "spire codex", "compendium", "card library", "relic collection",
            "potion lab", "jump back in", "pages you open", "stats", "rankings",
            "tier list", "leaderboard", "submit a run", "browse runs", "tools",
            "companion apps", "steam mod", "art exporter", "overlay",
            "knowledge demon bot", "sign in", "cookie", "press .",
        )
        human = key.replace("_", " ").lower()
        lines = [ln.strip() for ln in best_text.splitlines() if ln.strip()]
        body = []
        total = 0
        started = False
        for ln in lines:
            low = ln.lower()
            if not started:
                if key.lower() in low or human in low:
                    started = True
                else:
                    continue
            if any(m in low for m in nav_markers) and len(ln) < 60:
                continue
            if low.startswith("http"):
                continue
            body.append(ln)
            total += len(ln)
            if total > 600:
                break
        if not body:
            body = [ln for ln in lines if not any(m in ln.lower() for m in nav_markers)][:8]
        description = " ".join(body)[:700]
        # Infer kind/stem from the HTML URL category — fail-loud when the
        # category is unrecognizable instead of folding into a random domain.
        url_kind = None
        url_stem = None
        safe_url = best_url or ""
        for cat, knd in (
            ("relics", "relic"), ("cards", "card"), ("powers", "power"),
            ("potions", "potion"), ("events", "event"), ("monsters", "monster"),
            ("characters", "character"),
        ):
            if f"/{cat}/" in safe_url:
                url_kind, url_stem = knd, cat
                break
        kind = url_kind or kind
        if not kind or kind == "unknown":
            return None, None
        entry = {
            "id": key,
            "kind": kind,
            "name": key,
            "description": description,
            "aliases": [],
            "play_notes": "",
            "curated": False,
            "needs_zh": True,
            "source": f"codex-html:{best_url}",
        }
        source = entry["source"]

    # ---------- Fold ----------
    stem = {
        "move": "monsters",
        "monster": "monsters",
        "power": "powers",
        "relic": "relics",
        "card": "cards",
        "potion": "potions",
        "event": "events",
        "event_option": "events",
        "affliction": "afflictions",
        "status_card": "afflictions",
        "intent_class": "intents",
        "intent_type": "intents",
        "character": "characters",
    }.get(kind or "", "relics")

    if stem == "monsters" and isinstance(entry, dict) and entry.get("kind") == "monster" and entry.get("moves"):
        fold_monster_entry(entry, live_key=key)
        return entry, source
    if stem == "monsters" and "_MOVE" in key:
        # Move-level stub nested under generic host (rare fallback path).
        path = REF_DIR / "monsters.json"
        data = {}
        if path.exists():
            try:
                loaded = json.loads(path.read_text(encoding="utf-8"))
                if isinstance(loaded, dict):
                    data = loaded
            except (OSError, json.JSONDecodeError):
                data = {}
        generic = data.get("generic")
        if not isinstance(generic, dict):
            generic = {"id": "generic", "kind": "monster", "name": "generic", "description": "synthetic host for move stubs", "aliases": [], "play_notes": "", "curated": False, "needs_zh": True, "source": "synthetic", "moves": {}}
        moves = generic.get("moves")
        if not isinstance(moves, dict):
            moves = {}
        stub = dict(entry)
        stub["kind"] = "move"
        if key not in moves or moves.get(key, {}).get("curated") is not True:
            moves[key] = stub
        generic["moves"] = moves
        data["generic"] = generic
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        _REF_INDEX_CACHE.clear()
        return stub, source
    if stem == "events" and isinstance(entry, dict) and entry.get("kind") == "event":
        event_id = entry.get("id")
        for lang in ("en", "zh"):
            suffix = "_zh.json" if lang == "zh" else ".json"
            path = REF_DIR / f"events{suffix}"
            data = {}
            if path.exists():
                try:
                    loaded = json.loads(path.read_text(encoding="utf-8"))
                    if isinstance(loaded, dict):
                        data = loaded
                except (OSError, json.JSONDecodeError):
                    data = {}
            existing = data.get(event_id)
            if isinstance(existing, dict) and existing.get("curated") is True:
                continue
            payload = json.loads(json.dumps(entry))
            if lang == "zh":
                payload["needs_zh"] = True
            data[event_id] = payload
            path.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        _REF_INDEX_CACHE.clear()
        return entry, source
    fold_entry_into_reference(stem, key, entry, lang="en")
    zh_entry = json.loads(json.dumps(entry))
    zh_entry["needs_zh"] = True
    fold_entry_into_reference(stem, key, zh_entry, lang="zh")
    _REF_INDEX_CACHE.clear()
    return entry, source


def render_compact(state):
    """Render a bridge state snapshot as compact human-readable lines.

    Always prints move_id for monsters (dropping it on numeric intent labels
    was the root cause of "intent=11" information loss). Structured intent
    fields (damage/hits/base_damage/card_count) take priority over the label
    string; reference-DB snippets append when available.
    """
    use_tags = ref_tags_enabled(None)
    ref_index = load_reference_index(os.environ.get("SPIREBRIDGE_REF_LANG", "en")) if use_tags else {}
    lines = []
    run = state.get("run") or {}
    player = state.get("player") or {}
    combat = state.get("combat")
    screen = state.get("screen", "?")
    parts = [f"screen={screen}"]
    if state.get("screen_type"):
        parts.append(f"type={state['screen_type']}")
    if run:
        parts.append(f"floor={run.get('total_floor')}")
        parts.append(f"act={(run.get('act_index') or 0) + 1}")
        parts.append(f"room={run.get('room_type')}")
        if run.get("ascension") is not None:
            parts.append(f"asc={run.get('ascension')}")
        if run.get("seed"):
            parts.append(f"seed={run.get('seed')}")
        if run.get("map_coord"):
            c = run["map_coord"]
            parts.append(f"pos=({c.get('row')},{c.get('col')})")
    lines.append(" | ".join(parts))
    # Act-start boon rooms (Ancient/Neow-family, e.g. 先古移民 HP restore) are
    # easy to skip: the game lands on the row-1 map and available_map_points
    # historically omitted the start room. Surface it loudly while unvisited.
    # Ancient-typed check is defensive: is_boon_room is computed in StateBuilder
    # from point_type, but a stale/older mod build may not flag it yet.
    start_room = run.get("act_start_room") or {}
    if start_room and not start_room.get("visited") and (
        start_room.get("is_boon_room") or start_room.get("point_type") in ("Ancient", "Neow", "NeowBoon")
    ):
        lines.append(
            f"ACT-START BOON ROOM UNVISITED: ({start_room.get('row')},{start_room.get('col')})"
            f"={start_room.get('point_type')} — map_select it BEFORE any row-1+ point"
        )
    if player:
        gold = player.get("gold")
        gold_s = f" gold={gold}" if gold is not None else ""
        char_s = f" char={player.get('character')}" if player.get("character") else ""
        lines.append(f"player hp={player.get('hp')}/{player.get('max_hp')} block={player.get('block')}{gold_s}{char_s}")
        # player powers/debuffs mirror creature powers during combat
        combat_p = state.get("combat") or {}
        me = next((c for c in (combat_p.get("creatures") or []) if c.get("is_player")), None)
        if me and me.get("powers"):
            lines.append("player powers: " + ", ".join(fmt_power(p) for p in me["powers"]))
        relics = player.get("relics") or []
        if relics:
            relic_bits = []
            for r in relics:
                rid = r.get("id", "?")
                counter = r.get("counter")
                if counter is not None:
                    rid = f"{rid}:{counter}"
                relic_bits.append(rid)
            lines.append("relics: " + ", ".join(relic_bits))
        potions = [p for p in (player.get("potions") or []) if p]
        if potions:
            lines.append("potions: " + ", ".join(f"[{p['index']}]{p.get('id')}" for p in potions))
    if combat:
        lines.append(
            f"combat round={combat.get('round')} side={combat.get('current_side')} "
            f"phase={combat.get('turn_phase')} energy={combat.get('energy')}/{combat.get('max_energy')}"
        )
        graph_lines = []
        for c in combat.get("creatures") or []:
            mark = "*" if c.get("is_player") else "-"
            line = (
                f" {mark} id{c.get('combat_id')} {c.get('name')} "
                f"hp={c.get('hp')}/{c.get('max_hp')} block={c.get('block')}"
            )
            powers = c.get("powers") or []
            if powers:
                line += " powers=[" + ",".join(fmt_power(p) for p in powers) + "]"
            # move_id prints unconditionally — identity must never be dropped.
            move = c.get("move_id")
            if move:
                line += f" move={move}"
            intents = c.get("intents") or []
            if intents:
                line += " intent=" + "; ".join(format_intent_bits(intents, move_id=move))
            if move and ref_index:
                hit = ref_index.get(move) or ref_index.get(str(move).upper())
                if hit:
                    entry = hit[1]
                    snippet = entry.get("effect") or entry.get("description") or entry.get("play_notes") or ""
                    snippet = " ".join(str(snippet).split())[:60]
                    if snippet:
                        line += f" [{move}: {snippet}]"
            lines.append(line)
            graph = c.get("move_graph")
            if graph and not c.get("is_player"):
                gbits = [f"id{c.get('combat_id')} {c.get('name')}"]
                log = graph.get("state_log") or []
                if log:
                    gbits.append("log=[" + ",".join(str(x) for x in log) + "]")
                current = graph.get("current_move_id")
                if current:
                    gbits.append(f"current={current}")
                states = graph.get("states") or []
                follow_map = {
                    s.get("id"): s.get("follow_up_id")
                    for s in states
                    if s.get("kind") == "move" and s.get("follow_up_id")
                }
                if current and follow_map:
                    cycle = [current]
                    nxt = follow_map.get(current)
                    seen_cycle = {current}
                    while nxt and nxt not in seen_cycle and len(cycle) < 12:
                        cycle.append(nxt)
                        seen_cycle.add(nxt)
                        nxt = follow_map.get(nxt)
                    if len(cycle) > 1:
                        gbits.append("cycle=" + "→".join(str(x) for x in cycle))
                for s in states:
                    if s.get("kind") == "random_branch":
                        rbits = []
                        for b in s.get("branches") or []:
                            w = b.get("effective_weight", b.get("weight"))
                            wtxt = f" w={w:.2f}" if isinstance(w, (int, float)) else ""
                            rbits.append(f"{b.get('state_id')}{wtxt}")
                        gbits.append(f"branch@{s.get('id')}: " + " ".join(rbits))
                    elif s.get("kind") == "conditional_branch":
                        cbits = []
                        for b in s.get("branches") or []:
                            met = b.get("condition_met")
                            tag = "[ok]" if met is True else "[no]" if met is False else ""
                            cbits.append(f"{b.get('state_id')}{tag}")
                        gbits.append(f"cond@{s.get('id')}: " + " ".join(cbits))
                graph_lines.append("  " + " ".join(gbits))
        if graph_lines:
            lines.append("move graphs:")
            lines.extend(graph_lines)
        history = combat.get("history") or []
        if history:
            tail = history[-6:]
            lines.append("history: " + " | ".join(
                str(h.get("text") or h.get("kind")) for h in tail
            ))
        piles = combat.get("piles") or {}
        play_count = piles.get("play_count")
        play_s = f" play={play_count}" if play_count is not None else ""
        lines.append(
            f"piles draw={piles.get('draw_count')} discard={piles.get('discard_count')} "
            f"exhaust={piles.get('exhaust_count')}{play_s}"
        )
        for card in piles.get("hand") or []:
            playable = "ok" if card.get("can_play") else f"no({card.get('unplayable_reason')})"
            lines.append(
                f" [{card.get('index')}] {card.get('id')} cost={card.get('cost')} "
                f"target={card.get('target_type')} {playable}"
            )
    detail = state.get("screen_detail") or {}
    options = detail.get("options") or []
    if options:
        lines.append("options:")
        for opt in options:
            desc = opt.get("description")
            desc_s = ""
            if desc:
                flat = " ".join(str(desc).split())[:80]
                desc_s = f" — {flat}"
            lines.append(f" [{opt.get('index')}] {opt.get('kind')}:{opt.get('id')} {opt.get('name') or ''}{desc_s}")
    actions = state.get("available_actions") or []
    if actions:
        summaries = []
        for a in actions:
            name = a.get("action")
            args = a.get("args") or {}
            if name in ("play", "choose", "map_select", "use_potion", "rest", "smith", "shop_buy"):
                summaries.append(f"{name}({','.join(f'{k}={v}' for k, v in args.items())})")
            else:
                summaries.append(name)
        lines.append("actions: " + ", ".join(summaries))
    lines.append(f"fingerprint={state.get('fingerprint')}")
    return "\n".join(lines)


def _print_lookup_entry(domain, entry, key, extra=None):
    """Human-readable lookup output; --json uses the raw entry instead."""
    print(f"key={entry.get('id') or key} kind={entry.get('kind') or domain} domain={domain}")
    if entry.get("name"):
        print(f"name={entry['name']}")
    if entry.get("description"):
        print(f"description: {entry['description']}")
    if entry.get("effect"):
        print(f"effect: {entry['effect']}")
    for field in (
        "cost", "card_type", "rarity", "target_type", "character_pool", "upgrade",
        "power_type", "stack_type", "counter_class", "host_of_affliction",
        "hp", "acts", "is_boss", "is_elite", "cycle", "passives",
        "base_damage", "hits", "status_card", "status_count",
        "label_semantics", "state_fields", "decision_rule", "member_classes",
        "intent_type", "follow_up_id", "display_note", "event_id", "title",
        "gates", "option_summary", "usage", "character", "aliases",
    ):
        if field in entry and entry[field] not in (None, "", [], {}):
            print(f"{field}: {json.dumps(entry[field], ensure_ascii=False)}")
    if entry.get("play_notes"):
        print(f"play_notes: {entry['play_notes']}")
    if entry.get("source"):
        print(f"source: {entry['source']}")
    if entry.get("needs_zh"):
        print("needs_zh: true (Chinese description pending curation)")
    if entry.get("curated") is False:
        print("curated: false (auto-folded — refine before relying on it)")
    if extra:
        print(extra)


def cmd_lookup(args):
    """Resolve a live game id to its complete reference JSON entry.

    Miss path (per user directive 2026-09-18): fall back to spire-codex.com
    research — fetch candidate pages, fold a minimal entry into the matching
    references/game/*.json + _zh.json pair (curated:false), and return it.
    When codex has no page either, exit 1 with a loud web-research trigger
    (agent doctrine: perplexity-search → fold into JSON EN+ZH → re-run).
    """
    key = args.key
    lang = args.lang or os.environ.get("SPIREBRIDGE_REF_LANG", "en")
    matches = lookup_reference(key, lang=lang, domain=args.domain, match_all=args.all)
    if matches:
        domains = []
        for domain, entry in matches:
            domains.append(domain)
            if args.json:
                print(json.dumps(entry, ensure_ascii=False, indent=2))
            else:
                _print_lookup_entry(domain, entry, key)
                print("---")
        if not args.all and len(matches) == 1 and len(domains) == 1:
            return 0
        others = [d for d in domains]
        if others:
            print(f"(domains matched: {', '.join(others)} — use --all for every entry)")
        return 0

    # ---- miss: research fallback ----
    print(
        f"lookup: no entry for '{key}' in references/game/*.json — "
        "attempting spire-codex.com research fallback",
        file=sys.stderr,
    )
    domain_guess = None
    if args.domain:
        domain_guess = args.domain
    elif key.endswith("_MOVE") or "_MOVE_" in key:
        domain_guess = "move"
    elif key.endswith("_POWER"):
        domain_guess = "power"
    elif key.endswith("_POTION"):
        domain_guess = "potion"
    elif ".pages." in key:
        domain_guess = "event_option"
    elif key.endswith("_CURSE"):
        domain_guess = "affliction"
    entry, url = research_and_fold(key, domain_guess=domain_guess)
    if entry:
        print(f"lookup: researched via {url} — folded into references/game (curated:false, needs_zh:true)")
        if args.json:
            print(json.dumps(entry, ensure_ascii=False, indent=2))
        else:
            _print_lookup_entry(domain_guess or entry.get("kind"), entry, key, extra=f"folded_from: {url}")
        print(
            "next: refine the entry (and its _zh.json twin) with perplexity-search/"
            "decomp facts, set curated:true, then re-run "
            "scripts/build_game_reference_json.py --check",
            file=sys.stderr,
        )
        return 0
    candidates = ", ".join(codex_candidate_urls(key))
    print(
        f"lookup: MISS — '{key}' not in references/game/*.json and no spire-codex.com page matched.\n"
        f"  codex candidates tried: {candidates}\n"
        f"  next: research '{key}' via perplexity-search (or spire-codex.com browser search),\n"
        f"  fold the result into the matching <domain>.json + <domain>_zh.json (key='{key}',\n"
        f"  curated:true), then re-run build_game_reference_json.py --check. "
        "A lookup miss is a research trigger — never permission to guess.",
        file=sys.stderr,
    )
    return 1


def cmd_doctor(args):
    """Check mod install, game process, bridge handshake, and log-dir status.

    Args:
        args: Parsed CLI args (host/port).

    Returns:
        Process exit code (0 when all checks pass).
    """
    ok = True
    print("== spirectl doctor ==")
    env_dir = os.environ.get("SPIREBRIDGE_LOG_DIR")
    print(f"[0] run log dir: {RUNLOG_DIR or 'UNSET'} | SPIREBRIDGE_LOG_DIR={env_dir or 'unset — required, no fallback'}")
    mod_dir = GAME_MODS_DIR / MOD_ID
    dll = mod_dir / f"{MOD_ID}.dll"
    manifest = mod_dir / f"{MOD_ID}.json"
    print(f"[1] mod files: {'OK' if dll.exists() and manifest.exists() else 'MISSING'} ({mod_dir})")
    if not dll.exists() or not manifest.exists():
        ok = False
        print("     fix: run scripts/install-mod.sh")
    proc = subprocess.run(["pgrep", "-f", "Slay the Spire 2"], capture_output=True, text=True)
    game_running = bool(proc.stdout.strip())
    print(f"[2] game process: {'running pid=' + proc.stdout.strip().splitlines()[0] if game_running else 'not running'}")
    if game_running and GAME_LOG.exists():
        log = GAME_LOG.read_text(errors="ignore")
        mentions = MOD_ID in log
        listening = "listening on 127.0.0.1" in log
        print(f"[3] game log: mod mentioned={'yes' if mentions else 'no'} listening={'yes' if listening else 'no'} ({GAME_LOG})")
        if mentions and not listening:
            print("     hint: accept the mod-loading warning in game, then restart once")
    try:
        with BridgeClient(host=args.host, port=args.port) as client:
            hello = client.hello()
            if hello.get("type") != "hello_ok":
                print(f"[4] bridge handshake: NOT READY ({hello.get('message') or hello})")
                print("     hint: mod still initializing; retry in a few seconds")
                ok = False
            else:
                print(
                    f"[4] bridge handshake: OK protocol={hello.get('protocol_version')} "
                    f"game={hello.get('game_version')} mod={hello.get('mod_version')} "
                    f"assembly_hash={hello.get('assembly_hash')} speed={hello.get('speed', 'n/a')}"
                )
                state = client.state()
                if state.get("type") == "error":
                    print(f"[5] state read: NOT READY ({state.get('message')})")
                    ok = False
                else:
                    print(f"[5] state read: OK screen={state.get('screen')} fingerprint={state.get('fingerprint')}")
    except (ConnectionError, OSError, json.JSONDecodeError) as exc:
        print(f"[4] bridge handshake: FAILED ({exc})")
        if not game_running:
            print("     fix: launch the game (spirectl launch) and accept the mod warning once")
        else:
            print(f"     fix: check that port {args.port} is free and the mod is enabled in game settings")
        ok = False
    print("doctor:", "OK" if ok else "FAILED")
    return 0 if ok else 1


def cmd_state(args):
    """Read and print the current game state; logs the snapshot.

    Args:
        args: Parsed CLI args; args.json prints full JSON.

    Returns:
        Process exit code (0 ok, 1 game over detected).
    """
    with BridgeClient(host=args.host, port=args.port) as client:
        state = client.state()
        metrics = dict(client.last_metrics)
    log_run_event("state", {"state": state, "metrics": metrics})
    if state.get("screen") == "game_over" or (state.get("run") or {}).get("is_game_over"):
        log_run_event("run_end", {"state": state}, finalize=True)
    print(f"[{metrics_line(metrics)}]")
    if args.json:
        print(json.dumps(state, indent=2, ensure_ascii=False))
    else:
        print(render_compact(state))
    return 0


def _wait_mode_for(action, explicit):
    """Pick the settle wait mode for an action.

    Args:
        action: Action name being executed.
        explicit: Caller override ("settle" or "play"), or None.

    Returns:
        "play" for end_turn (or explicit "play"), otherwise "settle".
    """
    if explicit in ("settle", "play"):
        return explicit
    if action == "end_turn":
        return "play"
    return "settle"


def cmd_act(args):
    if _info_stop_flag_exists():
        print("[INFO-INCOMPLETE] act refused: stop flag set — server info was incomplete earlier", file=sys.stderr)
        print(f"  clear with: rm {INFO_STOP_FLAG}", file=sys.stderr)
        sys.exit(INFO_STOP_EXIT)
    """Submit one action and optionally wait for settle/play.

    Args:
        args: Parsed CLI args (action, args, wait/wait-play/wait-mode,
            wait-timeout, stall-timeout, json).

    Returns:
        Process exit code: 0 ok, 1 failed act, 3 stall.
    """
    act_args = json.loads(args.args) if args.args else None
    wait_mode = None
    if args.wait or args.wait_play or args.wait_mode:
        wait_mode = _wait_mode_for(args.action, args.wait_mode or ("play" if args.wait_play else "settle"))
    with BridgeClient(host=args.host, port=args.port) as client:
        t0 = time.perf_counter()
        result = client.act(args.action, act_args)
        metrics = dict(client.last_metrics)
        act_rtt_ms = metrics.get("rtt_ms") or 0
        settle_ms = 0
        stalled = False
        state = result.get("state")
        if wait_mode:
            state, settle_ms, stalled = wait_for_settle(
                client,
                mode=wait_mode,
                stall_s=args.stall_timeout,
            )
            if state is not None:
                result["state"] = state
        total_ms = int((time.perf_counter() - t0) * 1000)
        del act_rtt_ms  # folded into metrics below
    rotate = args.action in ("start_run", "continue_run")
    log_run_event(
        "act",
        {
            "action": args.action,
            "args": act_args,
            "result": result,
            "metrics": {**metrics, "settle_ms": settle_ms, "stalled": stalled, "total_ms": total_ms},
            "wait_mode": wait_mode,
        },
        rotate=rotate,
    )
    if (result.get("state") or {}).get("screen") == "game_over":
        log_run_event("run_end", {"last_action": args.action, "state": result.get("state")}, finalize=True)
    settle_note = f" settle={settle_ms}ms mode={wait_mode}" if wait_mode else ""
    stall_note = " STALL" if stalled else ""
    print(f"ok={result.get('ok')} message={result.get('message')} [{metrics_line(metrics)}{settle_note}{stall_note}]")
    state = result.get("state")
    if state:
        if args.json:
            print(json.dumps(state, indent=2, ensure_ascii=False))
        else:
            print(render_compact(state))
    if stalled:
        return 3
    return 0 if result.get("ok") else 1


def cmd_batch(args):
    if _info_stop_flag_exists():
        print("[INFO-INCOMPLETE] act refused: stop flag set — server info was incomplete earlier", file=sys.stderr)
        print(f"  clear with: rm {INFO_STOP_FLAG}", file=sys.stderr)
        sys.exit(INFO_STOP_EXIT)
    """Run a JSON list of acts sequentially, settling between each.

    Hand-index arithmetic across plays belongs to the caller: prefer
    high-to-low card_index so earlier plays do not invalidate later ones.

    Args:
        args: Parsed CLI args; args.acts is a JSON array of
            {"action", "args"} objects.

    Returns:
        Process exit code: 0 ok, 1 failed act, 2 bad input, 3 stall, 4 game_over.
    """
    acts = json.loads(args.acts)
    if not isinstance(acts, list) or not acts:
        print("batch requires a non-empty JSON array of {action,args?}", file=sys.stderr)
        return 2
    with BridgeClient(host=args.host, port=args.port) as client:
        state = client.state()
        print(f"batch start [{metrics_line(client.last_metrics)}]")
        print(render_compact(state) if not args.json else json.dumps(state, indent=2, ensure_ascii=False))
        for i, item in enumerate(acts):
            action = item.get("action")
            act_args = item.get("args")
            if not action:
                print(f"batch[{i}] missing action — abort", file=sys.stderr)
                return 2
            result = client.act(action, act_args)
            metrics = dict(client.last_metrics)
            log_run_event("act", {"action": action, "args": act_args, "result": result, "metrics": metrics, "batch": i})
            ok = bool(result.get("ok"))
            print(f"batch[{i}] {action} ok={ok} {result.get('message')} [{metrics_line(metrics)}]")
            if not ok:
                state = client.state()
                print("batch aborted on failed act")
                print(render_compact(state) if not args.json else json.dumps(state, indent=2, ensure_ascii=False))
                return 1
            is_last = i == len(acts) - 1
            if is_last and not args.wait_final:
                state = result.get("state") or client.state()
                print(render_compact(state) if not args.json else json.dumps(state, indent=2, ensure_ascii=False))
                break
            mode = "settle"
            if is_last and args.wait_final:
                mode = _wait_mode_for(action, None)
            state, settle_ms, stalled = wait_for_settle(
                client,
                mode=mode,
                stall_s=args.stall_timeout,
            )
            print(f"  settled {settle_ms}ms mode={mode}{' STALL' if stalled else ''}")
            print(render_compact(state) if not args.json else json.dumps(state, indent=2, ensure_ascii=False))
            log_run_event(
                "wait_change" if not stalled else "wait_stall",
                {"state": state, "metrics": {"settle_ms": settle_ms, "stalled": stalled}, "batch": i, "mode": mode},
            )
            if stalled:
                return 3
            if (state or {}).get("screen") == "game_over":
                log_run_event("run_end", {"last_action": action, "state": state}, finalize=True)
                print("batch: game_over reached")
                return 0
    return 0


def _load_run_events(path=None):
    """Load JSON events from a run log.

    Args:
        path: Explicit log file; None uses the current run pointer.

    Returns:
        Tuple (path, events); events is empty when nothing could be loaded.
    """
    if path:
        target = Path(path)
    else:
        log_dir, pointer_path = _require_log_dir()
        pointer = pointer_path.read_text(encoding="utf-8").strip() if pointer_path.exists() else ""
        if not pointer:
            return None, []
        target = log_dir / pointer
    if not target.exists():
        return target, []
    events = []
    with target.open(encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return target, events


def _percentile(values, p):
    """Return the p-quantile (0..1) of values, or None when empty."""
    if not values:
        return None
    ordered = sorted(values)
    idx = min(len(ordered) - 1, int(len(ordered) * p))
    return ordered[idx]


def cmd_profile(args):
    """Summarize timing in a run log: bridge RTT, game settle, client gaps.

    Args:
        args: Parsed CLI args; args.log selects a run-log path
            (default: current run), args.budget is the target minutes per run.

    Returns:
        Process exit code (0 on success, 1 when the log has no events).
    """
    path, events = _load_run_events(args.log)
    if not events:
        print(f"no run log events ({path})")
        return 1
    print(f"== profile {path} ==")
    t0, tN = events[0]["ts"], events[-1]["ts"]
    print(f"events={len(events)} span {t0} -> {tN}")

    def parse(ts):
        """Parse a run-log timestamp string into datetime."""
        return datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")

    span_s = (parse(tN) - parse(t0)).total_seconds()
    acts = [e for e in events if e["kind"] == "act"]
    run_ends = [e for e in events if e["kind"] == "run_end"]

    rtt, server, queue, settle, connect, total = [], [], [], [], [], []
    for e in events:
        m = e.get("metrics") or {}
        if m.get("rtt_ms") is not None:
            rtt.append(m["rtt_ms"])
        if m.get("server_ms") is not None:
            server.append(m["server_ms"])
        if m.get("queue_ms") is not None:
            queue.append(m["queue_ms"])
        if m.get("settle_ms") is not None:
            settle.append(m["settle_ms"])
        if m.get("connect_ms"):
            connect.append(m["connect_ms"])
        if m.get("total_ms") is not None:
            total.append(m["total_ms"])

    def block(name, vals, unit="ms"):
        """Print one timing block: n/p50/p90/p99/max/avg."""
        if not vals:
            print(f"  {name}: n/a (no instrumentation in this log)")
            return
        print(
            f"  {name}: n={len(vals)} p50={_percentile(vals, 0.5)}{unit} "
            f"p90={_percentile(vals, 0.9)}{unit} p99={_percentile(vals, 0.99)}{unit} "
            f"max={max(vals)}{unit} avg={sum(vals) // len(vals)}{unit}"
        )

    print("bridge instrumentation:")
    block("act/state rtt", rtt)
    block("server handle", server)
    block("dispatch queue", queue)
    block("tcp connect", connect)
    block("game settle (wait)", settle)
    block("command total", total)

    # Client-side gaps from timestamps (works on old logs too).
    gaps = []
    for a, b in zip(events, events[1:]):
        delta = (parse(b["ts"]) - parse(a["ts"])).total_seconds()
        gaps.append((delta, a, b))
    act_gaps = [(d, a, b) for d, a, b in gaps if b.get("kind") == "act"]
    after_end_turn = [
        d for d, a, _b in gaps
        if a.get("kind") == "act" and (a.get("action") == "end_turn" or (a.get("result") or {}).get("action") == "end_turn")
    ]
    print("wall-clock gaps (timestamp deltas between client calls):")
    all_d = [d for d, *_ in gaps]
    if all_d:
        print(
            f"  all gaps: n={len(all_d)} p50={_percentile(all_d, 0.5):.0f}s "
            f"p90={_percentile(all_d, 0.9):.0f}s max={max(all_d):.0f}s sum={sum(all_d):.0f}s"
        )
    if act_gaps:
        ad = [d for d, *_ in act_gaps]
        print(
            f"  gaps before act: n={len(ad)} p50={_percentile(ad, 0.5):.0f}s "
            f"p90={_percentile(ad, 0.9):.0f}s max={max(ad):.0f}s"
        )
    if after_end_turn:
        print(
            f"  after end_turn: n={len(after_end_turn)} p50={_percentile(after_end_turn, 0.5):.0f}s "
            f"p90={_percentile(after_end_turn, 0.9):.0f}s max={max(after_end_turn):.0f}s "
            f"sum={sum(after_end_turn):.0f}s"
        )

    # Decomposition when settle instrumentation exists.
    if settle and act_gaps:
        # Approximate client decision time = gap before act - previous settle - previous rtt
        decisions = []
        prev_settle = 0.0
        prev_rtt = 0.0
        for d, a, b in act_gaps:
            client_est = d - prev_settle / 1000.0 - prev_rtt / 1000.0
            if client_est >= 0:
                decisions.append(client_est)
            m = (a.get("metrics") or {})
            # a is the previous event; its settle applies to the gap we just measured
            if m.get("settle_ms") is not None:
                prev_settle = m["settle_ms"]
            if m.get("rtt_ms") is not None:
                prev_rtt = m["rtt_ms"]
        if decisions:
            print("estimated client decision time (gap - game settle - bridge rtt):")
            print(
                f"  decisions: n={len(decisions)} p50={_percentile(decisions, 0.5):.1f}s "
                f"p90={_percentile(decisions, 0.9):.1f}s max={max(decisions):.1f}s "
                f"sum={sum(decisions):.0f}s"
            )

    if acts:
        print(f"acts={len(acts)} run_span={span_s:.0f}s avg_act_cadence={span_s / max(1, len(acts)):.1f}s")
    if run_ends:
        print(f"run_end events: {len(run_ends)}")
    stalls = [e for e in events if (e.get("metrics") or {}).get("stalled")]
    print(f"stalls flagged: {len(stalls)}")
    budget = args.budget * 60
    if span_s > budget:
        print(f"BUDGET OVER: span {span_s:.0f}s > {args.budget}min ({budget:.0f}s) by {span_s - budget:.0f}s")
    else:
        print(f"budget ok: span {span_s:.0f}s <= {args.budget}min")
    return 0


def cmd_wait(args):
    """Poll for a state fingerprint change; return quickly when idle.

    Change-polling model (user directive 2026-09-16 — no timeout deadlines):
    return as soon as the fingerprint changes. If it stays unchanged for
    --quiet seconds, return the current state immediately with a "no change"
    note so the caller can decide — never block for minutes on an idle game.

    Args:
        args: Parsed CLI args (quiet, interval, json).

    Returns:
        Process exit code: 0 once a state snapshot is returned (changed or
        quiet), 1 on poll failure.
    """
    with BridgeClient(host=args.host, port=args.port) as client:
        state = client.state()
        prev = state.get("fingerprint")
        unchanged_since = time.perf_counter()
        print(f"polling (initial fingerprint={prev})")
        while True:
            time.sleep(args.interval)
            try:
                state = client.state()
                metrics = dict(client.last_metrics)
            except (ConnectionError, OSError, json.JSONDecodeError) as exc:
                print(f"poll failed: {exc}")
                return 1
            fp = state.get("fingerprint")
            now = time.perf_counter()
            if fp != prev:
                print(f"changed -> fingerprint={fp} screen={state.get('screen')} [{metrics_line(metrics)}]")
                log_run_event("wait_change", {"state": state, "metrics": metrics})
                print(render_compact(state) if not args.json else json.dumps(state, indent=2, ensure_ascii=False))
                return 0
            if now - unchanged_since >= args.quiet:
                quiet_s = now - unchanged_since
                print(
                    f"no change after {quiet_s:.1f}s — returning current state "
                    f"(screen={state.get('screen')}, fingerprint={fp})"
                )
                log_run_event("wait_no_change", {"state": state, "metrics": metrics, "quiet_s": quiet_s})
                print(render_compact(state) if not args.json else json.dumps(state, indent=2, ensure_ascii=False))
                return 0


def steam_fully_ready():
    """Return True when the Steam client and a helper process are running."""
    main = subprocess.run(["pgrep", "-f", "Steam.AppBundle/Steam/Contents/MacOS/steam_osx"],
                          capture_output=True).returncode == 0
    main = main or subprocess.run(["pgrep", "-x", "Steam"], capture_output=True).returncode == 0
    if not main:
        return False
    # UI helpers: newer builds use steamwebhelper; macOS bundle uses Steam Helper
    helper = subprocess.run(["pgrep", "-f", "steamwebhelper"], capture_output=True).returncode == 0
    helper = helper or subprocess.run(["pgrep", "-f", "Steam Helper"],
                                      capture_output=True).returncode == 0
    return helper


def focus_game_window():
    """Move the game window onto this session's terminal display (cosmetic).

    User preference 2026-09-18: the game must pop up on the screen of the
    Claude Code session that launched it, not on the work display. Delegates
    to scripts/focus-game-window.sh (AppleScript, windowed-mode game).
    Never raises — a failed window move must not block launch recovery.
    """
    script = REPO_ROOT / "scripts" / "focus-game-window.sh"
    if not script.exists():
        return
    try:
        result = subprocess.run(
            ["bash", str(script)], capture_output=True, text=True, timeout=25
        )
        msg = (result.stdout or "").strip()
        if msg:
            print(msg)
        err = (result.stderr or "").strip()
        if result.returncode != 0 and err:
            print(f"focus-game-window: {err}")
    except (subprocess.TimeoutExpired, OSError) as exc:
        print(f"focus-game-window: skipped ({exc})")


def cmd_launch(args):
    """Launch the game via Steam and wait for the bridge handshake.

    Starts Steam if needed, opens the steam:// run URL, then polls hello
    until the mod bridge answers or the timeout expires.

    Args:
        args: Parsed CLI args (host, port, timeout).

    Returns:
        Process exit code: 0 when the bridge answers, 1 otherwise.
    """
    suppress_crash_dialogs()
    if not steam_fully_ready():
        if not steam_fully_ready():
            print("Steam not ready; starting Steam and waiting for client boot")
            if subprocess.run(["pgrep", "-x", "Steam"], capture_output=True).returncode != 0:
                subprocess.run(["open", "-a", "Steam"], check=False)
        if not wait_for(steam_fully_ready, 60, interval=2.0):
            print("Steam client did not become ready; start Steam manually, then re-run launch")
            return 1
        time.sleep(5)  # extra settle time before issuing a rungameid URL
    if not game_process_running():
        url = f"steam://rungameid/{STEAM_APP_ID}"
        print(f"launching via {url} (Steam ready)")
        subprocess.run(["open", url], check=False)
        if not wait_for(game_process_running, 45, interval=2.0):
            print("game did not start from Steam URL; retrying once after settle")
            time.sleep(5)
            subprocess.run(["open", url], check=False)
            wait_for(game_process_running, 45, interval=2.0)
    if not game_process_running():
        print("game process did not start; launch it from the Steam client manually")
        return 1
    print("game process up; waiting for bridge")
    deadline = time.time() + args.timeout
    while time.time() < deadline:
        time.sleep(2)
        try:
            with BridgeClient(host=args.host, port=args.port) as client:
                hello = client.hello()
                if hello.get("type") != "hello_ok":
                    continue
                print(f"bridge up: game={hello.get('game_version')} mod={hello.get('mod_version')}")
                focus_game_window()
                return 0
        except (ConnectionError, OSError, json.JSONDecodeError):
            continue
    print("bridge did not come up in time; run spirectl doctor for details")
    return 1


def cmd_sl(args):
    if _info_stop_flag_exists():
        print("[INFO-INCOMPLETE] act refused: stop flag set — server info was incomplete earlier", file=sys.stderr)
        print(f"  clear with: rm {INFO_STOP_FLAG}", file=sys.stderr)
        sys.exit(INFO_STOP_EXIT)
    """Reload the current room: stop the game, relaunch, continue_run.

    The room-entry save replays combat with the same seed, so intents and
    draw order observed on the previous attempt stay valid.

    Args:
        args: Parsed CLI args (json, menu_timeout, stall_timeout).

    Returns:
        Process exit code: 0 ok, 2 launch failure, 3 reload stalled.
    """
    t0 = time.perf_counter()
    print("[sl] stopping game")
    cmd_stop(args)
    t_stop = time.perf_counter()
    print("[sl] launching")
    launch_args = argparse.Namespace(host=args.host, port=args.port, timeout=120.0)
    if cmd_launch(launch_args) != 0:
        print("[sl] launch failed", file=sys.stderr)
        return 2
    t_launch = time.perf_counter()
    # Launch returns on bridge handshake; logo may still be playing.
    print("[sl] waiting for main menu")
    with BridgeClient(host=args.host, port=args.port) as client:
        deadline = time.time() + args.menu_timeout
        state = client.state()
        while time.time() < deadline and state.get("screen") not in ("menu", "map", "combat"):
            time.sleep(0.4)
            state = client.state()
        print(f"[sl] screen={state.get('screen')} type={state.get('screen_type')}")
        if state.get("screen") != "menu":
            if state.get("screen") in ("map", "combat"):
                print("[sl] run still active — no reload needed")
                print(render_compact(state))
                return 0
        print("[sl] continue_run")
        result = client.act("continue_run")
        log_run_event("act", {"action": "continue_run", "args": {"via": "sl"}, "result": result}, rotate=True)
        print(f"ok={result.get('ok')} {result.get('message')}")
        state, settle_ms, stalled = wait_for_settle(client, mode="settle", stall_s=args.stall_timeout)
        t_end = time.perf_counter()
        log_run_event(
            "sl_reload",
            {
                "state": state,
                "timings_ms": {
                    "stop": int((t_stop - t0) * 1000),
                    "launch": int((t_launch - t_stop) * 1000),
                    "continue_settle": settle_ms,
                    "total": int((t_end - t0) * 1000),
                },
            },
        )
        print(f"[sl] total={int((t_end - t0) * 1000)}ms stop={int((t_stop - t0) * 1000)}ms "
              f"launch={int((t_launch - t_stop) * 1000)}ms settle={settle_ms}ms"
              f"{' STALL' if stalled else ''}")
        print(render_compact(state) if not args.json else json.dumps(state, indent=2, ensure_ascii=False))
        return 3 if stalled else 0
    return 0


def main(argv=None):
    """Parse CLI arguments and dispatch to the subcommand handler.

    Args:
        argv: Argument list; None uses sys.argv[1:].

    Returns:
        Exit code from the selected subcommand.
    """
    parser = argparse.ArgumentParser(prog="spirectl", description=__doc__)
    parser.add_argument("--host", default=os.environ.get("SPIREBRIDGE_HOST", DEFAULT_HOST))
    parser.add_argument("--port", type=int, default=int(os.environ.get("SPIREBRIDGE_PORT", DEFAULT_PORT)))
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("doctor", help="check mod install, game process, bridge handshake")

    p_watchdog = sub.add_parser(
        "watchdog",
        help="arm/disarm/status the external liveness watchdog",
    )
    p_watchdog.add_argument("watchdog_cmd", choices=("enable", "disable", "status"))

    p_state = sub.add_parser("state", help="read current game state")
    p_state.add_argument("--json", action="store_true", help="print full JSON instead of compact text")
    p_state.add_argument("--no-ref-tags", action="store_true",
                         help="disable compact auto-lookup snippets from references/game JSON")

    p_act = sub.add_parser("act", help="send one action to the game")
    p_act.add_argument("action", help="action name, e.g. play / end_turn / choose / map_select")
    p_act.add_argument("--args", help="action args as JSON object, e.g. '{\"card_index\":0}'")
    p_act.add_argument("--json", action="store_true", help="print returned state as JSON")
    p_act.add_argument("--wait", action="store_true",
                       help="after act, poll until state settles (stable fingerprint) then print it")
    p_act.add_argument("--wait-play", action="store_true",
                       help="after act, poll until player Play phase resumes (or non-combat screen)")
    p_act.add_argument("--wait-mode", choices=("settle", "play"), help="explicit wait mode override")
    p_act.add_argument("--stall-timeout", type=float, default=3.0,
                       help="declare STALL and return if the fingerprint freezes this long "
                            "(polling continues while state keeps changing — no deadline)")
    p_act.add_argument("--no-ref-tags", action="store_true",
                       help="disable compact auto-lookup snippets from references/game JSON")

    p_batch = sub.add_parser("batch", help="run a JSON array of acts sequentially with settle between")
    p_batch.add_argument("--acts", required=True,
                         help='JSON array e.g. \'[{"action":"play","args":{"card_index":2}},{"action":"end_turn"}]\'')
    p_batch.add_argument("--json", action="store_true")
    p_batch.add_argument("--wait-final", dest="wait_final", action="store_true", default=True,
                         help="wait for settle/play after the last act (default on)")
    p_batch.add_argument("--no-wait-final", dest="wait_final", action="store_false")
    p_batch.add_argument("--stall-timeout", type=float, default=3.0,
                         help="declare STALL and abort the batch if the fingerprint freezes this long")
    p_batch.add_argument("--no-ref-tags", action="store_true",
                         help="disable compact auto-lookup snippets from references/game JSON")

    p_wait = sub.add_parser("wait", help="poll for a state fingerprint change; returns quickly when idle")
    p_wait.add_argument("--quiet", type=float, default=3.0,
                        help="return current state after this many seconds without a fingerprint change")
    p_wait.add_argument("--interval", type=float, default=0.2)
    p_wait.add_argument("--json", action="store_true")
    p_wait.add_argument("--no-ref-tags", action="store_true",
                        help="disable compact auto-lookup snippets from references/game JSON")

    p_profile = sub.add_parser("profile", help="summarize run-log timing: rtt/settle/client gaps")
    p_profile.add_argument("--log", help="run log path (default: current run)")
    p_profile.add_argument("--budget", type=float, default=30.0, help="target minutes per run")

    p_launch = sub.add_parser("launch", help="launch the game via Steam and wait for the bridge")
    p_launch.add_argument("--timeout", type=float, default=120.0,
                          help="lifecycle cap for game boot + bridge handshake (not a play-loop wait)")

    p_sl = sub.add_parser("sl", help="save/load reload: stop -> launch -> continue_run (room-entry save)")
    p_sl.add_argument("--json", action="store_true")
    p_sl.add_argument("--menu-timeout", type=float, default=45.0)
    p_sl.add_argument("--stall-timeout", type=float, default=3.0)

    p_lookup = sub.add_parser(
        "lookup",
        help="resolve a live game id to its complete reference JSON entry "
             "(miss path researches spire-codex.com and folds findings into the JSON DB)",
    )
    p_lookup.add_argument("key", help="live game id, e.g. GLOMP_MOVE / RAVENOUS_POWER / BURNING_BLOOD / NEOW.pages.INITIAL.options.NEOWS_TALISMAN")
    p_lookup.add_argument("--json", action="store_true", help="print the raw JSON entry")
    p_lookup.add_argument("--lang", choices=("en", "zh"),
                          default=os.environ.get("SPIREBRIDGE_REF_LANG", "en"))
    p_lookup.add_argument("--domain",
                          help="restrict search: move|power|relic|card|potion|event|affliction|intent|character|monster")
    p_lookup.add_argument("--all", action="store_true", help="print every domain match")

    sub.add_parser("stop", help="gracefully stop the game (quiet quit -> TERM -> KILL)")

    args = parser.parse_args(argv)
    # Compact ref-tag opt-out: one env switch honored by render_compact.
    if getattr(args, "no_ref_tags", False):
        os.environ["SPIREBRIDGE_REF_TAGS"] = "0"
    handlers = {
        "doctor": cmd_doctor,
        "watchdog": cmd_watchdog,
        "state": cmd_state,
        "act": cmd_act,
        "batch": cmd_batch,
        "wait": cmd_wait,
        "profile": cmd_profile,
        "launch": cmd_launch,
        "sl": cmd_sl,
        "stop": cmd_stop,
        "lookup": cmd_lookup,
    }
    try:
        return handlers[args.cmd](args)
    except (ConnectionError, OSError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
