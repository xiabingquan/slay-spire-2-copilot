"""Strict entry schema for spirectl_lib/data JSON store.

Positioning: the store is purely programmatic — humans never read these
files. Prose (descriptions, play notes, live notes) lives in memory/lessons
and run notes, not here.

Every top-level entry: envelope + `detail` (shape keyed by entry kind).
EN and ZH twins differ ONLY in `name`; `id`/`kind`/`aliases`/`detail` are
identical. Nested move / event_option records are flat.

Validation is strict — no defaults, no silent fills:
- envelope key set is exactly {id, kind, name, aliases, detail}
- detail key set is exactly the kind's schema key set
- nested records match their flat schema exactly
- light type checks per field; missing/extra/mistyped = violation

`--check` hard-fails on any violation; spirectl lookup reports per-entry
schema errors fail-loud instead of guessing.
"""
from dataclasses import dataclass, fields

ENVELOPE_KEYS = ("id", "kind", "name", "aliases", "detail")


@dataclass
class MoveEntry:
    """Flat record nested under monster detail.moves."""
    id: str
    kind: str
    name: str
    aliases: list
    monster_id: str
    intents: list
    base_damage: object
    base_damage_ascension: object
    hits: object
    follow_up_id: object
    status_count: object


@dataclass
class EventOptionEntry:
    """Flat record nested under event detail.options."""
    id: str
    kind: str
    name: str
    aliases: list
    event_id: str
    page: str


@dataclass
class MonsterDetail:
    hp: dict                      # {min, max, min_asc, max_asc} — all nullable
    acts: list
    is_boss: bool
    is_elite: bool
    cycle: list
    moves: dict                   # {move_id: MoveEntry}
    passives: list
    display_names: list
    type: str


@dataclass
class CardDetail:
    cost: object
    card_type: str
    rarity: str
    target_type: object
    character_pool: str
    keywords: list


@dataclass
class RelicDetail:
    rarity: str
    character: str
    counter_shown: object


@dataclass
class PowerDetail:
    power_type: str
    stack_type: str
    counter_class: bool
    host_of_affliction: bool
    affliction_keys: list


@dataclass
class PotionDetail:
    rarity: str
    target: str
    usage: str


@dataclass
class AfflictionDetail:
    host_power_id: object


@dataclass
class IntentTypeDetail:
    member_classes: list


@dataclass
class IntentClassDetail:
    intent_type: str


@dataclass
class CharacterDetail:
    hp: object
    gold: object
    card_pool: str
    starter_relic: str
    unlocks_after_run_as: str


@dataclass
class EventDetail:
    acts: list
    options: dict                 # {textKey: EventOptionEntry}


KIND_TO_DETAIL = {
    "monster": MonsterDetail,
    "card": CardDetail,
    "relic": RelicDetail,
    "enchant": RelicDetail,
    "power": PowerDetail,
    "potion": PotionDetail,
    "affliction": AfflictionDetail,
    "curse": AfflictionDetail,
    "status_card": AfflictionDetail,
    "intent_type": IntentTypeDetail,
    "intent_class": IntentClassDetail,
    "character": CharacterDetail,
    "event": EventDetail,
}

NESTED_FLAT = {"move": MoveEntry, "event_option": EventOptionEntry}

DOMAIN_DEFAULT_KIND = {
    "characters": "character", "cards": "card", "powers": "power",
    "relics": "relic", "potions": "potion", "afflictions": "affliction",
    "intents": "intent_type", "monsters": "monster", "events": "event",
}

# light type gate: field -> allowed python types (None allowed everywhere;
# nested dicts/lists validated structurally elsewhere)
_TYPE = {
    "id": (str,), "kind": (str,), "name": (str,), "aliases": (list,),
    "monster_id": (str,), "intents": (list,), "follow_up_id": (str,),
    "event_id": (str,), "page": (str,), "hp": (dict,), "acts": (list,),
    "is_boss": (bool,), "is_elite": (bool,), "cycle": (list,), "moves": (dict,),
    "passives": (list,), "display_names": (list,), "type": (str,),
    "card_type": (str,), "rarity": (str,), "character_pool": (str,),
    "keywords": (list,), "character": (str,), "power_type": (str,),
    "stack_type": (str,), "counter_class": (bool,), "host_of_affliction": (bool,),
    "affliction_keys": (list,), "target": (str,), "usage": (str,),
    "member_classes": (list,), "card_pool": (str,), "starter_relic": (str,),
    "unlocks_after_run_as": (str,), "options": (dict,), "intent_type": (str,),
}


def _keyset(cls):
    return {f.name for f in fields(cls)}


def _type_errs(key, value):
    if value is None:
        return []
    allowed = _TYPE.get(key)
    if allowed and not isinstance(value, allowed):
        return [f"{key}: type {type(value).__name__} not in {allowed}"]
    return []


def _flat_violations(entry, cls):
    errs = []
    if not isinstance(entry, dict):
        return ["not a dict"]
    req = _keyset(cls)
    for k in req:
        if k not in entry:
            errs.append(f"missing {k}")
    for k in entry:
        if k not in req:
            errs.append(f"extra key {k}")
    for k, v in (entry.items() if isinstance(entry, dict) else []):
        if k in req:
            errs.extend(_type_errs(k, v))
    return errs


def entry_violations(entry) -> list:
    """Strict schema violations for one top-level entry (empty list = valid)."""
    errs = []
    if not isinstance(entry, dict):
        return ["entry not a dict"]
    for k in ENVELOPE_KEYS:
        if k not in entry:
            errs.append(f"envelope missing {k}")
    for k in entry:
        if k not in ENVELOPE_KEYS:
            errs.append(f"top-level extra key {k}")
    for k in ("id", "kind", "name"):
        errs.extend(_type_errs(k, entry.get(k)))
    errs.extend(_type_errs("aliases", entry.get("aliases")))
    kind = entry.get("kind") or ""
    if kind in NESTED_FLAT:
        # top-level move/event_option entries are flat records — no detail key
        return _flat_violations(entry, NESTED_FLAT[kind])
    dcls = KIND_TO_DETAIL.get(kind)
    if dcls is None:
        errs.append(f"unknown kind {kind!r}")
        return errs
    detail = entry.get("detail")
    if not isinstance(detail, dict):
        errs.append("detail missing or not a dict")
        return errs
    req = _keyset(dcls)
    for k in req:
        if k not in detail:
            errs.append(f"detail missing {k}")
    for k in detail:
        if k not in req:
            errs.append(f"detail extra key {k}")
    for k, v in detail.items():
        if k in req:
            errs.extend(f"detail.{e}" for e in _type_errs(k, v))
    if kind == "monster":
        hp = detail.get("hp")
        if isinstance(hp, dict):
            for hk in hp:
                if hk not in ("min", "max", "min_asc", "max_asc"):
                    errs.append(f"detail.hp extra key {hk}")
            for hk in ("min", "max", "min_asc", "max_asc"):
                if hk not in hp:
                    errs.append(f"detail.hp missing {hk}")
        for mk, mv in (detail.get("moves") or {}).items():
            for e in _flat_violations(mv, MoveEntry):
                errs.append(f"moves.{mk}: {e}")
    if kind == "event":
        for ok, ov in (detail.get("options") or {}).items():
            for e in _flat_violations(ov, EventOptionEntry):
                errs.append(f"options.{ok}: {e}")
    return errs
