#!/usr/bin/env python3
"""Phase 0 — live-id census for the SpireBridge JSON reference pipeline.

Scans SpireBridge run-*.log NDJSON files (each line: {"kind": "...",
"state": {...full state snapshot...}, ...}) and collects every game
identifier the wire has actually emitted. Output is the coverage oracle
for scripts/build_game_reference_json.py --check.

Domains collected (sorted lists + counts):
  move_ids          creatures[].move_id
  power_ids         creatures[].powers[].id (player creature included)
  relic_ids         player.relics[].id
  card_ids          player.deck[].id + combat piles (trailing '+' stripped)
  potion_ids        player.potions[].id
  event_option_ids  screen_detail.options[].id where kind == event_option
  card_option_ids   screen_detail.options[].id where kind == card
  relic_option_ids  screen_detail.options[].id where kind == relic
  button_option_ids screen_detail.options[].id where kind in (button, reward,
                    card_removal, shop_item, crystal_cell, hand_card, map_point)
  character_ids     player.character / player.character_id
  event_ids         textKey prefix before '.pages.' / '.dialogue.'
  intent_classes    creatures[].intents[].class
  intent_types      creatures[].intents[].type
  creature_names    creatures[].name (localized display names -> monster aliases)

Usage:
  python3 scripts/extract_live_ids.py [--logs DIR] [--out PATH]

Defaults: --logs $SPIREBRIDGE_LOG_DIR or /Users/xiabingquan/spire-logs;
--out scripts/.cache/live_ids.json (relative to this repo's skill folder).
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from collections import Counter
from pathlib import Path

DEFAULT_LOG_DIR = os.environ.get("SPIREBRIDGE_LOG_DIR", "/Users/xiabingquan/spire-logs")
SKILL_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUT = SKILL_ROOT / "scripts" / ".cache" / "live_ids.json"

# option kinds whose ids are game identifiers we want in the census
OPTION_KIND_BUCKETS = {
    "event_option": "event_option_ids",
    "card": "card_option_ids",
    "relic": "relic_option_ids",
    "button": "button_option_ids",
    "reward": "button_option_ids",
    "card_removal": "button_option_ids",
    "shop_item": "button_option_ids",
    "crystal_cell": "button_option_ids",
    "hand_card": "button_option_ids",
    "map_point": "button_option_ids",
}


def strip_upgrade(card_id: str) -> str:
    """STRIKE_IRONCLAD+ -> STRIKE_IRONCLAD (upgrade marker is display-only)."""
    return card_id[:-1] if card_id.endswith("+") else card_id


def walk_state(state: dict, acc: dict) -> None:
    """Collect identifiers out of one state/result.state payload."""
    player = state.get("player")
    if isinstance(player, dict):
        for key in ("character", "character_id"):
            val = player.get(key)
            if val:
                acc["character_ids"][str(val)] += 1
        for relic in player.get("relics") or []:
            if isinstance(relic, dict) and relic.get("id"):
                acc["relic_ids"][relic["id"]] += 1
        for potion in player.get("potions") or []:
            if isinstance(potion, dict) and potion.get("id"):
                acc["potion_ids"][potion["id"]] += 1
            elif isinstance(potion, str) and potion:
                acc["potion_ids"][potion] += 1
        for card in player.get("deck") or []:
            if isinstance(card, dict) and card.get("id"):
                acc["card_ids"][strip_upgrade(card["id"])] += 1

    combat = state.get("combat")
    if isinstance(combat, dict):
        for creature in combat.get("creatures") or []:
            if not isinstance(creature, dict):
                continue
            if creature.get("name"):
                acc["creature_names"][creature["name"]] += 1
            if creature.get("move_id"):
                acc["move_ids"][creature["move_id"]] += 1
            for power in creature.get("powers") or []:
                if isinstance(power, dict) and power.get("id"):
                    acc["power_ids"][power["id"]] += 1
            for intent in creature.get("intents") or []:
                if not isinstance(intent, dict):
                    continue
                if intent.get("class"):
                    acc["intent_classes"][intent["class"]] += 1
                if intent.get("type"):
                    acc["intent_types"][intent["type"]] += 1
        piles = combat.get("piles")
        if isinstance(piles, dict):
            for value in piles.values():
                if not isinstance(value, list):
                    continue
                for card in value:
                    if isinstance(card, dict) and card.get("id"):
                        acc["card_ids"][strip_upgrade(card["id"])] += 1
                    elif isinstance(card, str) and card:
                        acc["card_ids"][strip_upgrade(card)] += 1

    screen_detail = state.get("screen_detail")
    if isinstance(screen_detail, dict):
        for opt in screen_detail.get("options") or []:
            if not isinstance(opt, dict) or not opt.get("id"):
                continue
            bucket = OPTION_KIND_BUCKETS.get(opt.get("kind"))
            if bucket:
                acc[bucket][opt["id"]] += 1
                if bucket == "event_option_ids":
                    text_key = opt["id"]
                    for sep in (".pages.", ".dialogue."):
                        if sep in text_key:
                            acc["event_ids"][text_key.split(sep, 1)[0]] += 1
                            break
                    else:
                        if text_key != "PROCEED":
                            acc["event_ids"][text_key] += 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--logs", default=DEFAULT_LOG_DIR,
                        help="directory containing run-*.log NDJSON files "
                             "(default: $SPIREBRIDGE_LOG_DIR or %s)" % DEFAULT_LOG_DIR)
    parser.add_argument("--out", default=str(DEFAULT_OUT),
                        help="output JSON path (default: scripts/.cache/live_ids.json)")
    args = parser.parse_args()

    log_dir = Path(args.logs)
    if not log_dir.is_dir():
        print(f"extract_live_ids: log dir not found: {log_dir}", file=sys.stderr)
        return 1
    log_files = sorted(log_dir.glob("run-*.log"))
    if not log_files:
        print(f"extract_live_ids: no run-*.log files under {log_dir}", file=sys.stderr)
        return 1

    acc: dict[str, Counter] = {name: Counter() for name in [
        "move_ids", "power_ids", "relic_ids", "card_ids", "potion_ids",
        "event_option_ids", "card_option_ids", "relic_option_ids",
        "button_option_ids", "character_ids", "event_ids",
        "intent_classes", "intent_types", "creature_names",
    ]}
    lines_total = 0
    states_total = 0
    parse_errors = 0

    for log_file in log_files:
        with log_file.open("r", encoding="utf-8", errors="replace") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                lines_total += 1
                try:
                    record = json.loads(line)
                except json.JSONDecodeError:
                    parse_errors += 1
                    continue
                if not isinstance(record, dict):
                    continue
                # NDJSON rows carry state under "state"; tolerate "result"."state"
                candidates = []
                if isinstance(record.get("state"), dict):
                    candidates.append(record["state"])
                result = record.get("result")
                if isinstance(result, dict) and isinstance(result.get("state"), dict):
                    candidates.append(result["state"])
                for state in candidates:
                    states_total += 1
                    walk_state(state, acc)

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "meta": {
            "log_dir": str(log_dir),
            "log_files": len(log_files),
            "lines_total": lines_total,
            "states_total": states_total,
            "parse_errors": parse_errors,
        },
        "counts": {},
    }
    for name, counter in acc.items():
        payload[name] = sorted(counter.keys())
        payload["counts"][name] = len(counter)

    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
                        encoding="utf-8")
    print(f"extract_live_ids: scanned {len(log_files)} files, "
          f"{states_total} state payloads ({lines_total} lines, "
          f"{parse_errors} parse errors)")
    for name in acc:
        print(f"  {name}: {payload['counts'][name]}")
    print(f"extract_live_ids: wrote {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
