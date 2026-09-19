"""CLI argument parsing and subcommand dispatch."""
import argparse
import json
import os
import sys

from . import commands
from .config import DEFAULT_HOST, DEFAULT_PORT

DESCRIPTION = "spirectl — talk to the spire-copilot-bridge mod inside Slay the Spire 2."


def build_parser():
    """Build the spirectl argparse parser with all subcommands."""
    parser = argparse.ArgumentParser(prog="spirectl", description=DESCRIPTION)
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
                         help="disable compact auto-lookup snippets from spirectl_lib/data JSON")

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
                       help="disable compact auto-lookup snippets from spirectl_lib/data JSON")

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
                         help="disable compact auto-lookup snippets from spirectl_lib/data JSON")

    p_wait = sub.add_parser("wait", help="poll for a state fingerprint change; returns quickly when idle")
    p_wait.add_argument("--quiet", type=float, default=3.0,
                        help="return current state after this many seconds without a fingerprint change")
    p_wait.add_argument("--interval", type=float, default=0.2)
    p_wait.add_argument("--json", action="store_true")
    p_wait.add_argument("--no-ref-tags", action="store_true",
                        help="disable compact auto-lookup snippets from spirectl_lib/data JSON")

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

    return parser


def main(argv=None):
    """Parse CLI arguments and dispatch to the subcommand handler.

    Args:
        argv: Argument list; None uses sys.argv[1:].

    Returns:
        Exit code from the selected subcommand.
    """
    parser = build_parser()
    args = parser.parse_args(argv)
    # Compact ref-tag opt-out: one env switch honored by render_compact.
    if getattr(args, "no_ref_tags", False):
        os.environ["SPIREBRIDGE_REF_TAGS"] = "0"
    handlers = {
        "doctor": commands.cmd_doctor,
        "watchdog": commands.cmd_watchdog,
        "state": commands.cmd_state,
        "act": commands.cmd_act,
        "batch": commands.cmd_batch,
        "wait": commands.cmd_wait,
        "profile": commands.cmd_profile,
        "launch": commands.cmd_launch,
        "sl": commands.cmd_sl,
        "stop": commands.cmd_stop,
        "lookup": commands.cmd_lookup,
    }
    try:
        return handlers[args.cmd](args)
    except (ConnectionError, OSError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
