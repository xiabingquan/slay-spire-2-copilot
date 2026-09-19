"""Entry envelope, curated-extras application, zh twin derivation, merge policy."""
import json
from pathlib import Path

from .data import CURATED_EXTRAS
from .textutil import has_cjk, humanize


def envelope(entry_id: str, kind: str, name: str, description: str,
             aliases=None, play_notes: str = "", source: str = "", **extra):
    """Build one reference entry with the standard field set.

    EN name must never carry CJK — falls back to the id humanized form.
    """
    if has_cjk(name):
        name = humanize(entry_id) if not has_cjk(entry_id) else entry_id
    e = {
        "id": entry_id,
        "kind": kind,
        "name": name,
        "description": (description or "").strip(),
        "aliases": sorted({str(a) for a in (aliases or []) if a and a != entry_id}),
        "play_notes": (play_notes or "").strip(),
        "curated": False,
        "needs_zh": False,
        "source": source,
    }
    e.update(extra)
    return e


def load_existing(path: Path) -> dict:
    """Read a JSON object file; {} when missing or invalid."""
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except json.JSONDecodeError:
        return {}


def merge_domain(old: dict, new: dict) -> dict:
    """Merge policy: curated:true old entries are never overwritten.

    Regenerated entries carry unknown keys forward from the prior entry;
    curated-only keys that exist solely in old are preserved.
    """
    merged = {}
    for key, entry in new.items():
        prior = old.get(key)
        if isinstance(prior, dict) and prior.get("curated") is True:
            merged[key] = prior
            continue
        if isinstance(prior, dict):
            carried = dict(entry)
            for k, v in prior.items():
                if k not in carried:
                    carried[k] = v
            merged[key] = carried
        else:
            merged[key] = entry
    for key, entry in old.items():
        if key not in merged and isinstance(entry, dict) and entry.get("curated") is True:
            merged[key] = entry
    return merged


def apply_extras(domain: str, entries: dict, zh_entries: dict):
    """Apply CURATED_EXTRAS overlays; curated:true prev entries are kept."""
    for key, extra in (CURATED_EXTRAS.get(domain) or {}).items():
        en = dict(extra.get("en") or {})
        zh = dict(extra.get("zh") or {})
        if not en:
            continue
        en.setdefault("id", key)
        en["curated"] = True
        prev = entries.get(key)
        if prev is None or prev.get("curated") is not True:
            if prev:
                carried = dict(en)
                for k, v in prev.items():
                    if k not in carried:
                        carried[k] = v
                # curated field-level overrides win
                for k, v in en.items():
                    carried[k] = v
                en = carried
                en["curated"] = True
                # absorb parser-discovered moves if curated entry lacks them
                if not (en.get("moves") and any(
                        (en["moves"] or {}).values())) and prev.get("moves"):
                    en["moves"] = prev["moves"]
                if not en.get("cycle") and prev.get("cycle"):
                    en["cycle"] = prev["cycle"]
            entries[key] = en
        if zh:
            zh = dict(zh)
            zh.setdefault("id", key)
            for k, v in entries[key].items():
                if k not in ("name", "description", "play_notes", "zh_name",
                             "zh_description", "zh_moves", "aliases"):
                    zh.setdefault(k, v)
            zh["name"] = zh.get("name") or entries[key].get("name")
            zh["description"] = zh.get("description") or entries[key].get("description")
            zh["curated"] = True
            zh["needs_zh"] = False
            prevz = zh_entries.get(key)
            if prevz is None or prevz.get("curated") is not True:
                zh_entries[key] = zh


def to_zh_entry(en_entry: dict) -> dict:
    """Derive the ZH twin from an EN entry (zh_name/zh_description win)."""
    zh = {}
    for k, v in en_entry.items():
        if k in ("zh_name", "zh_description", "zh_moves", "zh_play_notes"):
            continue
        zh[k] = v
    zh["name"] = en_entry.get("zh_name") or en_entry.get("name") or en_entry.get("id", "")
    desc = en_entry.get("zh_description") or ""
    if not desc:
        desc = en_entry.get("description", "")
        zh["needs_zh"] = True
    else:
        zh["needs_zh"] = False
    zh["description"] = desc
    zh["play_notes"] = en_entry.get("zh_play_notes") or en_entry.get("play_notes", "")
    if en_entry.get("kind") == "monster":
        zh_moves = en_entry.get("zh_moves") or {}
        moves = {}
        for mk, mv in (en_entry.get("moves") or {}).items():
            mv_zh = dict(mv)
            zh_desc = zh_moves.get(mk) or mv.get("zh_description")
            if zh_desc:
                mv_zh["description"] = zh_desc
                mv_zh["needs_zh"] = False
            moves[mk] = mv_zh
        zh["moves"] = moves
    if en_entry.get("kind") == "event":
        options = {}
        for ok, ov in (en_entry.get("options") or {}).items():
            ov_zh = dict(ov)
            if ov.get("zh_description"):
                ov_zh["description"] = ov["zh_description"]
                ov_zh["needs_zh"] = False
            options[ok] = ov_zh
        zh["options"] = options
    return zh


def fill_zh_twins(en_domain: dict, zh_domain: dict):
    """Ensure every EN key has a ZH twin; non-curated twins follow EN fields.

    Existing curated ZH entries are untouched. Non-curated ZH descriptions
    that already carry real text (needs_zh false) are preserved over the
    EN-derived fallback.
    """
    for k, e in en_domain.items():
        if k not in zh_domain:
            zh_domain[k] = to_zh_entry(e)
            continue
        z = zh_domain[k]
        if z.get("curated") is True:
            continue
        twin = to_zh_entry(e)
        if z.get("description") and not z.get("needs_zh"):
            twin["description"] = z["description"]
            twin["needs_zh"] = False
        if z.get("name"):
            twin["name"] = z["name"]
        zh_domain[k] = twin
