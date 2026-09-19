"""spire-codex.com enrichment: structure-only fills into spirectl_lib/data.

Fill-only: missing/empty detail fields and aliases; never touches present
values; never writes prose (descriptions live in memory/lessons). API ids
without live suffixes land in aliases.
"""
import json
import re

from .config import CODEX_CACHE
from .data import CREATURE_NAME_TO_KEY
from spirectl_lib.refs import new_entry, move_entry  # noqa: E402


def codex_fetch(kind: str, cid: str, refresh: bool = False):
    """Fetch one codex API payload; disk cache under scripts/.cache/codex."""
    cache_path = CODEX_CACHE / kind / f"{cid}.json"
    if cache_path.exists() and not refresh:
        try:
            return json.loads(cache_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            pass
    import time
    import urllib.request
    url = f"https://spire-codex.com/api/{kind}/{cid}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "SpireBridge-json-pipeline/0.2"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
    except Exception as exc:
        data = {"_error": str(exc)}
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    time.sleep(0.2)
    return data


def codex_probe_ids(kind: str, live_id: str):
    cands = [live_id]
    if kind == "powers" and live_id.endswith("_POWER"):
        cands.append(live_id[: -len("_POWER")])
    return cands


def _merge_aliases(entry, *cands):
    al = set(entry.get("aliases") or [])
    for a in cands:
        if a and a != entry.get("id"):
            al.add(a)
    entry["aliases"] = sorted(al)


def _fill(det, key, value):
    if value not in (None, "", [], {}) and det.get(key) in (None, "", [], {}):
        det[key] = value


def fold_codex(all_en: dict, live_ids: dict, refresh: bool = False) -> int:
    """Fold codex STRUCTURE into EN store dicts (fill-only). Returns hit count."""
    hits = 0
    # powers
    for pid in live_ids.get("power_ids") or []:
        for cand in codex_probe_ids("powers", pid):
            data = codex_fetch("powers", cand, refresh)
            if not data or data.get("_error"):
                continue
            hits += 1
            ent = all_en["powers"].get(pid)
            if ent is None:
                continue
            _merge_aliases(ent, data.get("id"), data.get("name"))
            det = ent.setdefault("detail", {})
            _fill(det, "power_type", data.get("type"))
            _fill(det, "stack_type", data.get("stack_type"))
            if data.get("stack_type") == "Counter" and det.get("counter_class") in (None, False):
                det["counter_class"] = True
            break
    # flat domains: same-id probes
    for domain, plural, ids in [
        ("relics", "relics", live_ids.get("relic_ids")),
        ("potions", "potions", live_ids.get("potion_ids")),
        ("cards", "cards", list(dict.fromkeys((live_ids.get("card_ids") or []) + (live_ids.get("card_option_ids") or [])))),
        ("events", "events", live_ids.get("event_ids")),
        ("characters", "characters", ["IRONCLAD", "SILENT", "DEFECT", "NECROBINDER", "REGENT"]),
    ]:
        for lid in ids or []:
            if not lid or not re.match(r"^[A-Z][A-Z0-9_]+$", lid):
                continue
            data = codex_fetch(plural, lid, refresh)
            if not data or data.get("_error"):
                continue
            hits += 1
            ent = all_en[domain].get(lid)
            if ent is None:
                continue
            _merge_aliases(ent, data.get("id"), data.get("name"))
            det = ent.setdefault("detail", {})
            if domain == "relics":
                _fill(det, "rarity", data.get("rarity_key") or data.get("rarity"))
                _fill(det, "character", data.get("pool"))
            elif domain == "potions":
                _fill(det, "rarity", data.get("rarity_key") or data.get("rarity"))
                _fill(det, "target", data.get("target"))
                _fill(det, "usage", data.get("usage"))
            elif domain == "cards":
                _fill(det, "cost", data.get("cost"))
                _fill(det, "card_type", data.get("type_key") or data.get("type"))
                _fill(det, "rarity", data.get("rarity_key") or data.get("rarity"))
                _fill(det, "target_type", data.get("target"))
                _fill(det, "character_pool", data.get("color"))
            elif domain == "characters":
                _fill(det, "hp", data.get("starting_hp"))
                _fill(det, "gold", data.get("starting_gold"))
    # monsters: probe from store keys + display_names + creature map
    probes = set()
    for key, e in (all_en.get("monsters") or {}).items():
        if isinstance(e, dict) and re.match(r"^[A-Za-z][A-Za-z0-9_]*$", key):
            probes.add(key)
        for dn in ((e or {}).get("detail") or {}).get("display_names") or []:
            probes.add(dn)
    for zh_name in CREATURE_NAME_TO_KEY:
        probes.add(zh_name)
    for mid in sorted(p for p in probes if p):
        data = codex_fetch("monsters", mid, refresh)
        if not data or data.get("_error") or not data.get("id"):
            continue
        hits += 1
        api_id = data.get("id")
        target_key = None
        for key, ent in (all_en.get("monsters") or {}).items():
            if not isinstance(ent, dict):
                continue
            al = ent.get("aliases") or []
            if key == api_id or key == mid or api_id in al or mid in al:
                target_key = key
                break
        if target_key is None:
            target_key = api_id
            all_en["monsters"][target_key] = new_entry("monster", target_key,
                                                        name=data.get("name") or target_key)
        ent = all_en["monsters"][target_key]
        _merge_aliases(ent, api_id, data.get("name"), mid)
        det = ent.setdefault("detail", {})
        if data.get("min_hp") is not None and (det.get("hp") or {}).get("min") is None:
            det["hp"] = {"min": data.get("min_hp"), "max": data.get("max_hp"),
                         "min_asc": data.get("min_hp_ascension"),
                         "max_asc": data.get("max_hp_ascension")}
        typ = str(data.get("type") or "").lower()
        _fill(det, "type", data.get("type"))
        if typ == "boss": det["is_boss"] = True
        if typ == "elite": det["is_elite"] = True
        moves = det.setdefault("moves", {})
        cycle = list(det.get("cycle") or [])
        for mv in data.get("moves") or []:
            api_mid = mv.get("id") or ""
            live = api_mid if api_mid.endswith("_MOVE") else (api_mid + "_MOVE" if api_mid else "")
            if not live:
                continue
            dmg = mv.get("damage") if isinstance(mv.get("damage"), dict) else {}
            nd, asc, hits_n = dmg.get("normal"), dmg.get("ascension"), dmg.get("hit_count")
            intent = mv.get("intent")
            intents = []
            if intent:
                cmap = {"Attack": "SingleAttackIntent" if not (hits_n and hits_n > 1) else "MultiAttackIntent",
                        "Buff": "BuffIntent", "Debuff": "DebuffIntent", "Defend": "DefendIntent",
                        "Heal": "HealIntent", "Sleep": "SleepIntent", "Stun": "StunIntent",
                        "Summon": "SummonIntent", "Status": "StatusIntent"}
                cls = cmap.get(intent)
                if cls:
                    it = {"class": cls, "type": "Attack" if "Attack" in cls else intent}
                    if nd is not None:
                        it.update({"base_damage": nd, "hits": hits_n or 1})
                        if asc is not None:
                            it["base_damage_ascension"] = asc
                    intents.append(it)
            cur = moves.get(live)
            if cur is None:
                moves[live] = move_entry(live, target_key, name=mv.get("name") or live,
                                          aliases=[api_mid] if api_mid and api_mid != live else [],
                                          intents=intents, base_damage=nd,
                                          base_damage_ascension=asc, hits=hits_n)
                if live not in cycle and len(cycle) < 12:
                    cycle.append(live)
            else:
                _merge_aliases(cur, api_mid, mv.get("name"))
                _fill(cur, "intents", intents)
                _fill(cur, "base_damage", nd)
                _fill(cur, "base_damage_ascension", asc)
                _fill(cur, "hits", hits_n)
        det["cycle"] = cycle[:12]
    return hits
