"""JSON reference DB lookup (references/game/*.json) and spire-codex.com research."""
import json
import sys

from .config import CODEX_API, CODEX_BASE, REF_DIR
from .textutil import strip_codex_markup

# Domain priority for bare-key resolution (first match wins; --all overrides).
# (domain, file stem) pairs — also the kind->stem map for folding research.
REF_DOMAIN_FILES = [
    ("move", "monsters"),        # flattened from monsters[*].moves[*]
    ("power", "powers"),
    ("relic", "relics"),
    ("card", "cards"),
    ("potion", "potions"),
    ("event_option", "events"),  # flattened from events[*].options[*]
    ("event", "events"),
    ("affliction", "afflictions"),
    ("status_card", "afflictions"),
    ("intent_class", "intents"),
    ("intent_type", "intents"),
    ("character", "characters"),
    ("monster", "monsters"),
]

# spire-codex.com URL patterns: https://spire-codex.com/{category}/{lowercase_id}
# (underscores work unencoded; category chosen by id shape).

_REF_INDEX_CACHE = {}
_CODEX_API_CACHE = {}
_CODEX_MOVE_INDEX = None


def load_reference_index(lang="en"):
    """Load references/game/*.json (or *_zh.json) into {key: (domain, entry)}.

    Flattens nested keys: monsters[*].moves[*] -> move domain,
    events[*].options[*] -> event_option. Registers entry['id'], every
    aliases[] element, and id case-variants. Cached per lang.
    """
    if lang in _REF_INDEX_CACHE:
        return _REF_INDEX_CACHE[lang]
    index = {}
    suffix = "_zh.json" if lang == "zh" else ".json"
    if not REF_DIR.is_dir():
        print(
            f"lookup: reference dir missing: {REF_DIR} — "
            "generate it with scripts/build_game_reference_json.py",
            file=sys.stderr,
        )
        _REF_INDEX_CACHE[lang] = index
        return index

    def register(key, domain, entry):
        if not key or not isinstance(key, str):
            return
        if key not in index:
            index[key] = (domain, entry)

    for domain, stem in REF_DOMAIN_FILES:
        path = REF_DIR / f"{stem}{suffix}"
        if not path.exists():
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            print(f"lookup: failed to read {path.name}: {exc}", file=sys.stderr)
            continue
        if not isinstance(data, dict):
            continue
        for key, entry in data.items():
            if not isinstance(entry, dict):
                continue
            entry_kind = entry.get("kind") or domain
            register(key, entry_kind, entry)
            register(entry.get("id"), entry_kind, entry)
            for alias in entry.get("aliases") or []:
                if isinstance(alias, str):
                    register(alias, entry_kind, entry)
            register(key.upper(), entry_kind, entry)
            moves = entry.get("moves")
            if isinstance(moves, dict):
                for move_key, move_entry in moves.items():
                    if not isinstance(move_entry, dict):
                        continue
                    register(move_key, "move", move_entry)
                    register(move_entry.get("id"), "move", move_entry)
                    for alias in move_entry.get("aliases") or []:
                        if isinstance(alias, str):
                            register(alias, "move", move_entry)
            options = entry.get("options")
            if isinstance(options, dict):
                for opt_key, opt_entry in options.items():
                    if not isinstance(opt_entry, dict):
                        continue
                    register(opt_key, "event_option", opt_entry)
                    register(opt_entry.get("id"), "event_option", opt_entry)
                    for alias in opt_entry.get("aliases") or []:
                        if isinstance(alias, str):
                            register(alias, "event_option", opt_entry)
    _REF_INDEX_CACHE[lang] = index
    return index


