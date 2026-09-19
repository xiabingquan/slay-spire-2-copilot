"""Coverage + strict-schema gate (--check) for spirectl_lib/data.

Hard-fails when:
1. any hard-domain census live id does not resolve in the flattened index
   (envelope keys/aliases + detail.moves + detail.options);
2. any entry violates the strict schema (spirectl_lib/schema.py) — missing
   or extra keys, mistyped fields — in EN or ZH;
3. twins diverge: top-level key sets, aliases, or detail (nested record
   `name` values may differ per language);
4. an EN name is empty or leaks CJK.
"""
from .config import DOMAINS, HARD_CENSUS_DOMAINS, SOFT_CENSUS_DOMAINS
from spirectl_lib.schema import entry_violations  # noqa: E402
from .textutil import has_cjk
import copy


def flatten_index(all_en: dict) -> dict:
    """Flatten every resolvable key/alias across domains into one index."""
    index = {}

    def reg(key, domain, entry):
        if key and isinstance(key, str):
            index.setdefault(key, []).append((domain, entry))

    for domain, entries in all_en.items():
        for key, entry in entries.items():
            if not isinstance(entry, dict):
                continue
            kind = entry.get("kind") or domain
            reg(key, kind, entry)
            for alias in entry.get("aliases") or []:
                reg(alias, kind, entry)
            detail = entry.get("detail") if isinstance(entry.get("detail"), dict) else {}
            for mk, mv in (detail.get("moves") or {}).items():
                if isinstance(mv, dict):
                    reg(mk, "move", mv)
                    for alias in mv.get("aliases") or []:
                        reg(alias, "move", mv)
            for ok, ov in (detail.get("options") or {}).items():
                if isinstance(ov, dict):
                    reg(ok, "event_option", ov)
                    for alias in ov.get("aliases") or []:
                        reg(alias, "event_option", ov)
    return index


def _strip_nested_names(detail):
    d = copy.deepcopy(detail) if isinstance(detail, dict) else detail
    if isinstance(d, dict):
        for nest in ("moves", "options"):
            for rec in (d.get(nest) or {}).values():
                if isinstance(rec, dict) and "name" in rec:
                    rec["name"] = "<name>"
    return d


def run_check(all_en: dict, all_zh: dict, live_ids: dict) -> int:
    """Run coverage/schema/twin/name gates. 0 = PASS."""
    index = flatten_index(all_en)
    misses = [(d, lid) for d in HARD_CENSUS_DOMAINS
              for lid in (live_ids.get(d) or []) if lid and lid not in index]
    soft = [(d, lid) for d in SOFT_CENSUS_DOMAINS
            for lid in (live_ids.get(d) or []) if lid and lid not in index]

    schema_problems = []
    twin_problems = []
    name_problems = []
    for domain in DOMAINS:
        en = all_en.get(domain) or {}
        zh = all_zh.get(domain) or {}
        if set(en) != set(zh):
            twin_problems.append((domain, "top-level key sets differ",
                                  sorted(set(en) ^ set(zh))[:6]))
        for key, entry in en.items():
            for e in entry_violations(entry):
                schema_problems.append((domain, key, f"EN {e}"))
            if not str(entry.get("name") or "").strip():
                name_problems.append((domain, key, "EN name empty"))
            elif has_cjk(entry.get("name")):
                name_problems.append((domain, key, f"EN name CJK: {entry.get('name')!r}"))
            z = zh.get(key)
            if isinstance(z, dict):
                for e in entry_violations(z):
                    schema_problems.append((domain, key, f"ZH {e}"))
                if not str(z.get("name") or "").strip():
                    name_problems.append((domain, key, "ZH name empty"))
                if isinstance(entry, dict) and isinstance(z, dict):
                    if entry.get("aliases") != z.get("aliases"):
                        twin_problems.append((domain, key, "aliases differ"))
                    if _strip_nested_names(entry.get("detail")) != _strip_nested_names(z.get("detail")):
                        twin_problems.append((domain, key, "detail differs"))
        for key, z in zh.items():
            if key not in en:
                twin_problems.append((domain, key, "ZH-only key"))
            if isinstance(z, dict):
                pass
        # nested extra-key audit inside zh handled via entry_violations above

    print("== live-id coverage ==")
    total = sum(len(live_ids.get(d) or []) for d in HARD_CENSUS_DOMAINS)
    print(f"hard-domain live ids: {total}; misses: {len(misses)}")
    for domain, lid in misses[:40]:
        print(f"  {domain:<20} {lid}")
    if soft:
        print(f"soft misses (report-only): {len(soft)}")
        for domain, lid in soft[:20]:
            print(f"  {domain:<20} {lid}")

    print("\n== entry counts ==")
    for domain in DOMAINS:
        print(f"  {domain:<14} EN={len(all_en.get(domain) or {}):<5} ZH={len(all_zh.get(domain) or {})}")

    print("\n== schema violations (strict, no defaults) ==")
    print(f"count: {len(schema_problems)}")
    for row in schema_problems[:40]:
        print(f"  {row[0]:<12} {row[1][:40]:<40} {row[2]}")
    if len(schema_problems) > 40:
        print(f"  ... {len(schema_problems) - 40} more")

    print("\n== twin divergence ==")
    print(f"count: {len(twin_problems)}")
    for row in twin_problems[:30]:
        print(f"  {row[0]:<12} {str(row[1])[:40]:<40} {row[2]}")

    print("\n== name problems ==")
    print(f"count: {len(name_problems)}")
    for row in name_problems[:20]:
        print(f"  {row[0]:<12} {row[1][:40]:<40} {row[2]}")

    ok = not misses and not schema_problems and not twin_problems and not name_problems
    print("\n--check:", "PASS" if ok else "FAIL")
    return 0 if ok else 1
