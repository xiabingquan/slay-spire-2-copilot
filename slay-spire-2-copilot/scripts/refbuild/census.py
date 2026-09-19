"""Live-id coverage gate (--check): census resolution + entry quality checks.

Exits nonzero when: (1) any hard-domain live id from the census does not
resolve in the flattened index (top-level keys + aliases + monster moves +
event options); (2) any entry lacks a non-empty description in EN or ZH, the
ZH twin is missing, or EN/ZH key sets diverge; (3) an EN name field leaks CJK.
"""
from .config import DOMAINS, HARD_CENSUS_DOMAINS, SOFT_CENSUS_DOMAINS
from .textutil import has_cjk


def flatten_index(all_en: dict) -> dict:
    """Flatten every resolvable key/alias across domains into one index."""
    index: dict[str, list] = {}

    def reg(key, domain, entry):
        if key:
            index.setdefault(str(key), []).append((domain, entry))

    for domain, entries in all_en.items():
        for key, entry in entries.items():
            reg(key, domain, entry)
            for alias in entry.get("aliases") or []:
                reg(alias, domain, entry)
            if domain == "monsters":
                for mk, mv in (entry.get("moves") or {}).items():
                    reg(mk, "monster_move", mv)
                    for alias in mv.get("aliases") or []:
                        reg(alias, "monster_move", mv)
            if domain == "events":
                for ok, ov in (entry.get("options") or {}).items():
                    reg(ok, "event_option", ov)
                    for alias in ov.get("aliases") or []:
                        reg(alias, "event_option", ov)
    return index


def run_check(all_en: dict, all_zh: dict, live_ids: dict) -> int:
    """Run the coverage/quality gate over the JSON store. 0 = PASS."""
    index = flatten_index(all_en)
    misses = []
    for domain in HARD_CENSUS_DOMAINS:
        for lid in live_ids.get(domain) or []:
            if lid and lid not in index:
                misses.append((domain, lid))
    soft_misses = []
    for domain in SOFT_CENSUS_DOMAINS:
        for lid in live_ids.get(domain) or []:
            if lid and lid not in index:
                soft_misses.append((domain, lid))

    desc_problems = []
    cjk_name_problems = []
    for domain, entries in all_en.items():
        zh_entries = all_zh.get(domain) or {}
        for key, entry in entries.items():
            if has_cjk(entry.get("name")):
                cjk_name_problems.append((domain, key, entry.get("name")))
            if not (entry.get("description") or "").strip():
                desc_problems.append((domain, key, "EN description empty"))
            zh_e = zh_entries.get(key)
            if zh_e is None:
                desc_problems.append((domain, key, "missing in _zh.json"))
                continue
            if set(zh_e.keys()) != set(entry.keys()):
                desc_problems.append((domain, key, "EN/ZH schema mismatch"))
            if not (zh_e.get("description") or "").strip():
                desc_problems.append((domain, key, "ZH description empty"))
            if domain == "monsters":
                zh_moves = zh_e.get("moves") or {}
                for mk, mv in (entry.get("moves") or {}).items():
                    if not (mv.get("description") or "").strip():
                        desc_problems.append((domain, f"{key}.moves.{mk}",
                                              "move EN description empty"))
                    zmv = zh_moves.get(mk)
                    if isinstance(zmv, dict) and not (zmv.get("description") or "").strip():
                        desc_problems.append((domain, f"{key}.moves.{mk}",
                                              "move ZH description empty"))
            if domain == "events":
                zh_opts = zh_e.get("options") or {}
                for ok, ov in (entry.get("options") or {}).items():
                    if not (ov.get("description") or "").strip():
                        desc_problems.append((domain, f"{key}.options.{ok}",
                                              "option EN description empty"))
                    zov = zh_opts.get(ok)
                    if isinstance(zov, dict) and not (zov.get("description") or "").strip():
                        desc_problems.append((domain, f"{key}.options.{ok}",
                                              "option ZH description empty"))

    print("== live-id coverage ==")
    total = sum(len(live_ids.get(d) or []) for d in HARD_CENSUS_DOMAINS)
    print(f"hard-domain live ids: {total}; misses: {len(misses)}")
    if misses:
        print("\nMISSING-ID TABLE (live id -> not resolvable in spirectl_lib/data/*.json)")
        print(f"{'domain':<20} live_id")
        for domain, lid in misses:
            print(f"{domain:<20} {lid}")
    if soft_misses:
        print(f"\nsoft misses (report-only): {len(soft_misses)}")
        for domain, lid in soft_misses[:40]:
            print(f"  {domain:<20} {lid}")
        if len(soft_misses) > 40:
            print(f"  ... {len(soft_misses) - 40} more")

    print("\n== entry counts (EN) ==")
    for domain in DOMAINS:
        entries = all_en.get(domain) or {}
        zh_entries = all_zh.get(domain) or {}
        print(f"  {domain:<14} EN={len(entries):<5} ZH={len(zh_entries):<5}")

    print("\n== EN name CJK leakage ==")
    print(f"count: {len(cjk_name_problems)}")
    for domain, key, name in cjk_name_problems[:40]:
        print(f"  {domain:<14} {key:<40} name={name!r}")

    print("\n== description problems ==")
    print(f"hard: {len(desc_problems)}")
    for domain, key, msg in desc_problems[:60]:
        print(f"  {domain:<14} {key:<48} {msg}")
    if len(desc_problems) > 60:
        print(f"  ... {len(desc_problems) - 60} more")

    ok = not misses and not desc_problems and not cjk_name_problems
    print("\n--check:", "PASS" if ok else "FAIL")
    return 0 if ok else 1