def lookup_reference(key, lang="en", domain=None, match_all=False):
    """Resolve a live game id against the JSON reference DB.

    Resolution ladder: exact key -> event textKey / prefix before '.pages.'
    -> case-insensitive -> suffix probes (X+ -> X; STRIKE family).
    Returns list of (domain, entry); empty list = loud miss.
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
    """GET a spire-codex.com API path, return parsed JSON or None.

    Cache-first: every successful payload is kept per-process so a burst of
    lookups on the same monster/index does not re-hit the network.
    """
    if path in _CODEX_API_CACHE:
        return _CODEX_API_CACHE[path]
    import urllib.request

    url = CODEX_API + path
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "spirectl-lookup/0.2 (+spire-copilot-bridge)",
            "Accept": "application/json",
        },
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
    """Build {live_move_id: (monster_dict, move_dict)} from /api/monsters.

    API move ids carry no _MOVE suffix (SEA_KICK) while live state emits
    SEA_KICK_MOVE — both shapes are registered. Cached per process; the full
    monster list (~115 entries) is fetched once.
    """
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
                if not isinstance(move, dict):
                    continue
                mid = move.get("id")
                if not mid:
                    continue
                index[mid] = (monster, move)
                index[f"{mid}_MOVE"] = (monster, move)
    _CODEX_MOVE_INDEX = index
    return index


def codex_search(kind_path, query, timeout=10.0):
    """Query the codex search endpoint, e.g. /powers?search=ravenous."""
    import urllib.parse

    q = urllib.parse.quote(query)
    data = codex_api_get(f"/{kind_path}?search={q}", timeout=timeout)
    return data if isinstance(data, list) else []


def _format_damage(damage):
    """Render codex damage dict: {'normal':11,'ascension':13,'hit_count':4}."""
    if damage is None:
        return None
    if isinstance(damage, (int, float)):
        return str(damage)
    if not isinstance(damage, dict):
        return str(damage)
    normal = damage.get("normal")
    asc = damage.get("ascension")
    hits = damage.get("hit_count")
    parts = []
    if hits:
        parts.append(f"{normal}x{hits}")
    elif normal is not None:
        parts.append(str(normal))
    if asc is not None:
        parts.append(f"A:{asc}")
    return " ".join(parts) or None


def describe_move_from_api(move):
    """Build effect/play text for one codex move entry."""
    bits = []
    intent = move.get("intent")
    if intent:
        bits.append(str(intent))
    dmg = _format_damage(move.get("damage"))
    if dmg:
        bits.append(f"damage {dmg}")
    if move.get("block") is not None:
        bits.append(f"block {move['block']}")
    if move.get("heal") is not None:
        bits.append(f"heal {move['heal']}")
    for power in move.get("powers") or []:
        if not isinstance(power, dict):
            continue
        pid = power.get("power_id") or power.get("id") or "?"
        amt = power.get("amount")
        target = power.get("target")
        ptxt = pid if amt is None else f"{pid} {amt}"
        if target:
            ptxt += f" ({target})"
        bits.append(ptxt)
    effect = move.get("name") or move.get("id") or "move"
    if bits:
        effect = f"{effect}: " + "; ".join(bits)
    return effect


def build_monster_entry_from_api(monster):
    """Full monsters.json entry from a codex monster payload (live-id keys)."""
    api_id = monster.get("id") or ""
    moves = {}
    cycle = []
    for move in monster.get("moves") or []:
        if not isinstance(move, dict):
            continue
        api_move_id = move.get("id")
        if not api_move_id:
            continue
        live_move_id = f"{api_move_id}_MOVE"
        cycle.append(live_move_id)
        damage_raw = move.get("damage")
        damage = damage_raw if isinstance(damage_raw, dict) else {}
        intent = {
            "type": move.get("intent"),
            "base_damage": damage.get("normal"),
            "hits": damage.get("hit_count"),
        }
        if damage.get("hit_count") in (None, 1):
            if move.get("damage"):
                intent["class"] = "SingleAttackIntent"
        elif move.get("damage"):
            intent["class"] = "MultiAttackIntent"
        if damage.get("ascension") is not None:
            intent["base_damage_ascension"] = {"ascension": damage.get("ascension")}
        moves[live_move_id] = {
            "id": live_move_id,
            "kind": "move",
            "monster_id": api_id,
            "name": move.get("name") or api_move_id,
            "intents": [intent],
            "effect": describe_move_from_api(move),
            "follow_up_id": None,
            "play_notes": "",
            "aliases": [move.get("name") or api_move_id, api_move_id],
            "curated": False,
            "needs_zh": True,
            "source": f"codex-api:/monsters/{api_id}#{api_move_id}",
        }
    hp = {
        "base": monster.get("min_hp"),
        "max": monster.get("max_hp"),
        "notes": "",
    }
    if monster.get("min_hp_ascension") is not None:
        hp["ascension"] = {"min": monster.get("min_hp_ascension"), "max": monster.get("max_hp_ascension")}
    entry = {
        "id": api_id,
        "kind": "monster",
        "name": monster.get("name") or api_id,
        "type": monster.get("type"),
        "acts": [],
        "hp": hp,
        "is_boss": (monster.get("type") or "").lower() == "boss",
        "is_elite": (monster.get("type") or "").lower() == "elite",
        "cycle": cycle,
        "moves": moves,
        "aliases": [monster.get("name") or api_id],
        "description": (
            f"{monster.get('name') or api_id} ({monster.get('type') or 'monster'}): "
            f"HP {monster.get('min_hp')}-{monster.get('max_hp')} "
            f"(A {monster.get('min_hp_ascension')}-{monster.get('max_hp_ascension')}); "
            f"cycle {' → '.join(cycle) if cycle else 'unknown'}"
        ),
        "play_notes": "",
        "curated": False,
        "needs_zh": True,
        "source": f"codex-api:/monsters/{api_id}",
    }
    return entry


def fold_monster_entry(entry):
    """Merge a monster entry into monsters.json + monsters_zh.json."""
    api_id = entry.get("id")
    target_key = api_id
    for lang in ("en", "zh"):
        suffix = "_zh.json" if lang == "zh" else ".json"
        path = REF_DIR / f"monsters{suffix}"
        data = {}
        if path.exists():
            try:
                loaded = json.loads(path.read_text(encoding="utf-8"))
                if isinstance(loaded, dict):
                    data = loaded
            except (OSError, json.JSONDecodeError):
                data = {}
        existing = data.get(target_key)
        if isinstance(existing, dict) and existing.get("curated") is True:
            # Keep curated monster; still merge uncurated live-key aliases
            continue
        zh_entry = dict(entry)
        if lang == "zh":
            zh_entry["needs_zh"] = True
        data[target_key] = zh_entry
        REF_DIR.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    _REF_INDEX_CACHE.clear()


def fold_entry_into_reference(domain_stem, key, entry, lang="en"):
    """Write/merge one entry into references/game/<stem>.json (+ _zh.json)."""
    suffix = "_zh.json" if lang == "zh" else ".json"
    path = REF_DIR / f"{domain_stem}{suffix}"
    data = {}
    if path.exists():
        try:
            loaded = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(loaded, dict):
                data = loaded
        except (OSError, json.JSONDecodeError):
            data = {}
    existing = data.get(key)
    if isinstance(existing, dict) and existing.get("curated") is True:
        return path, False
    data[key] = entry
    REF_DIR.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path, True


def codex_candidate_urls(key):
    """Build spire-codex.com HTML candidate URLs (last-resort fallback)."""
    slug = key.lower().replace(" ", "_")
    candidates = []
    if "_MOVE" in key:
        stem = slug
        if stem.endswith("_move"):
            stem = stem[: -len("_move")]
        candidates.extend([f"{CODEX_BASE}/monsters/{slug}", f"{CODEX_BASE}/monsters/{stem}"])
    elif key.endswith("_POWER"):
        candidates.append(f"{CODEX_BASE}/powers/{slug}")
    elif key.endswith("_POTION") or "POTION" in key:
        candidates.append(f"{CODEX_BASE}/potions/{slug}")
    elif ".pages." in key:
        event = key.split(".pages.", 1)[0].lower()
        candidates.append(f"{CODEX_BASE}/events/{event}")
    elif key.isupper() or "_" in key:
        for category in ("relics", "cards", "potions", "powers", "events", "monsters", "characters"):
            candidates.append(f"{CODEX_BASE}/{category}/{slug}")
    else:
        for category in ("reference", "powers", "monsters", "cards"):
            candidates.append(f"{CODEX_BASE}/{category}/{slug}")
    deduped = []
    seen = set()
    for url in candidates:
        if url not in seen:
            seen.add(url)
            deduped.append(url)
    return deduped[:8]


def fetch_codex_text(url, timeout=12.0):
    """Best-effort HTML fetch, returned as plain text (last-resort fallback)."""
    import html as html_mod
    import re as re_mod
    import urllib.request

    req = urllib.request.Request(
        url,
        headers={"User-Agent": "spirectl-lookup/0.2 (+spire-copilot-bridge)"},
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        raw = resp.read().decode("utf-8", errors="replace")
    raw = re_mod.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", " ", raw)
    raw = re_mod.sub(r"(?is)<br\s*/?>|</p>|</div>|</li>|</h[1-6]>", "\n", raw)
    text = re_mod.sub(r"(?s)<[^>]+>", " ", raw)
    text = html_mod.unescape(text)
    text = re_mod.sub(r"[ \t]+", " ", text)
    text = re_mod.sub(r"\n\s*\n+", "\n", text)
    return text.strip()


def research_and_fold(key, domain_guess=None):
    """Lookup-miss fallback: spire-codex.com API first, HTML last.

    Returns (entry, source) when research produced data, else (None, None).
    Folded entries carry key = the LIVE id (state's shape); API ids land in
    aliases. Entries are curated:false — agent curation completes them.
    """
    source = None
    kind = domain_guess
    entry = None

    # ---------- API-first per domain ----------
    # Power ids: live shape has _POWER suffix; API ids usually don't.
    power_queries = [key]
    if key.endswith("_POWER"):
        power_queries.append(key[: -len("_POWER")])
    power_queries.append(key.replace("_", " ").lower())

    if kind == "move" or "_MOVE" in key:
        index = codex_move_index()
        hit = index.get(key) or index.get(key.replace("_MOVE", ""))
        if hit:
            monster = hit[0]
            entry = build_monster_entry_from_api(monster)
            source = f"codex-api:/monsters/{monster.get('id')}"
            kind = "move"
    if entry is None and (kind == "monster" or (kind is None and key.isupper())):
        data = codex_api_get(f"/monsters/{key.lower()}")
        if data is None:
            results = codex_search("monsters", key.replace("_", " ").lower())
            data = results[0] if results else None
        if isinstance(data, dict) and data.get("id"):
            entry = build_monster_entry_from_api(data)
            source = f"codex-api:/monsters/{data.get('id')}"
            kind = "monster"
    if entry is None and (kind in ("relic", None) or key.endswith("_PEARL") or key.isupper()):
        data = codex_api_get(f"/relics/{key.lower()}")
        if data is None:
            results = codex_search("relics", key.replace("_", " ").lower())
            data = results[0] if results else None
        if isinstance(data, dict) and data.get("id"):
            description = strip_codex_markup(data.get("description") or data.get("description_raw") or "")
            entry = {
                "id": key,
                "kind": "relic",
                "name": data.get("name") or key,
                "rarity": data.get("rarity_key") or data.get("rarity"),
                "character": data.get("pool"),
                "description": description,
                "aliases": [data.get("name"), data.get("id")],
                "play_notes": "",
                "curated": False,
                "needs_zh": True,
                "source": f"codex-api:/relics/{data.get('id')}",
            }
            source = entry["source"]
            kind = "relic"
    if entry is None and (kind in ("card", None) or key.endswith("_STRIKE") or key.endswith("_IRONCLAD")):
        data = codex_api_get(f"/cards/{key.lower()}")
        if data is None:
            results = codex_search("cards", key.replace("_", " ").lower())
            data = results[0] if results else None
        if isinstance(data, dict) and data.get("id"):
            description = strip_codex_markup(data.get("description") or data.get("description_raw") or "")
            entry = {
                "id": key,
                "kind": "card",
                "name": data.get("name") or key,
                "cost": data.get("cost"),
                "card_type": data.get("type_key") or data.get("type"),
                "rarity": data.get("rarity_key") or data.get("rarity"),
                "target_type": data.get("target"),
                "character_pool": data.get("color"),
                "description": description,
                "aliases": [data.get("name"), data.get("id")],
                "play_notes": "",
                "curated": False,
                "needs_zh": True,
                "source": f"codex-api:/cards/{data.get('id')}",
            }
            source = entry["source"]
            kind = "card"
    if entry is None and (kind in ("potion", None) or key.endswith("_POTION") or "POTION" in key):
        data = codex_api_get(f"/potions/{key.lower()}")
        if data is None:
            results = codex_search("potions", key.replace("_", " ").lower())
            data = results[0] if results else None
        if isinstance(data, dict) and data.get("id"):
            description = strip_codex_markup(data.get("description") or data.get("description_raw") or "")
            entry = {
                "id": key,
                "kind": "potion",
                "name": data.get("name") or key,
                "rarity": data.get("rarity_key") or data.get("rarity"),
                "description": description,
                "aliases": [data.get("name"), data.get("id")],
                "play_notes": "",
                "curated": False,
                "needs_zh": True,
                "source": f"codex-api:/potions/{data.get('id')}",
            }
            source = entry["source"]
            kind = "potion"
    if entry is None and kind in ("power", None):
        data = None
        for query in power_queries:
            data = codex_api_get(f"/powers/{query.lower()}")
            if data is not None:
                break
        if data is None:
            for query in power_queries:
                results = codex_search("powers", query.replace("_", " ").lower())
                if results:
                    data = results[0]
                    break
        if isinstance(data, dict) and data.get("id"):
            description = strip_codex_markup(data.get("description") or data.get("description_raw") or "")
            entry = {
                "id": key,
                "kind": "power",
                "name": data.get("name") or key,
                "power_type": data.get("type"),
                "stack_type": data.get("stack_type"),
                "counter_class": (data.get("stack_type") == "Counter"),
                "description": description,
                "aliases": [data.get("name"), data.get("id"), key.replace("_POWER", "")],
                "play_notes": "",
                "curated": False,
                "needs_zh": True,
                "source": f"codex-api:/powers/{data.get('id')}",
            }
            source = entry["source"]
            kind = "power"
    if entry is None and (kind in ("event", "event_option", None) or ".pages." in key):
        event_id = key.split(".pages.", 1)[0] if ".pages." in key else key
        data = codex_api_get(f"/events/{event_id.lower()}")
        if data is None:
            results = codex_search("events", event_id.replace("_", " ").lower())
            data = results[0] if results else None
        if isinstance(data, dict) and data.get("id"):
            description = strip_codex_markup(data.get("description") or "")
            options_blob = data.get("options") or data.get("pages") or []
            entry = {
                "id": event_id,
                "kind": "event",
                "name": data.get("name") or event_id,
                "acts": [data.get("act")] if data.get("act") else [],
                "description": description,
                "option_summary": json.dumps(options_blob, ensure_ascii=False)[:600] if options_blob else "",
                "aliases": [data.get("name"), data.get("id")],
                "play_notes": "",
                "curated": False,
                "needs_zh": True,
                "source": f"codex-api:/events/{data.get('id')}",
                "options": {},
            }
            # Fold the specific event_option key when the miss was an option.
            if ".pages." in key:
                option_entry = {
                    "id": key,
                    "kind": "event_option",
                    "event_id": event_id,
                    "title": key.rsplit(".", 1)[-1].replace("_", " ").title(),
                    "description": description,
                    "aliases": [key.rsplit(".", 1)[-1]],
                    "play_notes": "",
                    "curated": False,
                    "needs_zh": True,
                    "source": f"codex-api:/events/{data.get('id')}",
                }
                entry["options"][key] = option_entry
            source = entry["source"]
            kind = kind or "event"

    # ---------- HTML last resort ----------
    if entry is None:
        urls = codex_candidate_urls(key)
        best_text = ""
        best_url = None
        for url in urls:
            try:
                text = fetch_codex_text(url)
            except Exception:
                continue
            if not text or len(text) < 80:
                continue
            human = key.replace("_", " ").lower()
            if key.lower() not in text.lower() and human not in text.lower():
                continue
            best_text = text
            best_url = url
            break
        if not best_text:
            return None, None
        nav_markers = (
            "spire codex", "compendium", "card library", "relic collection",
            "potion lab", "jump back in", "pages you open", "stats", "rankings",
            "tier list", "leaderboard", "submit a run", "browse runs", "tools",
            "companion apps", "steam mod", "art exporter", "overlay",
            "knowledge demon bot", "sign in", "cookie", "press .",
        )
        human = key.replace("_", " ").lower()
        lines = [ln.strip() for ln in best_text.splitlines() if ln.strip()]
        body = []
        total = 0
        started = False
        for ln in lines:
            low = ln.lower()
            if not started:
                if key.lower() in low or human in low:
                    started = True
                else:
                    continue
            if any(m in low for m in nav_markers) and len(ln) < 60:
                continue
            if low.startswith("http"):
                continue
            body.append(ln)
            total += len(ln)
            if total > 600:
                break
        if not body:
            body = [ln for ln in lines if not any(m in ln.lower() for m in nav_markers)][:8]
        description = " ".join(body)[:700]
        # Infer kind/stem from the HTML URL category — fail-loud when the
        # category is unrecognizable instead of folding into a random domain.
        url_kind = None
        safe_url = best_url or ""
        for cat, knd in (
            ("relics", "relic"), ("cards", "card"), ("powers", "power"),
            ("potions", "potion"), ("events", "event"), ("monsters", "monster"),
            ("characters", "character"),
        ):
            if f"/{cat}/" in safe_url:
                url_kind = knd
                break
        kind = url_kind or kind
        if not kind or kind == "unknown":
            return None, None
        entry = {
            "id": key,
            "kind": kind,
            "name": key,
            "description": description,
            "aliases": [],
            "play_notes": "",
            "curated": False,
            "needs_zh": True,
            "source": f"codex-html:{best_url}",
        }
        source = entry["source"]

    # ---------- Fold ----------
    stem = {d: s for d, s in REF_DOMAIN_FILES}.get(kind or "", "relics")

    if stem == "monsters" and isinstance(entry, dict) and entry.get("kind") == "monster" and entry.get("moves"):
        fold_monster_entry(entry)
        return entry, source
    if stem == "monsters" and "_MOVE" in key:
        # Move-level stub nested under generic host (rare fallback path).
        path = REF_DIR / "monsters.json"
        data = {}
        if path.exists():
            try:
                loaded = json.loads(path.read_text(encoding="utf-8"))
                if isinstance(loaded, dict):
                    data = loaded
            except (OSError, json.JSONDecodeError):
                data = {}
        generic = data.get("generic")
        if not isinstance(generic, dict):
            generic = {"id": "generic", "kind": "monster", "name": "generic", "description": "synthetic host for move stubs", "aliases": [], "play_notes": "", "curated": False, "needs_zh": True, "source": "synthetic", "moves": {}}
        moves = generic.get("moves")
        if not isinstance(moves, dict):
            moves = {}
        stub = dict(entry)
        stub["kind"] = "move"
        if key not in moves or moves.get(key, {}).get("curated") is not True:
            moves[key] = stub
        generic["moves"] = moves
        data["generic"] = generic
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        _REF_INDEX_CACHE.clear()
        return stub, source
    if stem == "events" and isinstance(entry, dict) and entry.get("kind") == "event":
        event_id = entry.get("id")
        for lang in ("en", "zh"):
            suffix = "_zh.json" if lang == "zh" else ".json"
            path = REF_DIR / f"events{suffix}"
            data = {}
            if path.exists():
                try:
                    loaded = json.loads(path.read_text(encoding="utf-8"))
                    if isinstance(loaded, dict):
                        data = loaded
                except (OSError, json.JSONDecodeError):
                    data = {}
            existing = data.get(event_id)
            if isinstance(existing, dict) and existing.get("curated") is True:
                continue
            payload = json.loads(json.dumps(entry))
            if lang == "zh":
                payload["needs_zh"] = True
            data[event_id] = payload
            path.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        _REF_INDEX_CACHE.clear()
        return entry, source
    fold_entry_into_reference(stem, key, entry, lang="en")
    zh_entry = json.loads(json.dumps(entry))
    zh_entry["needs_zh"] = True
    fold_entry_into_reference(stem, key, zh_entry, lang="zh")
    _REF_INDEX_CACHE.clear()
    return entry, source


def print_entry(domain, entry, key, extra=None):
    """Human-readable lookup output; --json uses the raw entry instead."""
    print(f"key={entry.get('id') or key} kind={entry.get('kind') or domain} domain={domain}")
    if entry.get("name"):
        print(f"name={entry['name']}")
    if entry.get("description"):
        print(f"description: {entry['description']}")
    if entry.get("effect"):
        print(f"effect: {entry['effect']}")
    for field in (
        "cost", "card_type", "rarity", "target_type", "character_pool", "upgrade",
        "power_type", "stack_type", "counter_class", "host_of_affliction",
        "hp", "acts", "is_boss", "is_elite", "cycle", "passives",
        "base_damage", "hits", "status_card", "status_count",
        "label_semantics", "state_fields", "decision_rule", "member_classes",
        "intent_type", "follow_up_id", "display_note", "event_id", "title",
        "gates", "option_summary", "usage", "character", "aliases",
    ):
        if field in entry and entry[field] not in (None, "", [], {}):
            print(f"{field}: {json.dumps(entry[field], ensure_ascii=False)}")
    if entry.get("play_notes"):
        print(f"play_notes: {entry['play_notes']}")
    if entry.get("source"):
        print(f"source: {entry['source']}")
    if entry.get("needs_zh"):
        print("needs_zh: true (Chinese description pending curation)")
    if entry.get("curated") is False:
        print("curated: false (auto-folded — refine before relying on it)")
    if extra:
        print(extra)


def guess_domain(key, explicit=None):
    """Infer the reference domain for a lookup miss from key shape.

    Args:
        key: Live game id.
        explicit: Caller-provided --domain value, used verbatim when set.

    Returns:
        Domain string, or None when no shape rule matches.
    """
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
