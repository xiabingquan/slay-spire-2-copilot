"""CLI subcommand handlers: doctor, watchdog, state, act, batch, wait, profile, launch, sl, stop, lookup."""
import json
import os
import subprocess
import sys
import time
from datetime import datetime

from . import gamectl, infogate, refs, render, runlog
from .client import BridgeClient, metrics_line, wait_for_settle
from .config import (
    GAME_LOG,
    GAME_MODS_DIR,
    MOD_ID,
    STEAM_APP_ID,
    WATCHDOG_DISARM,
    WATCHDOG_LAST_NOTIFY,
    WATCHDOG_STATE_DIR,
)


def print_state(state, as_json=False):
    """Print a state snapshot as compact text or full JSON."""
    render.print_state(state, as_json)


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


def _log_game_over(state, last_action=None):
    """Log a run_end event when the snapshot shows game over.

    Args:
        state: Bridge state snapshot.
        last_action: Action name that led to the snapshot, if any.
    """
    if state and (state.get("screen") == "game_over" or (state.get("run") or {}).get("is_game_over")):
        payload = {"state": state}
        if last_action:
            payload["last_action"] = last_action
        runlog.log_run_event("run_end", payload, finalize=True)


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
    log_dir = runlog.current_log_dir()
    print(f"state dir: {WATCHDOG_STATE_DIR}")
    print(f"run log dir: {log_dir or 'UNSET'} (SPIREBRIDGE_LOG_DIR={'set' if os.environ.get('SPIREBRIDGE_LOG_DIR') else 'unset — required, no fallback'})")
    return 0


def cmd_stop(args):
    """Stop the game process (AppleEvent quit -> SIGTERM -> SIGKILL).

    Args:
        args: Parsed CLI args (unused).

    Returns:
        Process exit code (0 once the game process is gone).
    """
    return gamectl.stop_game()


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
    print(f"[0] run log dir: {runlog.current_log_dir() or 'UNSET'} | SPIREBRIDGE_LOG_DIR={env_dir or 'unset — required, no fallback'}")
    mod_dir = GAME_MODS_DIR / MOD_ID
    dll = mod_dir / f"{MOD_ID}.dll"
    manifest = mod_dir / f"{MOD_ID}.json"
    print(f"[1] mod files: {'OK' if dll.exists() and manifest.exists() else 'MISSING'} ({mod_dir})")
    if not dll.exists() or not manifest.exists():
        ok = False
        print("     fix: run scripts/install_mod.sh")
    pids = gamectl.game_process_pids()
    game_running = bool(pids)
    print(f"[2] game process: {'running pid=' + pids[0] if game_running else 'not running'}")
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
    runlog.log_run_event("state", {"state": state, "metrics": metrics})
    _log_game_over(state)
    print(f"[{metrics_line(metrics)}]")
    print_state(state, args.json)
    return 0


