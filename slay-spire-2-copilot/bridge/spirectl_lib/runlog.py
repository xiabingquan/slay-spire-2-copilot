"""Run-log machinery: SPIREBRIDGE_LOG_DIR resolution, rotation, JSONL events.

Run-log directory: SPIREBRIDGE_LOG_DIR only — no pointer files, no CLI flags,
no fallback directory. Unset -> commands that write run logs fail fast.
  export SPIREBRIDGE_LOG_DIR=/abs/dir
"""
import hashlib
import json
import os
import secrets
import time
from pathlib import Path

LOG_DIR_UNSET_ERROR = (
    "SPIREBRIDGE_LOG_DIR is not set. The skill invocation must supply an "
    "absolute log folder path; set SPIREBRIDGE_LOG_DIR for the whole session. "
    "There is no fallback log directory."
)
POINTER_NAME = ".current_run"


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


def current_log_dir():
    """Return the resolved log directory, or None when the env var is unset."""
    try:
        return resolve_log_dir()
    except RuntimeError:
        return None


def require_log_dir():
    """Return the active log directory and its current-run pointer file.

    Returns:
        Tuple (log_dir, pointer_path).

    Raises:
        SystemExit: If SPIREBRIDGE_LOG_DIR was never set for this process.
    """
    try:
        log_dir = resolve_log_dir()
    except RuntimeError as exc:
        raise SystemExit(f"error: {exc}")
    return log_dir, log_dir / POINTER_NAME


def runlog_file():
    """Return the active run-log file path, deriving one if needed.

    File names are run-<timestamp>-<hash8>.log inside SPIREBRIDGE_LOG_DIR;
    rotation is driven by the .current_run pointer in that same folder.

    Returns:
        Path of the current run log file.

    Raises:
        SystemExit: If SPIREBRIDGE_LOG_DIR is unset.
    """
    log_dir, pointer = require_log_dir()
    log_dir.mkdir(parents=True, exist_ok=True)
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
        (SPIREBRIDGE_NO_RUNLOG set).

    Raises:
        SystemExit: If a write is required but SPIREBRIDGE_LOG_DIR is unset.
    """
    if os.environ.get("SPIREBRIDGE_NO_RUNLOG"):
        return None
    _, pointer = require_log_dir()
    if rotate and pointer.exists():
        pointer.unlink(missing_ok=True)
    path = runlog_file()
    record = {"ts": time.strftime("%Y-%m-%d %H:%M:%S"), "kind": kind, **data}
    if finalize:
        record["outcome"] = data.get("outcome") or "game_over"
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")
    return path


def load_run_events(path=None):
    """Load JSON events from a run log.

    Args:
        path: Explicit log file; None uses the current run pointer.

    Returns:
        Tuple (path, events); events is empty when nothing could be loaded.
        path is None when no explicit path was given and the pointer is missing.

    Raises:
        SystemExit: If no explicit path is given and SPIREBRIDGE_LOG_DIR is unset.
    """
    if path:
        target = Path(path)
    else:
        log_dir, pointer_path = require_log_dir()
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
