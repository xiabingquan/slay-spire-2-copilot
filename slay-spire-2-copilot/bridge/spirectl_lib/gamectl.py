"""Game/Steam process lifecycle: stop, readiness checks, window placement."""
import subprocess
import time

from .config import REPO_ROOT


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


def game_process_pids():
    """Return pgrep lines for running Slay the Spire 2 processes."""
    proc = subprocess.run(["pgrep", "-f", "Slay the Spire 2"], capture_output=True, text=True)
    return [ln for ln in proc.stdout.strip().splitlines() if ln]


def game_process_running():
    """Return True when a Slay the Spire 2 process is present."""
    return bool(game_process_pids())


def suppress_crash_dialogs():
    """Silence the macOS CrashReporter dialog after hard kills."""
    subprocess.run(
        ["defaults", "write", "com.apple.CrashReporter", "DialogType", "-string", "none"],
        capture_output=True,
    )


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


def _run_window_script(argv, label):
    """Run scripts/focus_game_window.sh and echo its output; never raise.

    Args:
        argv: Full argument list for subprocess.run.
        label: Prefix for error messages.
    """
    try:
        result = subprocess.run(argv, capture_output=True, text=True, timeout=25)
        msg = (result.stdout or "").strip()
        if msg:
            print(msg)
        err = (result.stderr or "").strip()
        if result.returncode != 0 and err:
            print(f"{label}: {err}")
    except (subprocess.TimeoutExpired, OSError) as exc:
        print(f"{label}: skipped ({exc})")


def focus_game_window():
    """Place the game window after launch via focus_game_window.sh (cosmetic).

    Relaunches restore the window to its last recorded screen+position when a
    record exists (written by record_game_window_pos on graceful stops);
    otherwise the script falls back to terminal-display placement. A failed
    move must never block launch recovery.
    """
    script = REPO_ROOT / "scripts" / "focus_game_window.sh"
    if not script.exists():
        return
    _run_window_script(["bash", str(script)], "focus_game_window")


def record_game_window_pos():
    """Record the CURRENT game window position for later restore (cosmetic).

    Called on graceful stop paths while the window still exists; writes the
    position cache via focus_game_window.sh --record. A failed record only
    means the next launch falls back to terminal-relative placement.
    """
    script = REPO_ROOT / "scripts" / "focus_game_window.sh"
    if not script.exists():
        return
    _run_window_script(["bash", str(script), "--record"], "record_game_window_pos")


def stop_game():
    """Stop the game: AppleEvent quit, then SIGTERM, then SIGKILL.

    Returns:
        Process exit code (0 once the game process is gone).
    """
    suppress_crash_dialogs()
    if not game_process_running():
        print("game not running")
        return 0
    # Capture the window's current screen+position before tearing the
    # process down — relaunches restore to this record.
    record_game_window_pos()
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
