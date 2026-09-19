"""spire-codex.com API enrichment: cache-first fetches folded into EN entries.

API ids carry no live suffixes (API SEA_KICK = live SEA_KICK_MOVE; API
RAVENOUS = live RAVENOUS_POWER). JSON keys stay in LIVE form; API ids land
in aliases[]. Responses cached under scripts/.cache/codex/ — the JSON DB is
the durable store; the cache is reproducible input.
"""
import json
import re

from .config import CODEX_CACHE
from .data import CREATURE_NAME_TO_KEY
from .merge import envelope
from .textutil import humanize

def _append_source(ent: dict, suffix: str):
    """Append a provenance suffix once; re-runs must stay idempotent."""
    src = ent.get("source") or ""
    if suffix not in src:
        ent["source"] = src + suffix


BBCode_RE = re.compile(r"\[/?[a-zA-Z_]+\]")


def codex_clean(text):
    if not text:
        return text
    return BBCode_RE.sub("", str(text)).strip()


def codex_fetch(kind: str, cid: str, refresh: bool = False):
    """Fetch one codex API payload; per-process cache under scripts/.cache/codex."""
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
        req = urllib.request.Request(
            url, headers={"User-Agent": "SpireBridge-json-pipeline/0.2"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
    except Exception as exc:
        data = {"_error": str(exc)}
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n",
                          encoding="utf-8")
    time.sleep(0.2)
    return data


def codex_probe_ids(kind: str, live_id: str):
    """Candidate API ids for a live id (suffix-stripped probes)."""
    cands = [live_id]
    if kind == "powers" and live_id.endswith("_POWER"):
        cands.append(live_id[: -len("_POWER")])
    if kind == "monsters":
        cands.append(live_id)
    return cands


def fold_codex(all_en: dict, live_ids: dict, refresh: bool = False) -> int:
    """Fold codex API facts into EN entries. Returns fetch-hit count."""
    hits = 0
    # --- powers: live RAVENOUS_POWER <- API RAVENOUS
    for pid in live_ids.get("power_ids") or []:
        for cand in codex_probe_ids("powers", pid):
            data = codex_fetch("powers", cand, refresh)
            if data.get("_error"):
                continue
            hits += 1
            ent = all_en["powers"].get(pid)
            if ent is None:
                continue
            ent.setdefault("aliases", [])
            if data.get("id") and data["id"] not in ent["aliases"] \
                    and data["id"] != pid:
                ent["aliases"] = sorted(set(ent["aliases"]) | {data["id"]})
            desc = codex_clean(data.get("description"))
            if desc and (len(ent.get("description") or "") < 40
                         or not ent.get("description")):
                ent["description"] = desc
                _append_source(ent, f"; codex:powers/{cand}")
            if data.get("type") and not ent.get("power_type"):
                ent["power_type"] = data["type"]
            break
    # --- relics / potions / cards / events / characters: same-id probes
    for domain, kind, id_list in [
        ("relics", "relics", live_ids.get("relic_ids")),
        ("potions", "potions", live_ids.get("potion_ids")),
        ("cards", "cards", list(dict.fromkeys(
            (live_ids.get("card_ids") or []) + (live_ids.get("card_option_ids") or [])))),
        ("events", "events", live_ids.get("event_ids")),
        ("characters", "characters", ["IRONCLAD", "SILENT", "DEFECT",
                                      "NECROBINDER", "REGENT"]),
    ]:
        for lid in id_list or []:
            if not lid or not re.match(r"^[A-Z][A-Z0-9_]+$", lid):
                continue
            data = codex_fetch(kind, lid, refresh)
            if data.get("_error"):
                continue
            hits += 1
            ent = all_en[domain].get(lid)
            if ent is None:
                continue
            desc = codex_clean(data.get("description"))
            if desc and len(ent.get("description") or "") < 40:
                ent["description"] = desc
                _append_source(ent, f"; codex:{kind}/{lid}")
            if domain == "cards" and data.get("cost") is not None \
                    and ent.get("cost") is None:
                ent["cost"] = str(data["cost"])
            if domain == "relics" and data.get("rarity_key") and not ent.get("rarity"):
                ent["rarity"] = data["rarity_key"]
            if domain == "potions" and data.get("rarity_key") and not ent.get("rarity"):
                ent["rarity"] = data["rarity_key"]
            if domain == "characters":
                if data.get("starting_hp") and not ent.get("hp"):
                    ent["hp"] = data["starting_hp"]
                if data.get("description") and len(ent.get("description") or "") < 40:
                    ent["description"] = codex_clean(data["description"])
    # --- monsters: fold structured hp/moves; keys stay LIVE-shaped
    monster_probe_ids = set()
    for key in (all_en.get("monsters") or {}):
        if re.match(r"^[A-Z][A-Z0-9_]+$", key):
            monster_probe_ids.add(key)
    for zh_name, key in CREATURE_NAME_TO_KEY.items():
        monster_probe_ids.add(key)
    monster_probe_ids |= {"SEAPUNK", "CORPSE_SLUG", "CALCIFIED_CULTIST",
                          "CULTIST", "CorpseSlug"}
    for mid in sorted(monster_probe_ids):
        data = codex_fetch("monsters", mid, refresh)
        if data.get("_error"):
            continue
        hits += 1
        api_id = data.get("id") or mid
        # canonical key: live-shaped entry key — prefer existing entry whose id
        # or aliases carry the api id / the probe id
        target_key = None
        for key, ent in (all_en.get("monsters") or {}).items():
            if key == api_id or key == mid or api_id in (ent.get("aliases") or []) \
                    or mid in (ent.get("aliases") or []):
                target_key = key
                break
        if target_key is None:
            target_key = api_id
        mon = all_en["monsters"].get(target_key)
        if mon is None:
            mon = envelope(
                target_key, "monster", data.get("name") or target_key,
                codex_clean(data.get("description")) or
                f"Monster {data.get('name', target_key)} — codex {api_id}.",
                aliases=[api_id, data.get("name")] if api_id else [],
                source=f"codex:monsters/{api_id}",
                acts=[], hp={"base": None, "notes": None},
                is_boss=str(data.get("type", "")).lower() == "boss",
                passives=[], cycle=[], moves={},
            )
            all_en["monsters"][target_key] = mon
        mon.setdefault("aliases", [])
        for a in {api_id, data.get("name"), mid} - {None, target_key}:
            if a not in mon["aliases"]:
                mon["aliases"] = sorted(set(mon["aliases"]) | {a})
        min_hp, max_hp = data.get("min_hp"), data.get("max_hp")
        amin, amax = data.get("min_hp_ascension"), data.get("max_hp_ascension")
        if min_hp:
            notes = f"{min_hp}-{max_hp} HP"
            if amin:
                notes += f"; A: {amin}-{amax}"
            mon["hp"] = {"base": min_hp, "notes": notes}
        if str(data.get("type", "")).lower() == "boss":
            mon["is_boss"] = True
        moves = dict(mon.get("moves") or {})
        cycle = list(mon.get("cycle") or [])
        for mv in data.get("moves") or []:
            api_mid = mv.get("id") or ""
            live_mid = api_mid if api_mid.endswith("_MOVE") or api_mid == "STUNNED" \
                else (api_mid + "_MOVE" if api_mid else "")
            if not live_mid:
                continue
            dmg = mv.get("damage") or {}
            norm, asc, hits_n = dmg.get("normal"), dmg.get("ascension"), \
                dmg.get("hit_count")
            intent = mv.get("intent")
            effect_bits = [f"codex: {mv.get('name', api_mid)}"]
            if intent:
                effect_bits.append(f"intent={intent}")
            if norm is not None:
                if hits_n and hits_n > 1:
                    effect_bits.append(f"damage {norm}x{hits_n}"
                                       + (f" (A:{asc})" if asc else ""))
                else:
                    effect_bits.append(f"damage {norm}"
                                       + (f" (A:{asc})" if asc else ""))
            if mv.get("block"):
                effect_bits.append(f"block {mv['block']}")
            if mv.get("heal"):
                effect_bits.append(f"heal {mv['heal']}")
            if mv.get("powers"):
                effect_bits.append(f"powers {mv['powers']}")
            codex_desc = "; ".join(effect_bits)
            prev = moves.get(live_mid)
            intents = []
            if intent:
                cls_map = {"Attack": "SingleAttackIntent" if not (hits_n and hits_n > 1)
                           else "MultiAttackIntent",
                           "Buff": "BuffIntent", "Debuff": "DebuffIntent",
                           "Defend": "DefendIntent", "Heal": "HealIntent",
                           "Sleep": "SleepIntent", "Stun": "StunIntent",
                           "Summon": "SummonIntent", "Status": "StatusIntent",
                           "Unknown": "UnknownIntent"}
                cls = cls_map.get(intent)
                if cls:
                    entry_i = {"class": cls,
                               "type": "Attack" if "Attack" in cls else intent}
                    if norm is not None:
                        entry_i["base_damage"] = norm
                        entry_i["hits"] = hits_n or 1
                        if asc is not None:
                            entry_i["base_damage_ascension"] = asc
                    intents.append(entry_i)
            if prev is None:
                moves[live_mid] = envelope(
                    live_mid, "move", mv.get("name") or humanize(api_mid),
                    codex_desc,
                    aliases=[api_mid] if api_mid and api_mid != live_mid else [],
                    source=f"codex:monsters/{api_id} move {api_mid}",
                    monster_id=target_key, intents=intents,
                    base_damage=norm,
                    base_damage_ascension=asc,
                    hits=hits_n, status_count=None,
                    display_note=(f"{norm}x{hits_n}" if hits_n and hits_n > 1
                                  else (str(norm) if norm is not None else None)),
                )
            else:
                if api_mid and api_mid not in (prev.get("aliases") or []) \
                        and api_mid != live_mid:
                    prev["aliases"] = sorted(set(prev.get("aliases") or [])
                                             | {api_mid})
                # Thin md fragments -> replace with codex numbers, keeping the
                # archive text once. Codex-born stubs (startswith "codex:") are
                # never re-wrapped — re-wrapping them grew "| archive:" chains
                # on every build and broke idempotency.
                prev_desc = prev.get("description") or ""
                thin = len(prev_desc) < 40 or prev_desc.strip().endswith("→") \
                    or prev_desc.strip().startswith("(")
                if thin and codex_desc and not prev_desc.startswith("codex:"):
                    prev["description"] = codex_desc + (
                        f" | archive: {prev_desc}" if prev_desc.strip() else "")
                    _append_source(prev, f"; codex:monsters/{api_id}")
                # numeric fills are independent of the description branch —
                # applying both in one pass keeps re-runs idempotent
                if norm is not None and prev.get("base_damage") is None:
                    prev["base_damage"] = norm
                    prev["base_damage_ascension"] = asc
                    prev["hits"] = hits_n
                    if not prev.get("intents"):
                        prev["intents"] = intents
                if mv.get("name") and not prev.get("name"):
                    prev["name"] = mv["name"]
            if live_mid not in cycle and len(cycle) < 12:
                cycle.append(live_mid)
        mon["moves"] = moves
        if cycle and not mon.get("cycle"):
            mon["cycle"] = cycle
        elif cycle:
            merged_cycle = list(dict.fromkeys(list(mon.get("cycle") or []) + cycle))
            mon["cycle"] = merged_cycle[:12]
    return hits
