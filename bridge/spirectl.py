#!/usr/bin/env python3
# spirectl: CLI bridging a Claude Code session to the SpireBridge STS2 mod.
"""spirectl — talk to the mimo-spire-bridge mod inside Slay the Spire 2."""

import argparse
import json
import os
import re
import socket
import subprocess
import sys
import time
from pathlib import Path

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 17612
MOD_ID = "mimo-spire-bridge"
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
RUNLOG_DIR = REPO_ROOT / "logs"
RUNLOG_POINTER = RUNLOG_DIR / ".current_run"
STEAM_APP_ID = "2868840"
BBCODE_RE = re.compile(r"\[/?[^\]]+\]")


def strip_bbcode(text):
    return BBCODE_RE.sub("", text) if isinstance(text, str) else text


def _runlog_file(finalize=False):
    """One log file per run under logs/. Rotated on start/continue_run,
    finalized on game_over. Returns path of the active run log."""
    RUNLOG_DIR.mkdir(parents=True, exist_ok=True)
    current = None
    if RUNLOG_POINTER.exists():
        current = RUNLOG_POINTER.read_text(encoding="utf-8").strip() or None
        if finalize:
            return RUNLOG_DIR / current
        if current:
            return RUNLOG_DIR / current
    stamp = time.strftime("%Y%m%d-%H%M%S")
    current = f"run-{stamp}.log"
    RUNLOG_POINTER.write_text(current + "\n", encoding="utf-8")
    return RUNLOG_DIR / current


def log_run_event(kind, data, rotate=False, finalize=False):
    """Append a complete record (timestamp + kind + full JSON) to the run log."""
    if rotate and RUNLOG_POINTER.exists():
        RUNLOG_POINTER.unlink(missing_ok=True)
    path = _runlog_file(finalize=finalize)
    record = {"ts": time.strftime("%Y-%m-%d %H:%M:%S"), "kind": kind, **data}
    if finalize:
        record["outcome"] = data.get("outcome") or "game_over"
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")
    return path
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
    proc = subprocess.run(["pgrep", "-f", "Slay the Spire 2"], capture_output=True, text=True)
    return bool(proc.stdout.strip())


def suppress_crash_dialogs():
    """macOS shows 'app quit unexpectedly' after hard kills; silence the
    CrashReporter dialog so automated restarts stay quiet."""
    subprocess.run(
        ["defaults", "write", "com.apple.CrashReporter", "DialogType", "-string", "none"],
        capture_output=True,
    )


def cmd_stop(args):
    """Graceful game stop: AppleEvent quit -> SIGTERM -> SIGKILL."""
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
    deadline = time.time() + timeout
    while time.time() < deadline:
        if predicate():
            return True
        time.sleep(interval)
    return False


class BridgeClient:
    def __init__(self, host=DEFAULT_HOST, port=DEFAULT_PORT, timeout=12.0):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.sock = None
        self.rfile = None
        self.wfile = None

    def connect(self):
        self.sock = socket.create_connection((self.host, self.port), timeout=self.timeout)
        self.sock.settimeout(self.timeout)
        self.rfile = self.sock.makefile("r", encoding="utf-8")
        self.wfile = self.sock.makefile("w", encoding="utf-8")

    def close(self):
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
        if self.sock is None:
            self.connect()
        assert self.wfile is not None and self.rfile is not None
        self.wfile.write(json.dumps(payload) + "\n")
        self.wfile.flush()
        line = self.rfile.readline()
        if not line:
            raise ConnectionError("bridge closed the connection")
        return json.loads(line.lstrip("﻿"))

    def hello(self):
        return self.request({"type": "hello"})

    def state(self):
        return self.request({"type": "state"})

    def act(self, action, args=None):
        payload = {"type": "act", "action": action}
        if args:
            payload["args"] = args
        return self.request(payload)

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        del exc_type, exc_val, exc_tb
        self.close()


