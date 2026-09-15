# Commands and state reference

spirectl speaks JSON-lines TCP to the spire-copilot-bridge mod (default
127.0.0.1:17612). Run all commands from the skill folder
`<repo>/slay-spire-2-copilot` (holds bridge/, mod/, setup/, docs/, skill memory).

## Runtime log folder (env-only)

The skill invocation takes a **log folder** (absolute directory), not a file.
Deliver it only via environment variable — no pointer files, no CLI flags, no
personal paths inside the repo:

    SPIREBRIDGE_LOG_DIR=/abs/folder python3 bridge/spirectl.py state
    SPIREBRIDGE_LOG_DIR=/abs/folder python3 bridge/spirectl.py act play --args '{...}'

Resolution: `SPIREBRIDGE_LOG_DIR` env > per-user fallback
`~/.local/share/slay-spire-2-copilot/logs` (computed at runtime, never stored
in the project). Inside the folder each run derives a unique file name:

    run-<YYYYmmdd-HHMMSS>-<hash8>.log     # timestamp + short sha256

e.g. `run-20260916-013052-a3f9c012.log`. A `.current_run` pointer in the same
folder tracks the active file across rotation (start_run/continue_run rotates,
game_over finalizes). `doctor` prints `[0] run log dir: ... | SPIREBRIDGE_LOG_DIR=...`.

External liveness watchdog (crontab `bridge/watchdog-external.sh`) reads
`SPIREBRIDGE_LOG_DIR` from **its own environment** (set it on the crontab line
to track the active session folder; otherwise it watches the fallback folder).
Alerts fire only while ARMED:

    python3 bridge/spirectl.py watchdog enable    # session start
    python3 bridge/spirectl.py watchdog disable   # user stopped play
    python3 bridge/spirectl.py watchdog status

## CLI

    python3 bridge/spirectl.py doctor
    python3 bridge/spirectl.py watchdog enable|disable|status
    python3 bridge/spirectl.py launch
    python3 bridge/spirectl.py state [--json]
    python3 bridge/spirectl.py act <action> [--args '{"k":v}'] [--wait|--wait-play] [--json]
    python3 bridge/spirectl.py batch --acts '[{"action":"play","args":{"card_index":2}},{"action":"end_turn"}]'
    python3 bridge/spirectl.py wait [--timeout 60] [--interval 0.2]
    python3 bridge/spirectl.py profile [--log /abs/folder/run-<ts>-<hash>.log] [--budget 30]
    python3 bridge/spirectl.py sl [--json]
    python3 bridge/spirectl.py stop
