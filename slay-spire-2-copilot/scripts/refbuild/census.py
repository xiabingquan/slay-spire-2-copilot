"""Live-id coverage gate (--check): census resolution + entry quality checks.

Exits nonzero when: (1) any hard-domain live id from the census does not
resolve in the flattened index (top-level keys + aliases + monster moves +
event options); (2) any entry lacks a non-empty EN description, or (except
needs_zh:true) a non-empty ZH description; (3) an EN name field leaks CJK.
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
            if not (zh_e.get("description") or "").strip():
                if zh_e.get("needs_zh"):
                    desc_problems.append((domain, key, "needs_zh:true (ZH empty)"))
                else:
                    desc_problems.append((domain, key, "ZH description empty"))
            if domain == "monsters":
                for mk, mv in (entry.get("moves") or {}).items():
                    if not (mv.get("description") or "").strip():
                        desc_problems.append((domain, f"{key}.moves.{mk}",
                                              "move EN description empty"))
            if domain == "events":
                for ok, ov in (entry.get("options") or {}).items():
                    if not (ov.get("description") or "").strip():
                        desc_problems.append((domain, f"{key}.options.{ok}",
                                              "option EN description empty"))

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
    needs_zh_report = []
    for domain in DOMAINS:
        entries = all_en.get(domain) or {}
        zh_entries = all_zh.get(domain) or {}
        needs = [k for k, e in zh_entries.items() if e.get("needs_zh")]
        needs_zh_report.extend((domain, k) for k in needs)
        print(f"  {domain:<14} EN={len(entries):<5} ZH={len(zh_entries):<5} "
              f"needs_zh={len(needs)}")

    print("\n== EN name CJK leakage ==")
    print(f"count: {len(cjk_name_problems)}")
    for domain, key, name in cjk_name_problems[:40]:
        print(f"  {domain:<14} {key:<40} name={name!r}")

    print("\n== description problems ==")
    hard_desc = [p for p in desc_problems if not p[2].startswith("needs_zh:true")]
    needs_zh_desc = [p for p in desc_problems if p[2].startswith("needs_zh:true")]
    print(f"hard: {len(hard_desc)}; needs_zh flags: {len(needs_zh_desc)}")
    for domain, key, msg in hard_desc[:60]:
        print(f"  {domain:<14} {key:<48} {msg}")
    if len(hard_desc) > 60:
        print(f"  ... {len(hard_desc) - 60} more")
    if needs_zh_report:
        print("\n== needs_zh:true keys (ZH description falls back to EN) ==")
        for domain, key in needs_zh_report[:80]:
            print(f"  {domain:<14} {key}")
        if len(needs_zh_report) > 80:
            print(f"  ... {len(needs_zh_report) - 80} more")

    ok = not misses and not hard_desc and not cjk_name_problems
    print("\n--check:", "PASS" if ok else "FAIL")
    return 0 if ok else 1
