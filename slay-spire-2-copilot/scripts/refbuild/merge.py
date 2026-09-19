"""Entry envelope, curated-extras application, zh twin maintenance, merge policy.

EN and ZH files share one schema per domain: identical key sets, identical
field names. Chinese text lives ONLY in the ZH twin's name/description —
EN entries never carry zh_* fields.
"""
import copy
import json
from pathlib import Path

from .data import CURATED_EXTRAS
from .textutil import has_cjk, humanize


def envelope(entry_id: str, kind: str, name: str, description: str,
             aliases=None, play_notes: str = "", **extra):
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
    """Apply CURATED_EXTRAS overlays; curated:true prev entries are kept.

    EN blocks write the EN twin; zh blocks write Chinese name/description
    straight into the ZH twin. Both sides keep the same field schema.
    """
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
                for k, v in en.items():
                    carried[k] = v
                en = carried
                en["curated"] = True
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
                if k not in ("name", "description", "play_notes"):
                    zh.setdefault(k, v)
            zh["name"] = zh.get("name") or entries[key].get("name")
            zh["description"] = zh.get("description") or entries[key].get("description")
            zh["curated"] = True
            prevz = zh_entries.get(key)
            if prevz is None or prevz.get("curated") is not True:
                zh_entries[key] = zh


def fill_zh_twins(en_domain: dict, zh_domain: dict):
    """Create ZH twins only for keys missing in the ZH file.

    Existing ZH entries are never touched — Chinese text is authored and
    curated in the ZH twin itself. New twins start as schema-identical
    copies of the EN entry (English placeholder text until curated).
    """
    for k, e in en_domain.items():
        if k not in zh_domain:
            zh_domain[k] = copy.deepcopy(e)

def sync_schemas(en_domain: dict, zh_domain: dict):
    """Make every ZH entry's key set identical to its EN twin (EN is the
    structure authority). ZH-only keys are dropped; EN-only keys are copied
    in (English placeholder values — Chinese is curated in the ZH twin).
    Nested moves/options maps are synced the same way.
    """
    for k, e in en_domain.items():
        z = zh_domain.get(k)
        if not isinstance(z, dict) or not isinstance(e, dict):
            continue
        for fk in set(e) - set(z):
            z[fk] = copy.deepcopy(e[fk])
        for fk in set(z) - set(e):
            del z[fk]
        for nest in ("moves", "options"):
            en_nest = e.get(nest)
            if not isinstance(en_nest, dict):
                continue
            z_nest = z.get(nest)
            if not isinstance(z_nest, dict):
                z_nest = {}
                z[nest] = z_nest
            for nk, nv in en_nest.items():
                zv = z_nest.get(nk)
                if not isinstance(nv, dict) or not isinstance(zv, dict):
                    z_nest[nk] = copy.deepcopy(nv)
                    continue
                for fk in set(nv) - set(zv):
                    zv[fk] = copy.deepcopy(nv[fk])
                for fk in set(zv) - set(nv):
                    del zv[fk]
            for nk in set(z_nest) - set(en_nest):
                del z_nest[nk]
