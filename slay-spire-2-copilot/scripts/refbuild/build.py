"""Build orchestration: --check gate, or overlay refresh of the JSON store.

The references/game JSON files are the durable source of truth (markdown
twins retired). Generate mode is an overlay pass: codex enrichment +
curated extras + zh twin fill + move/zh fixups applied ON TOP of the
existing store — keys are never dropped, curated:true entries never
overwritten.
"""
import argparse
import json
import sys
from pathlib import Path

from . import census, codex, fixups
from .config import DOMAINS, DEFAULT_LIVE_IDS, DEFAULT_OUT_DIR
from .data import CURATED_MOVES
from .merge import apply_extras, envelope, fill_zh_twins, load_existing
from .textutil import humanize


def _apply_curated_moves(en: dict):
    """Fill missing/uncurated monster move entries from CURATED_MOVES tables."""
    for mon_key, move_map in CURATED_MOVES.items():
        mon = (en.get("monsters") or {}).get(mon_key)
        if mon is None:
            continue
        moves = dict(mon.get("moves") or {})
        for mk, (mid, mname, mdesc, mintent, bdmg, basc, hits) in move_map.items():
            prev = moves.get(mk)
            if prev is not None and (prev.get("description") or "").strip() \
                    and not prev.get("description", "").startswith(mid):
                continue
            moves[mk] = envelope(
                mid, "move", mname, mdesc,
                aliases=[humanize(mid.replace("_MOVE", ""))],
                play_notes="",
                source="curated:census + monsters.md archive cycle",
                monster_id=mon_key,
                intents=[mintent] if mintent else [],
                base_damage=bdmg,
                base_damage_ascension=basc,
                hits=hits,
                status_count=None,
                display_note=None,
            )
        mon["moves"] = moves
        mon.setdefault("cycle", [])
        if mon_key == "SEAPUNK" and not mon["cycle"]:
            mon["cycle"] = ["SEA_KICK_MOVE", "SPINNING_KICK_MOVE",
                            "BUBBLE_BURP_MOVE"]


def _propagate_affliction_hosts(en: dict):
    """Set power host_of_affliction flags derived from affliction entries."""
    for aff in en.get("afflictions", {}).values():
        host = aff.get("host_power_id")
        if host and host in en.get("powers", {}):
            en["powers"][host]["host_of_affliction"] = True
            keys = set(en["powers"][host].get("affliction_keys") or [])
            keys.add(aff["id"])
            en["powers"][host]["affliction_keys"] = sorted(keys)


def main(argv=None) -> int:
    """Parse CLI args and run check or overlay-build. Returns exit code."""
    parser = argparse.ArgumentParser(description="Build references/game JSON DB")
    parser.add_argument("--live-ids", default=str(DEFAULT_LIVE_IDS))
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    parser.add_argument("--check", action="store_true",
                        help="coverage gate only (reads existing JSON output)")
    parser.add_argument("--no-codex", action="store_true",
                        help="skip spire-codex.com enrichment")
    parser.add_argument("--codex-refresh", action="store_true",
                        help="re-fetch codex API instead of using cache")
    args = parser.parse_args(argv)

    out_dir = Path(args.out_dir)
    live_path = Path(args.live_ids)
    live_ids = {}
    if live_path.exists():
        live_ids = json.loads(live_path.read_text(encoding="utf-8"))
    else:
        print(f"build_game_reference_json: WARN live-ids missing ({live_path})",
              file=sys.stderr)

    if args.check:
        all_en = {d: load_existing(out_dir / f"{d}.json") for d in DOMAINS}
        all_zh = {d: load_existing(out_dir / f"{d}_zh.json") for d in DOMAINS}
        return census.run_check(all_en, all_zh, live_ids)

    print(f"build_game_reference_json: out={out_dir} live-ids={live_path} mode=overlay")
    en = {d: load_existing(out_dir / f"{d}.json") for d in DOMAINS}
    zh = {d: load_existing(out_dir / f"{d}_zh.json") for d in DOMAINS}

    if not args.no_codex:
        hits = codex.fold_codex(en, live_ids, refresh=args.codex_refresh)
        print(f"  codex fold: {hits} API hits (cache: {codex.CODEX_CACHE})")
    fixups.apply_move_fixups(en)
    _propagate_affliction_hosts(en)
    _apply_curated_moves(en)

    for domain in DOMAINS:
        fill_zh_twins(en[domain], zh[domain])
        apply_extras(domain, en[domain], zh[domain])
        if domain == "monsters":
            _apply_curated_moves(en)

    fixups.apply_post_fixups(en)
    for domain in DOMAINS:
        fill_zh_twins(en[domain], zh[domain])

    for domain in DOMAINS:
        en_path = out_dir / f"{domain}.json"
        zh_path = out_dir / f"{domain}_zh.json"
        en_path.write_text(json.dumps(en[domain], ensure_ascii=False, indent=2,
                                      sort_keys=True) + "\n", encoding="utf-8")
        zh_path.write_text(json.dumps(zh[domain], ensure_ascii=False, indent=2,
                                      sort_keys=True) + "\n", encoding="utf-8")
        print(f"  wrote {en_path.name} ({len(en[domain])}) + {zh_path.name} "
              f"({len(zh[domain])})")

    all_en = {d: load_existing(out_dir / f"{d}.json") for d in DOMAINS}
    all_zh = {d: load_existing(out_dir / f"{d}_zh.json") for d in DOMAINS}
    return census.run_check(all_en, all_zh, live_ids)


if __name__ == "__main__":
    sys.exit(main())
