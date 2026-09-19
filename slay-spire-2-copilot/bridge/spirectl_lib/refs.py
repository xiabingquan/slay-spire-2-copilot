"""JSON reference DB lookup (spirectl_lib/data/*.json) and spire-codex.com research.

Store schema: envelope {id, kind, name, aliases, detail} — purely
programmatic; see spirectl_lib/schema.py for the strict per-kind detail
shapes. Research folds write STRUCTURE from codex only; prose lives in
memory/lessons.
"""
import copy
import json
import re
import sys

from .config import CODEX_API, CODEX_BASE, REF_DIR
from .schema import KIND_TO_DETAIL, NESTED_FLAT, DOMAIN_DEFAULT_KIND, _keyset

# Domain priority for bare-key resolution (first match wins; --all overrides).
REF_DOMAIN_FILES = [
    ("move", "monsters"),
    ("power", "powers"),
    ("relic", "relics"),
    ("card", "cards"),
    ("potion", "potions"),
    ("event_option", "events"),
    ("event", "events"),
    ("affliction", "afflictions"),
    ("status_card", "afflictions"),
    ("intent_class", "intents"),
    ("intent_type", "intents"),
    ("character", "characters"),
    ("monster", "monsters"),
]
KIND_TO_API_PLURAL = {
    "monster": "monsters", "move": "monsters", "relic": "relics",
    "card": "cards", "potion": "potions", "power": "powers",
    "event": "events", "event_option": "events", "character": "characters",
}
_REF_INDEX_CACHE = {}
_CODEX_API_CACHE = {}
_CODEX_MOVE_INDEX = None


def _read_json_dict(path):
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def _write_json_dict(path, data):
    REF_DIR.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_reference_index(lang="en"):
    """Load spirectl_lib/data/*.json into {key: (domain, entry)}.

    Registers envelope keys/aliases plus nested detail.moves / detail.options
    records. Cached per lang.
    """
    if lang in _REF_INDEX_CACHE:
        return _REF_INDEX_CACHE[lang]
    index = {}
    suffix = "_zh.json" if lang == "zh" else ".json"
    if not REF_DIR.is_dir():
        print(f"lookup: reference dir missing: {REF_DIR} — data lives at spirectl_lib/data", file=sys.stderr)
        _REF_INDEX_CACHE[lang] = index
        return index

    def reg(key, domain, entry):
        if key and isinstance(key, str) and key not in index:
            index[key] = (domain, entry)

    for domain, stem in REF_DOMAIN_FILES:
        data = _read_json_dict(REF_DIR / f"{stem}{suffix}")
        for key, entry in data.items():
            if not isinstance(entry, dict):
                continue
            kind = entry.get("kind") or DOMAIN_DEFAULT_KIND.get(stem, domain)
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
    _REF_INDEX_CACHE[lang] = index
    return index


def lookup_reference(key, lang="en", domain=None, match_all=False):
    """Resolve a live game id against the JSON store.

    Resolution ladder: exact key -> prefix before '.pages.' / first dot ->
    case-insensitive -> suffix probes. Returns list of (domain, entry);
    empty list = loud miss.
    """
    if not key:
        return []
    index = load_reference_index(lang)
    candidates = []
    seen = set()

    def consider(k):
        if not k or not isinstance(k, str) or k in seen:
            return
        seen.add(k)
        hit = index.get(k)
        if hit is None:
            return
        if domain and hit[0] != domain and not hit[0].startswith(domain):
            return
        candidates.append(hit)

    consider(key)
    if ".pages." in key:
        consider(key.split(".pages.", 1)[0])
    if "." in key:
        consider(key.split(".")[0])
    if not candidates:
        lowered = key.lower()
        for k in index:
            if k.lower() == lowered:
                consider(k)
    if not candidates and key.endswith("+"):
        consider(key[:-1])
    if not candidates and key.startswith("STRIKE"):
        for k in index:
            if k.startswith("STRIKE"):
                consider(k)
    if not candidates and not domain:
        for k in index:
            if k.endswith(key) or key.endswith(k):
                consider(k)
                if not match_all and candidates:
                    break
    return candidates if match_all else candidates[:1]