def cmd_act(args):
    """Submit one action and optionally wait for settle/play.

    Args:
        args: Parsed CLI args (action, args, wait/wait-play/wait-mode,
            wait-timeout, stall-timeout, json).

    Returns:
        Process exit code: 0 ok, 1 failed act, 3 stall.
    """
    infogate.require_no_stop()
    act_args = json.loads(args.args) if args.args else None
    wait_mode = None
    if args.wait or args.wait_play or args.wait_mode:
        wait_mode = _wait_mode_for(args.action, args.wait_mode or ("play" if args.wait_play else "settle"))
    with BridgeClient(host=args.host, port=args.port) as client:
        t0 = time.perf_counter()
        result = client.act(args.action, act_args)
        metrics = dict(client.last_metrics)
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
    rotate = args.action in ("start_run", "continue_run")
    runlog.log_run_event(
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
    _log_game_over(result.get("state"), last_action=args.action)
    settle_note = f" settle={settle_ms}ms mode={wait_mode}" if wait_mode else ""
    stall_note = " STALL" if stalled else ""
    print(f"ok={result.get('ok')} message={result.get('message')} [{metrics_line(metrics)}{settle_note}{stall_note}]")
    state = result.get("state")
    if state:
        print_state(state, args.json)
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
        Process exit code: 0 ok, 1 failed act, 2 bad input, 3 stall.
    """
    infogate.require_no_stop()
    acts = json.loads(args.acts)
    if not isinstance(acts, list) or not acts:
        print("batch requires a non-empty JSON array of {action,args?}", file=sys.stderr)
        return 2
    with BridgeClient(host=args.host, port=args.port) as client:
        state = client.state()
        print(f"batch start [{metrics_line(client.last_metrics)}]")
        print_state(state, args.json)
        for i, item in enumerate(acts):
            action = item.get("action")
            act_args = item.get("args")
            if not action:
                print(f"batch[{i}] missing action — abort", file=sys.stderr)
                return 2
            result = client.act(action, act_args)
            metrics = dict(client.last_metrics)
            runlog.log_run_event("act", {"action": action, "args": act_args, "result": result, "metrics": metrics, "batch": i})
            ok = bool(result.get("ok"))
            print(f"batch[{i}] {action} ok={ok} {result.get('message')} [{metrics_line(metrics)}]")
            if not ok:
                state = client.state()
                print("batch aborted on failed act")
                print_state(state, args.json)
                return 1
            is_last = i == len(acts) - 1
            if is_last and not args.wait_final:
                state = result.get("state") or client.state()
                print_state(state, args.json)
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
            print_state(state, args.json)
            runlog.log_run_event(
                "wait_change" if not stalled else "wait_stall",
                {"state": state, "metrics": {"settle_ms": settle_ms, "stalled": stalled}, "batch": i, "mode": mode},
            )
            if stalled:
                return 3
            if (state or {}).get("screen") == "game_over":
                runlog.log_run_event("run_end", {"last_action": action, "state": state}, finalize=True)
                print("batch: game_over reached")
                return 0
    return 0


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
    path, events = runlog.load_run_events(args.log)
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

    Change-polling model (no timeout deadlines): return as soon as the
    fingerprint changes. If it stays unchanged for --quiet seconds, return
    the current state immediately with a "no change" note so the caller can
    decide — never block for minutes on an idle game.

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
                runlog.log_run_event("wait_change", {"state": state, "metrics": metrics})
                print_state(state, args.json)
                return 0
            if now - unchanged_since >= args.quiet:
                quiet_s = now - unchanged_since
                print(
                    f"no change after {quiet_s:.1f}s — returning current state "
                    f"(screen={state.get('screen')}, fingerprint={fp})"
                )
                runlog.log_run_event("wait_no_change", {"state": state, "metrics": metrics, "quiet_s": quiet_s})
                print_state(state, args.json)
                return 0


def _launch_game(host, port, timeout):
    """Start Steam/game if needed and poll until the bridge handshake answers.

    Args:
        host: Bridge host.
        port: Bridge port.
        timeout: Lifecycle cap for game boot + bridge handshake (seconds).

    Returns:
        0 when the bridge is up, 1 otherwise.
    """
    gamectl.suppress_crash_dialogs()
    if not gamectl.steam_fully_ready():
        print("Steam not ready; starting Steam and waiting for client boot")
        if subprocess.run(["pgrep", "-x", "Steam"], capture_output=True).returncode != 0:
            subprocess.run(["open", "-a", "Steam"], check=False)
        if not gamectl.wait_for(gamectl.steam_fully_ready, 60, interval=2.0):
            print("Steam client did not become ready; start Steam manually, then re-run launch")
            return 1
        time.sleep(5)  # extra settle time before issuing a rungameid URL
    if not gamectl.game_process_running():
        url = f"steam://rungameid/{STEAM_APP_ID}"
        print(f"launching via {url} (Steam ready)")
        subprocess.run(["open", url], check=False)
        if not gamectl.wait_for(gamectl.game_process_running, 45, interval=2.0):
            print("game did not start from Steam URL; retrying once after settle")
            time.sleep(5)
            subprocess.run(["open", url], check=False)
            gamectl.wait_for(gamectl.game_process_running, 45, interval=2.0)
    if not gamectl.game_process_running():
        print("game process did not start; launch it from the Steam client manually")
        return 1
    print("game process up; waiting for bridge")
    deadline = time.time() + timeout
    while time.time() < deadline:
        time.sleep(2)
        try:
            with BridgeClient(host=host, port=port) as client:
                hello = client.hello()
                if hello.get("type") != "hello_ok":
                    continue
                print(f"bridge up: game={hello.get('game_version')} mod={hello.get('mod_version')}")
                gamectl.focus_game_window()
                return 0
        except (ConnectionError, OSError, json.JSONDecodeError):
            continue
    print("bridge did not come up in time; run spirectl doctor for details")
    return 1


def cmd_launch(args):
    """Launch the game via Steam and wait for the bridge handshake.

    Args:
        args: Parsed CLI args (host, port, timeout).

    Returns:
        Process exit code: 0 when the bridge answers, 1 otherwise.
    """
    return _launch_game(args.host, args.port, args.timeout)


def cmd_sl(args):
    """Reload the current room: stop the game, relaunch, continue_run.

    The room-entry save replays combat with the same seed, so intents and
    draw order observed on the previous attempt stay valid.

    Args:
        args: Parsed CLI args (json, menu_timeout, stall_timeout).

    Returns:
        Process exit code: 0 ok, 2 launch failure, 3 reload stalled.
    """
    infogate.require_no_stop()
    t0 = time.perf_counter()
    print("[sl] stopping game")
    gamectl.stop_game()
    t_stop = time.perf_counter()
    print("[sl] launching")
    if _launch_game(args.host, args.port, 120.0) != 0:
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
                print_state(state, args.json)
                return 0
        print("[sl] continue_run")
        result = client.act("continue_run")
        runlog.log_run_event("act", {"action": "continue_run", "args": {"via": "sl"}, "result": result}, rotate=True)
        print(f"ok={result.get('ok')} {result.get('message')}")
        state, settle_ms, stalled = wait_for_settle(client, mode="settle", stall_s=args.stall_timeout)
        t_end = time.perf_counter()
        runlog.log_run_event(
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
        print_state(state, args.json)
        return 3 if stalled else 0


def cmd_lookup(args):
    """Resolve a live game id to its complete reference JSON entry.

    Miss path: fall back to spire-codex.com research — fetch candidate pages,
    fold a minimal entry into the matching spirectl_lib/data/*.json + _zh.json
    pair (curated:false), and return it. When codex has no page either,
    exit 1 with a loud web-research trigger (agent doctrine: perplexity-search
    -> fold into JSON EN+ZH -> re-run).

    Args:
        args: Parsed CLI args (key, json, lang, domain, all).

    Returns:
        Process exit code: 0 on hit (local or researched fold), 1 on miss.
    """
    key = args.key
    lang = args.lang or os.environ.get("SPIREBRIDGE_REF_LANG", "en")
    matches = refs.lookup_reference(key, lang=lang, domain=args.domain, match_all=args.all)
    if matches:
        domains = []
        for domain, entry in matches:
            domains.append(domain)
            if args.json:
                print(json.dumps(entry, ensure_ascii=False, indent=2))
            else:
                refs.print_entry(domain, entry, key)
                print("---")
        if not args.all and len(matches) == 1 and len(domains) == 1:
            return 0
        others = [d for d in domains]
        if others:
            print(f"(domains matched: {', '.join(others)} — use --all for every entry)")
        return 0

    # ---- miss: research fallback ----
    print(
        f"lookup: no entry for '{key}' in spirectl_lib/data/*.json — "
        "attempting spire-codex.com research fallback",
        file=sys.stderr,
    )
    domain_guess = refs.guess_domain(key, args.domain)
    entry, url = refs.research_and_fold(key, domain_guess=domain_guess)
    if entry:
        print(f"lookup: researched via {url} — structure folded into spirectl_lib/data")
        if args.json:
            print(json.dumps(entry, ensure_ascii=False, indent=2))
        else:
            refs.print_entry(domain_guess or entry.get("kind"), entry, key, extra=f"folded_from: {url}")
        print(
            "next: curate the ZH name in the _zh twin if needed; structured facts "
            "come from codex. Doctrine text belongs in memory/lessons. Re-run "
            "scripts/build_game_reference_json.py --check after edits.",
            file=sys.stderr,
        )
        return 0
    candidates = ", ".join(refs.codex_candidate_urls(key))
    print(
        f"lookup: MISS — '{key}' not in spirectl_lib/data/*.json and no spire-codex.com page matched.\n"
        f"  codex candidates tried: {candidates}\n"
        f"  next: research '{key}' via perplexity-search (or spire-codex.com browser search),\n"
        f"  fold structure into the matching <domain>.json + <domain>_zh.json (key='{key}',\n"
        f"  structure from codex), then re-run build_game_reference_json.py --check. "
        "A lookup miss is a research trigger — never permission to guess.",
        file=sys.stderr,
    )
    return 1
