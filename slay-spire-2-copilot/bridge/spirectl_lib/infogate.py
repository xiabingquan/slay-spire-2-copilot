"""Information-completeness contract: hard-stop gate plus Feishu notification.

The bridge server must return exactly what a player can read in-game — no
uncertainty, no fallbacks. Payloads with notify_user=true / info_complete=false
record a stop flag, notify Feishu once, and exit 78; further act/batch/sl
calls are refused until the flag file is removed. Transient settle-lag
incompleteness self-heals in client.request via one state re-read.
"""
import subprocess
import sys
from pathlib import Path

from .config import (
    INFO_NOTIFY_SCRIPT,
    INFO_STOP_EXIT,
    INFO_STOP_FLAG,
    WATCHDOG_STATE_DIR,
)


def stop_flag_exists():
    """True when a hard-stop flag file is present."""
    return INFO_STOP_FLAG.exists()


def extract_missing(obj):
    """Pull missing_info / notify reasons from an act_result or state payload.

    Args:
        obj: Bridge response or state dict.

    Returns:
        Deduplicated list of missing-info strings; possibly empty.
    """
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


def gate_triggered(obj):
    """True when a payload signals incomplete game information.

    Args:
        obj: Bridge response or state dict.

    Returns:
        True on notify_user=true, info_complete=false, or an
        "info incomplete" error message.
    """
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


def stop_and_notify(obj):
    """Hard-stop path: record the stop, ping Feishu once per fingerprint, exit 78.

    Args:
        obj: Payload that failed the information-completeness gate.

    Raises:
        SystemExit: Always, with code INFO_STOP_EXIT.
    """
    missing = extract_missing(obj)
    reason = "\n".join(f"- {m}" for m in missing) if missing else "- (unspecified incompleteness)"
    fingerprint = "\n".join(missing)
    already = INFO_STOP_FLAG.exists() and INFO_STOP_FLAG.read_text(encoding="utf-8").strip() == fingerprint
    WATCHDOG_STATE_DIR.mkdir(parents=True, exist_ok=True)
    INFO_STOP_FLAG.write_text(fingerprint, encoding="utf-8")
    print("[INFO-INCOMPLETE] server returned incomplete information — execution stopped (no fallback)", file=sys.stderr)
    print(reason, file=sys.stderr)
    print(f"[INFO-INCOMPLETE] stop flag: {INFO_STOP_FLAG}", file=sys.stderr)
    if not already and Path(INFO_NOTIFY_SCRIPT).exists():
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


def require_no_stop():
    """Refuse act-family commands while an earlier stop flag is armed.

    Raises:
        SystemExit: With code INFO_STOP_EXIT when the stop flag exists.
    """
    if stop_flag_exists():
        print("[INFO-INCOMPLETE] act refused: stop flag set — server info was incomplete earlier", file=sys.stderr)
        print(f"  clear with: rm {INFO_STOP_FLAG}", file=sys.stderr)
        sys.exit(INFO_STOP_EXIT)
