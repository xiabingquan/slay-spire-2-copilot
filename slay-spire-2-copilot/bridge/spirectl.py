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


def render_compact(state):
    """Render a bridge state snapshot as compact human-readable lines.

    Args:
        state: Bridge state snapshot dict.

    Returns:
        Multi-line string summarizing screen, run, player, combat, options.
    """
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
        if run.get("map_coord"):
            c = run["map_coord"]
            parts.append(f"pos=({c.get('row')},{c.get('col')})")
    lines.append(" | ".join(parts))
    # Act-start boon rooms (Ancient/Neow-family, e.g. 先古移民 HP restore) are
    # easy to skip: the game lands on the row-1 map and available_map_points
    # historically omitted the start room. Surface it loudly while unvisited.
    start_room = run.get("act_start_room") or {}
    if start_room and not start_room.get("visited") and start_room.get("is_boon_room"):
        lines.append(
            f"ACT-START BOON ROOM UNVISITED: ({start_room.get('row')},{start_room.get('col')})"
            f"={start_room.get('point_type')} — map_select it BEFORE any row-1+ point"
        )
    if player:
        gold = player.get("gold")
        gold_s = f" gold={gold}" if gold is not None else ""
        lines.append(f"player hp={player.get('hp')}/{player.get('max_hp')} block={player.get('block')}{gold_s}")
        # player powers/debuffs mirror creature powers during combat
        combat_p = state.get("combat") or {}
        me = next((c for c in (combat_p.get("creatures") or []) if c.get("is_player")), None)
        if me and me.get("powers"):
            lines.append("player powers: " + ", ".join(p.get("id", "?") for p in me["powers"]))
        relics = player.get("relics") or []
        if relics:
            lines.append("relics: " + ", ".join(r.get("id", "?") for r in relics))
        potions = [p for p in (player.get("potions") or []) if p]
        if potions:
            lines.append("potions: " + ", ".join(f"[{p['index']}]{p.get('id')}" for p in potions))
    if combat:
        lines.append(
            f"combat round={combat.get('round')} side={combat.get('current_side')} "
            f"phase={combat.get('turn_phase')} energy={combat.get('energy')}/{combat.get('max_energy')}"
        )
        for c in combat.get("creatures") or []:
            mark = "*" if c.get("is_player") else "-"
            line = (
                f" {mark} id{c.get('combat_id')} {c.get('name')} "
                f"hp={c.get('hp')}/{c.get('max_hp')} block={c.get('block')}"
            )
            powers = c.get("powers") or []
            if powers:
                line += " powers=[" + ",".join(p.get("id", "?") for p in powers) + "]"
            intents = c.get("intents") or []
            if intents:
                move = c.get("move_id")
                bits = []
                for it in intents:
                    label = strip_bbcode(it.get("label") or it.get("type"))
                    dmg = it.get("damage")
                    hits = it.get("hits")
                    desc = label or it.get("class")
                    # Loc leaks like intents:FORMAT_EMPTY carry no decision
                    # value — fall back to intent class/type + the monster's
                    # current move id so the intent is still readable.
                    if not desc or "FORMAT_EMPTY" in str(desc):
                        desc = it.get("type") or it.get("class") or "unknown"
                        if move:
                            desc = f"{desc}({move})"
                    if dmg is not None:
                        desc = f"{desc} dmg={dmg}"
                    if hits is not None:
                        desc = f"{desc}x{hits}"
                    bits.append(str(desc))
                line += " intent=" + "; ".join(bits)
            lines.append(line)
        piles = combat.get("piles") or {}
        lines.append(
            f"piles draw={piles.get('draw_count')} discard={piles.get('discard_count')} "
            f"exhaust={piles.get('exhaust_count')}"
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
            lines.append(f" [{opt.get('index')}] {opt.get('kind')}:{opt.get('id')} {opt.get('name') or ''}")
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
                return 0
        except (ConnectionError, OSError, json.JSONDecodeError):
            continue
    print("bridge did not come up in time; run spirectl doctor for details")
    return 1


def cmd_sl(args):
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

    p_batch = sub.add_parser("batch", help="run a JSON array of acts sequentially with settle between")
    p_batch.add_argument("--acts", required=True,
                         help='JSON array e.g. \'[{"action":"play","args":{"card_index":2}},{"action":"end_turn"}]\'')
    p_batch.add_argument("--json", action="store_true")
    p_batch.add_argument("--wait-final", dest="wait_final", action="store_true", default=True,
                         help="wait for settle/play after the last act (default on)")
    p_batch.add_argument("--no-wait-final", dest="wait_final", action="store_false")
    p_batch.add_argument("--stall-timeout", type=float, default=3.0,
                         help="declare STALL and abort the batch if the fingerprint freezes this long")

    p_wait = sub.add_parser("wait", help="poll for a state fingerprint change; returns quickly when idle")
    p_wait.add_argument("--quiet", type=float, default=3.0,
                        help="return current state after this many seconds without a fingerprint change")
    p_wait.add_argument("--interval", type=float, default=0.2)
    p_wait.add_argument("--json", action="store_true")

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

    sub.add_parser("stop", help="gracefully stop the game (quiet quit -> TERM -> KILL)")

    args = parser.parse_args(argv)
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
    }
    try:
        return handlers[args.cmd](args)
    except (ConnectionError, OSError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