def codex_api_get(path, timeout=10.0):
    """GET a spire-codex.com API path, return parsed JSON or None (memory cache)."""
    if path in _CODEX_API_CACHE:
        return _CODEX_API_CACHE[path]
    import urllib.request
    req = urllib.request.Request(
        CODEX_API + path,
        headers={"User-Agent": "spirectl-lookup/0.2 (+spire-copilot-bridge)",
                 "Accept": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8", errors="replace"))
    except Exception:
        return None
    if isinstance(data, dict) and data.get("detail") and len(data) == 1:
        return None
    _CODEX_API_CACHE[path] = data
    return data


def codex_move_index():
    """Build {move_id: monster_dict} from /api/monsters (both id shapes)."""
    global _CODEX_MOVE_INDEX
    if _CODEX_MOVE_INDEX is not None:
        return _CODEX_MOVE_INDEX
    index = {}
    data = codex_api_get("/monsters")
    if isinstance(data, list):
        for monster in data:
            if not isinstance(monster, dict):
                continue
            for move in monster.get("moves") or []:
                if isinstance(move, dict) and move.get("id"):
                    index[move["id"]] = monster
                    index[f"{move['id']}_MOVE"] = monster
    _CODEX_MOVE_INDEX = index
    return index


def codex_search(kind_path, query, timeout=10.0):
    import urllib.parse
    data = codex_api_get(f"/{kind_path}?search={urllib.parse.quote(query)}", timeout=timeout)
    return data if isinstance(data, list) else []


def _empty(value_type):
    return [] if value_type == list else ({} if value_type == dict else
            (False if value_type == bool else None))


def new_entry(kind, key, name=None, aliases=None):
    """Construct a schema-valid empty entry for the given kind."""
    aliases = [a for a in (aliases or []) if a]
    if kind in NESTED_FLAT:
        req = _keyset(NESTED_FLAT[kind])
        flat = {}
        for f in req:
            if f == "id": flat[f] = key
            elif f == "kind": flat[f] = kind
            elif f == "name": flat[f] = name or key
            elif f == "aliases": flat[f] = aliases
            else:
                t = NESTED_FLAT[kind].__dataclass_fields__[f].type
                flat[f] = [] if f == "intents" else None
        return flat
    dcls = KIND_TO_DETAIL.get(kind)
    detail = {}
    if dcls is not None:
        for f in _keyset(dcls):
            fname = f
            if fname in ("hp",):
                detail[fname] = {"min": None, "max": None, "min_asc": None, "max_asc": None}
            elif fname in ("moves", "options"):
                detail[fname] = {}
            elif fname in ("acts", "passives", "display_names", "keywords",
                           "affliction_keys", "member_classes", "cycle"):
                detail[fname] = []
            elif fname in ("is_boss", "is_elite", "counter_class", "host_of_affliction"):
                detail[fname] = False
            else:
                detail[fname] = None
    return {"id": key, "kind": kind, "name": name or key, "aliases": aliases, "detail": detail}


def move_entry(key, monster_id, name=None, aliases=None, intents=None,
               base_damage=None, base_damage_ascension=None, hits=None):
    return {
        "id": key, "kind": "move", "name": name or key,
        "aliases": [a for a in (aliases or []) if a and a != key],
        "monster_id": monster_id, "intents": intents or [],
        "base_damage": base_damage, "base_damage_ascension": base_damage_ascension,
        "hits": hits, "follow_up_id": None, "status_count": None,
    }


def fold_entry_into_reference(domain_stem, key, entry):
    """Persist one entry; existing keys are preserved (fill-only on detail)."""
    kind = entry.get("kind") or DOMAIN_DEFAULT_KIND.get(domain_stem, "relic")
    suffixes = ("_zh.json", ".json")
    for lang in ("zh", "en"):
        path = REF_DIR / f"{domain_stem}{'_zh' if lang == 'zh' else ''}.json"
        data = _read_json_dict(path)
        if key in data and isinstance(data[key], dict):
            cur = data[key]
            # fill-only: missing detail fields, never overwrite present values
            det = cur.get("detail") if isinstance(cur.get("detail"), dict) else {}
            new_det = entry.get("detail") or {}
            for fk, fv in new_det.items():
                if fk not in det or det[fk] in (None, "", [], {}):
                    det[fk] = copy.deepcopy(fv)
            if isinstance(cur.get("detail"), dict) or det:
                cur["detail"] = det
            merged_al = set(cur.get("aliases") or []) | set(entry.get("aliases") or [])
            cur["aliases"] = sorted(a for a in merged_al if a)
        else:
            data[key] = copy.deepcopy(entry)
            if lang == "zh":
                # ZH twin starts as an EN-name placeholder
                pass
        _write_json_dict(path, data)
    _REF_INDEX_CACHE.clear()
    return REF_DIR / f"{domain_stem}.json", True


def _fold_monster(entry):
    """Persist a monster entry (EN+ZH), fill-only on existing keys."""
    key = entry.get("id") or ""
    fold_entry_into_reference("monsters", key, entry)
    return entry


def _codex_move_struct(api_mid, mon_id, mv):
    live = api_mid if str(api_mid).endswith("_MOVE") else (f"{api_mid}_MOVE" if api_mid else "")
    if not live:
        return None, None
    dmg = mv.get("damage") if isinstance(mv.get("damage"), dict) else {}
    nd, asc, hits = dmg.get("normal"), dmg.get("ascension"), dmg.get("hit_count")
    intent = mv.get("intent")
    intents = []
    if intent:
        cmap = {"Attack": "SingleAttackIntent" if not (hits and hits > 1) else "MultiAttackIntent",
                "Buff": "BuffIntent", "Debuff": "DebuffIntent", "Defend": "DefendIntent",
                "Heal": "HealIntent", "Sleep": "SleepIntent", "Stun": "StunIntent",
                "Summon": "SummonIntent", "Status": "StatusIntent"}
        cls = cmap.get(intent)
        if cls:
            it = {"class": cls, "type": "Attack" if "Attack" in cls else intent}
            if nd is not None:
                it.update({"base_damage": nd, "hits": hits or 1})
                if asc is not None:
                    it["base_damage_ascension"] = asc
            intents.append(it)
    return live, move_entry(live, mon_id, name=mv.get("name") or live,
                            aliases=[api_mid] if api_mid and api_mid != live else [],
                            intents=intents, base_damage=nd,
                            base_damage_ascension=asc, hits=hits)


def codex_fill_monster(target_key, detail_data):
    """Merge codex monster structure into store under target_key."""
    api_id = (detail_data or {}).get("id") or target_key
    entry = new_entry("monster", target_key, name=(detail_data or {}).get("name") or target_key,
                      aliases=[a for a in {api_id, (detail_data or {}).get("name")} if a])
    det = entry["detail"]
    if detail_data.get("min_hp") is not None:
        det["hp"] = {"min": detail_data.get("min_hp"), "max": detail_data.get("max_hp"),
                     "min_asc": detail_data.get("min_hp_ascension"),
                     "max_asc": detail_data.get("max_hp_ascension")}
    typ = str(detail_data.get("type") or "").lower()
    det["type"] = str(detail_data.get("type") or "")
    det["is_boss"] = typ == "boss"
    det["is_elite"] = typ == "elite"
    cycle = []
    for mv in detail_data.get("moves") or []:
        live, ment = _codex_move_struct(mv.get("id") or "", target_key, mv)
        if live and ment:
            det["moves"][live] = ment
            cycle.append(live)
    det["cycle"] = cycle[:12]
    _fold_monster(entry)
    return entry


def codex_fill_flat(domain_stem, kind, key, data):
    """Merge codex structured fields into a card/relic/power/potion/event/character."""
    entry = new_entry(kind, key, name=(data or {}).get("name") or key,
                      aliases=[a for a in {key, (data or {}).get("id"), (data or {}).get("name")} if a])
    det = entry["detail"]
    if kind == "relic" or kind == "enchant":
        if data.get("rarity_key") or data.get("rarity"): det["rarity"] = data.get("rarity_key") or data.get("rarity")
        if data.get("pool"): det["character"] = data.get("pool")
    elif kind == "card":
        if data.get("cost") is not None: det["cost"] = data.get("cost")
        if data.get("type_key") or data.get("type"): det["card_type"] = data.get("type_key") or data.get("type")
        if data.get("rarity_key") or data.get("rarity"): det["rarity"] = data.get("rarity_key") or data.get("rarity")
        if data.get("target"): det["target_type"] = data.get("target")
        if data.get("color"): det["character_pool"] = data.get("color")
    elif kind == "power":
        if data.get("type"): det["power_type"] = data.get("type")
        if data.get("stack_type"): det["stack_type"] = data.get("stack_type")
        det["counter_class"] = (data.get("stack_type") == "Counter")
    elif kind == "potion":
        if data.get("rarity_key") or data.get("rarity"): det["rarity"] = data.get("rarity_key") or data.get("rarity")
        if data.get("target"): det["target"] = data.get("target")
        if data.get("usage"): det["usage"] = data.get("usage")
    elif kind == "character":
        if data.get("starting_hp") is not None: det["hp"] = data.get("starting_hp")
        if data.get("starting_gold") is not None: det["gold"] = data.get("starting_gold")
    fold_entry_into_reference(domain_stem, key, entry)
    return entry


def research_and_fold(key, domain_guess=None):
    """Lookup-miss fallback: spire-codex.com API structure first, HTML last.

    Returns (entry, source_url) when research produced data, else (None, None).
    Folds STRUCTURE only (no prose) under the live id key; both key shapes
    land in aliases.
    """
    kind = domain_guess
    entry = None
    source = None

    if kind == "move" or "_MOVE" in key:
        hit_monster = codex_move_index().get(key) or codex_move_index().get(key.replace("_MOVE", ""))
        if hit_monster:
            api_id = hit_monster.get("id") or key
            # move-level miss: fold the host monster structure; entry = the move record
            host_key = api_id
            mon_entry = codex_fill_monster(host_key, hit_monster)
            ment = (mon_entry.get("detail") or {}).get("moves", {}).get(key) or \
                   (mon_entry.get("detail") or {}).get("moves", {}).get(key if key.endswith("_MOVE") else key + "_MOVE")
            if ment:
                entry = ment
                source = f"codex-api:/monsters/{api_id}"
                kind = "move"

    if entry is None:
        attempts = [
            ("monster", lambda k, g: g == "monster" or (g is None and k.isupper()), "monsters", "monster"),
            ("relic", lambda k, g: g in ("relic", None) or k.endswith("_PEARL") or k.isupper(), "relics", "relic"),
            ("card", lambda k, g: g in ("card", None) or k.endswith("_STRIKE") or k.endswith("_IRONCLAD"), "cards", "card"),
            ("potion", lambda k, g: g in ("potion", None) or k.endswith("_POTION") or "POTION" in k, "potions", "potion"),
            ("power", lambda k, g: g in ("power", None), "powers", "power"),
            ("event", lambda k, g: g in ("event", "event_option", None) or ".pages." in k, "events", "event"),
        ]
        for attempt_kind, probe, plural, eff_kind in attempts:
            if not probe(key, kind):
                continue
            queries = [key]
            if attempt_kind == "power" and key.endswith("_POWER"):
                queries.append(key[: -len("_POWER")])
            data = None
            for q in queries:
                data = codex_api_get(f"/{plural}/{q.lower()}")
                if data is not None:
                    break
            if data is None:
                results = codex_search(plural, key.replace("_", " ").lower())
                data = results[0] if results else None
            if isinstance(data, dict) and data.get("id"):
                if attempt_kind == "monster":
                    entry = codex_fill_monster(key, data)
                else:
                    entry = codex_fill_flat(plural, eff_kind, key, data)
                source = f"codex-api:/{plural}/{data.get('id')}"
                kind = eff_kind
                break

    if entry is None:
        # HTML last resort: structure unknown -> record identity-only stub
        urls = codex_candidate_urls(key)
        best_url = None
        for url in urls:
            try:
                probe = fetch_codex_text(url)
            except Exception:
                continue
            if probe and len(probe) >= 80:
                best_url = url
                break
        if not best_url:
            return None, None
        kind_eff = kind or guess_domain(key) or "relic"
        if kind_eff in NESTED_FLAT:
            kind_eff = "monster" if kind_eff == "move" else "event"
        entry = new_entry(kind_eff, key)
        stem = {"monster": "monsters", "move": "monsters", "relic": "relics", "card": "cards",
                "potion": "potions", "power": "powers", "event": "events",
                "event_option": "events", "character": "characters",
                "affliction": "afflictions", "curse": "afflictions",
                "status_card": "afflictions", "intent_type": "intents",
                "intent_class": "intents", "enchant": "relics"}.get(kind_eff, "relics")
        fold_entry_into_reference(stem, key, entry)
        source = f"codex-html:{best_url}"
    return entry, source


def plural_of(kind):
    return KIND_TO_API_PLURAL.get(kind, "relics")


def codex_candidate_urls(key):
    """Build spire-codex.com HTML candidate URLs (last-resort fallback)."""
    slug = key.lower().replace(" ", "_")
    candidates = []
    if "_MOVE" in key:
        stem = slug[:-5] if slug.endswith("_move") else slug
        candidates.extend([f"{CODEX_BASE}/monsters/{slug}", f"{CODEX_BASE}/monsters/{stem}"])
    elif key.endswith("_POWER"):
        candidates.append(f"{CODEX_BASE}/powers/{slug}")
    elif key.endswith("_POTION") or "POTION" in key:
        candidates.append(f"{CODEX_BASE}/potions/{slug}")
    elif ".pages." in key:
        candidates.append(f"{CODEX_BASE}/events/{key.split('.pages.', 1)[0].lower()}")
    elif key.isupper() or "_" in key:
        for category in ("relics", "cards", "potions", "powers", "events", "monsters", "characters"):
            candidates.append(f"{CODEX_BASE}/{category}/{slug}")
    else:
        for category in ("reference", "powers", "monsters", "cards"):
            candidates.append(f"{CODEX_BASE}/{category}/{slug}")
    deduped, seen = [], set()
    for url in candidates:
        if url not in seen:
            seen.add(url); deduped.append(url)
    return deduped[:8]


def fetch_codex_text(url, timeout=12.0):
    """Best-effort HTML fetch as plain text (last-resort fallback probe)."""
    import html as html_mod
    import urllib.request
    req = urllib.request.Request(url, headers={"User-Agent": "spirectl-lookup/0.2 (+spire-copilot-bridge)"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        raw = resp.read().decode("utf-8", errors="replace")
    raw = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", " ", raw)
    raw = re.sub(r"(?is)<br\s*/?>|</p>|</div>|</li>|</h[1-6]>", "\n", raw)
    text = re.sub(r"(?s)<[^>]+>", " ", raw)
    text = html_mod.unescape(text)
    text = re.sub(r"[ \t]+", " ", text)
    return re.sub(r"\n\s*\n+", "\n", text).strip()


def print_entry(domain, entry, key, extra=None):
    """Programmatic lookup output: envelope + detail fields (no prose)."""
    print(f"key={entry.get('id') or key} kind={entry.get('kind') or domain} domain={domain}")
    if entry.get("name"):
        print(f"name={entry['name']}")
    if entry.get("aliases"):
        print(f"aliases: {json.dumps(entry['aliases'], ensure_ascii=False)}")
    detail = entry.get("detail")
    if isinstance(detail, dict):
        for k, v in detail.items():
            if v in (None, "", [], {}):
                continue
            print(f"{k}: {json.dumps(v, ensure_ascii=False)}")
    else:
        for k, v in entry.items():
            if k in ("id", "kind", "name", "aliases") or v in (None, "", [], {}):
                continue
            print(f"{k}: {json.dumps(v, ensure_ascii=False)}")
    if extra:
        print(extra)


def guess_domain(key, explicit=None):
    """Infer the reference domain for a lookup miss from key shape."""
    if explicit:
        return explicit
    if key.endswith("_MOVE") or "_MOVE_" in key:
        return "move"
    if key.endswith("_POWER"):
        return "power"
    if key.endswith("_POTION"):
        return "potion"
    if ".pages." in key:
        return "event_option"
    if key.endswith("_CURSE"):
        return "affliction"
    return None
