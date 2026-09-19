"""Build orchestration: --check gate, or overlay refresh of the JSON store.

spirectl_lib/data is the programmatic source of truth (schema:
spirectl_lib/schema.py). Generate mode is an overlay pass — codex structure
fills + curated structured overlays + zh twin maintenance; keys are never
dropped, existing values never overwritten.
"""
import argparse
import copy
import json
import sys
from pathlib import Path

from . import census, codex
from .config import DOMAINS, DEFAULT_LIVE_IDS, DEFAULT_OUT_DIR
from .data import CURATED_MOVES
from .merge import apply_extras, fill_zh_twins, load_existing, sync_twins
from spirectl_lib.refs import new_entry, move_entry  # noqa: E402


def _apply_curated_moves(en: dict):
    """Fill missing monster move records from structured CURATED_MOVES."""
    for mon_key, move_map in CURATED_MOVES.items():
        e = en.get("monsters", {}).get(mon_key)
        if not isinstance(e, dict):
            continue
        det = e.setdefault("detail", {})
        moves = det.setdefault("moves", {})
        cycle = list(det.get("cycle") or [])
        for mk, tup in move_map.items():
            mid, mname, mintent, bdmg, basc, hits_n = tup
            if mk in moves:
                continue
            intents = []
            if mintent:
                cls_map = {"Attack": "SingleAttackIntent", "MultiAttack": "MultiAttackIntent",
                           "Buff": "BuffIntent", "Debuff": "DebuffIntent", "Defend": "DefendIntent"}
                cls = cls_map.get(str(mintent).split("Intent")[0] + "Intent" if False else "",
                                  "SingleAttackIntent" if mintent == "Attack" else (
                                  "MultiAttackIntent" if mintent == "MultiAttack" else (
                                  "BuffIntent" if mintent == "Buff" else (
                                  "DebuffIntent" if mintent == "Debuff" else (
                                  "DefendIntent" if mintent == "Defend" else "UnknownIntent")))))
                it = {"class": cls, "type": "Attack" if "Attack" in cls else (mintent or "")}
                if bdmg is not None:
                    it.update({"base_damage": bdmg, "hits": hits_n or 1})
                    if basc is not None:
                        it["base_damage_ascension"] = basc
                intents.append(it)
            moves[mk] = move_entry(mid, mon_key, name=mname, intents=intents,
                                   base_damage=bdmg, base_damage_ascension=basc, hits=hits_n)
            if mk not in cycle and len(cycle) < 12:
                cycle.append(mk)
        det["cycle"] = cycle[:12]


def _propagate_affliction_hosts(en: dict):
    """Set power detail.host_of_affliction / affliction_keys from afflictions."""
    for aff in (en.get("afflictions") or {}).values():
        if not isinstance(aff, dict):
            continue
        host = (aff.get("detail") or {}).get("host_power_id")
        powers = en.get("powers") or {}
        if host and host in powers and isinstance(powers[host], dict):
            det = powers[host].setdefault("detail", {})
            det["host_of_affliction"] = True
            keys = set(det.get("affliction_keys") or [])
            keys.add(aff.get("id"))
            det["affliction_keys"] = sorted(keys)


def main(argv=None) -> int:
    """Parse CLI args and run check or overlay-build. Returns exit code."""
    parser = argparse.ArgumentParser(description="Build spirectl_lib/data JSON DB")
    parser.add_argument("--live-ids", default=str(DEFAULT_LIVE_IDS))
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    parser.add_argument("--check", action="store_true",
                        help="coverage/schema gate only (reads existing JSON)")
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
        print(f"build_game_reference_json: WARN live-ids missing ({live_path})", file=sys.stderr)

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
    _propagate_affliction_hosts(en)
    _apply_curated_moves(en)
    for domain in DOMAINS:
        fill_zh_twins(en[domain], zh[domain])
        apply_extras(domain, en[domain], zh[domain])
        if domain == "monsters":
            _apply_curated_moves(en)
        sync_twins(en[domain], zh[domain])

    for domain in DOMAINS:
        en_path = out_dir / f"{domain}.json"
        zh_path = out_dir / f"{domain}_zh.json"
        en_path.write_text(json.dumps(en[domain], ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        zh_path.write_text(json.dumps(zh[domain], ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(f"  wrote {en_path.name} ({len(en[domain])}) + {zh_path.name} ({len(zh[domain])})")

    all_en = {d: load_existing(out_dir / f"{d}.json") for d in DOMAINS}
    all_zh = {d: load_existing(out_dir / f"{d}_zh.json") for d in DOMAINS}
    return census.run_check(all_en, all_zh, live_ids)


if __name__ == "__main__":
    sys.exit(main())
