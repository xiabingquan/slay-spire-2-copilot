"""Bridge TCP client (line-delimited JSON), settle polling, timing metrics."""
import json
import socket
import sys
import time

from . import infogate
from .config import DEFAULT_HOST, DEFAULT_PORT
from .textutil import strip_bbcode


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

    def _raw_request(self, payload):
        """Send one JSON request and read one JSON response line (no info gate)."""
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

    def request(self, payload):
        """Send one JSON request and read one JSON response line.

        Information-completeness gate: incomplete server info is a hard stop
        plus Feishu notification, never played through. Transient
        incompleteness (settle-lag during screen transitions) self-heals with
        one re-read of state; only persistent incompleteness stops.

        Args:
            payload: Serializable request object.

        Returns:
            Parsed response dict.

        Raises:
            ConnectionError: If the server closes the connection.
            OSError, json.JSONDecodeError: Transport or payload failures.
        """
        resp = self._raw_request(payload)
        if infogate.gate_triggered(resp):
            time.sleep(0.4)
            try:
                fresh = self._raw_request({"type": "state"})
            except Exception:
                fresh = None
            fresh_st = None
            if isinstance(fresh, dict):
                fresh_st = fresh.get("state") if isinstance(fresh.get("state"), dict) else fresh
            if isinstance(fresh_st, dict) and fresh_st.get("info_complete") is not False:
                print(
                    "[INFO-INCOMPLETE] transient — immediate re-read shows "
                    "info_complete, continuing without stop flag",
                    file=sys.stderr,
                )
                if payload.get("type") == "state" and isinstance(fresh, dict):
                    resp = fresh
            else:
                infogate.stop_and_notify(resp)
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
        del exc_type, exc_val, exc_tb
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

    Change-polling model (no timeout deadlines): keep polling while the
    fingerprint keeps changing — that is real game progress. The only
    early-out besides the target condition is a frozen fingerprint: if state
    does not change for stall_s and the condition is still unmet, return
    flagged stalled=True so the caller can re-read and decide.

    Args:
        client: Connected BridgeClient.
        mode: "settle" waits for a stable fingerprint; "play" additionally
            requires combat_play_ready (Play phase / non-combat / game_over).
        stall_s: Frozen-fingerprint window that ends the poll as stalled.
        stable_s: Fingerprint stability window required to declare settled.

    Returns:
        Tuple (state, settle_ms, stalled): last snapshot, polling wall time,
        and whether the wait ended without reaching the target condition.
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


def format_intent_bits(intents, move_id=None):
    """Build compact intent descriptors from structured intent dicts.

    Args:
        intents: List of structured intent dicts from combat state.
        move_id: Host move id, used only to label FORMAT_EMPTY fallbacks.

    Returns:
        List of compact descriptor strings, one per intent.
    """
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