def render_compact(state):
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
                bits = []
                for it in intents:
                    label = strip_bbcode(it.get("label") or it.get("type"))
                    dmg = it.get("damage")
                    hits = it.get("hits")
                    desc = label or it.get("class")
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
    ok = True
    print("== spirectl doctor ==")
    mod_dir = GAME_MODS_DIR / MOD_ID
    dll = mod_dir / f"{MOD_ID}.dll"
    manifest = mod_dir / f"{MOD_ID}.json"
    print(f"[1] mod files: {'OK' if dll.exists() and manifest.exists() else 'MISSING'} ({mod_dir})")
    if not dll.exists() or not manifest.exists():
        ok = False
        print("     fix: run setup/install-mod.sh")
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
                    f"assembly_hash={hello.get('assembly_hash')}"
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
    with BridgeClient(host=args.host, port=args.port) as client:
        state = client.state()
    log_run_event("state", {"state": state})
    if state.get("screen") == "game_over" or (state.get("run") or {}).get("is_game_over"):
        log_run_event("run_end", {"state": state}, finalize=True)
    if args.json:
        print(json.dumps(state, indent=2, ensure_ascii=False))
    else:
        print(render_compact(state))
    return 0


def cmd_act(args):
    act_args = json.loads(args.args) if args.args else None
    with BridgeClient(host=args.host, port=args.port) as client:
        result = client.act(args.action, act_args)
    rotate = args.action in ("start_run", "continue_run")
    log_run_event("act", {"action": args.action, "args": act_args, "result": result}, rotate=rotate)
    if (result.get("state") or {}).get("screen") == "game_over":
        log_run_event("run_end", {"last_action": args.action, "state": result.get("state")}, finalize=True)
    print(f"ok={result.get('ok')} message={result.get('message')}")
    state = result.get("state")
    if state:
        if args.json:
            print(json.dumps(state, indent=2, ensure_ascii=False))
        else:
            print(render_compact(state))
    return 0 if result.get("ok") else 1


def cmd_wait(args):
    deadline = time.time() + args.timeout
    with BridgeClient(host=args.host, port=args.port) as client:
        prev = client.state().get("fingerprint")
        print(f"waiting (initial fingerprint={prev})")
        while time.time() < deadline:
            time.sleep(args.interval)
            try:
                state = client.state()
            except (ConnectionError, OSError, json.JSONDecodeError) as exc:
                print(f"poll failed: {exc}")
                return 1
            fp = state.get("fingerprint")
            if fp != prev:
                print(f"changed -> fingerprint={fp} screen={state.get('screen')}")
                log_run_event("wait_change", {"state": state})
                print(render_compact(state) if not args.json else json.dumps(state, indent=2, ensure_ascii=False))
                return 0
    print(f"timeout after {args.timeout}s (fingerprint={prev})")
    log_run_event("wait_timeout", {"fingerprint": prev, "timeout": args.timeout})
    return 1


def steam_fully_ready():
    """Steam client process exists and a helper/renderer process is up."""
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


def main(argv=None):
    parser = argparse.ArgumentParser(prog="spirectl", description=__doc__)
    parser.add_argument("--host", default=os.environ.get("SPIREBRIDGE_HOST", DEFAULT_HOST))
    parser.add_argument("--port", type=int, default=int(os.environ.get("SPIREBRIDGE_PORT", DEFAULT_PORT)))
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("doctor", help="check mod install, game process, bridge handshake")

    p_state = sub.add_parser("state", help="read current game state")
    p_state.add_argument("--json", action="store_true", help="print full JSON instead of compact text")

    p_act = sub.add_parser("act", help="send one action to the game")
    p_act.add_argument("action", help="action name, e.g. play / end_turn / choose / map_select")
    p_act.add_argument("--args", help="action args as JSON object, e.g. '{\"card_index\":0}'")
    p_act.add_argument("--json", action="store_true", help="print returned state as JSON")

    p_wait = sub.add_parser("wait", help="poll until game state fingerprint changes")
    p_wait.add_argument("--timeout", type=float, default=60.0)
    p_wait.add_argument("--interval", type=float, default=0.4)
    p_wait.add_argument("--json", action="store_true")

    p_launch = sub.add_parser("launch", help="launch the game via Steam and wait for the bridge")
    p_launch.add_argument("--timeout", type=float, default=120.0)

    sub.add_parser("stop", help="gracefully stop the game (quiet quit -> TERM -> KILL)")

    args = parser.parse_args(argv)
    handlers = {
        "doctor": cmd_doctor,
        "state": cmd_state,
        "act": cmd_act,
        "wait": cmd_wait,
        "launch": cmd_launch,
        "stop": cmd_stop,
    }
    try:
        return handlers[args.cmd](args)
    except (ConnectionError, OSError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
