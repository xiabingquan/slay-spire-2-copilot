"""Entry construction, curated overlays, zh twin maintenance, merge policy.

Store schema per spirectl_lib/schema.py: envelope + per-kind detail; EN/ZH
twins share id/kind/aliases/detail — only `name` differs by language
(nested move/option names may also differ per language).
"""
import copy
import json
from pathlib import Path

from .data import CURATED_EXTRAS
from spirectl_lib.refs import new_entry          # noqa: E402  (path set in __init__)
from spirectl_lib.schema import DOMAIN_DEFAULT_KIND, entry_violations  # noqa: E402


def load_existing(path: Path) -> dict:
    """Read a JSON object file; {} when missing or invalid."""
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return data if isinstance(data, dict) else {}


def _fill_detail(target: dict, incoming: dict, key: str):
    """Fill-only: write incoming detail fields when target lacks a value."""
    det = target.setdefault("detail", {})
    for fk, fv in (incoming or {}).items():
        cur = det.get(fk)
        if fk == "moves" and isinstance(fv, dict):
            moves = det.setdefault("moves", {})
            for mk, mv in fv.items():
                if mk not in moves:
                    moves[mk] = copy.deepcopy(mv)
        elif cur in (None, "", [], {}):
            det[fk] = copy.deepcopy(fv)


def apply_extras(domain: str, entries: dict, zh_entries: dict):
    """Apply CURATED_EXTRAS structured overlays (fill-only, both twins)."""
    kind = DOMAIN_DEFAULT_KIND.get(domain, domain)
    for key, extra in (CURATED_EXTRAS.get(domain) or {}).items():
        en_blk = extra.get("en") or {}
        zh_blk = extra.get("zh") or {}
        e = entries.get(key)
        if not isinstance(e, dict):
            e = new_entry(kind, key)
            entries[key] = e
        if en_blk.get("name"):
            e["name"] = en_blk["name"]
        if en_blk.get("aliases"):
            e["aliases"] = sorted(set(e.get("aliases") or []) | set(en_blk["aliases"]))
        _fill_detail(e, en_blk.get("detail") or {}, key)
        z = zh_entries.get(key)
        if not isinstance(z, dict):
            z = copy.deepcopy(e)
            zh_entries[key] = z
        if zh_blk.get("name"):
            z["name"] = zh_blk["name"]
        if zh_blk.get("aliases"):
            z["aliases"] = sorted(set(z.get("aliases") or []) | set(zh_blk["aliases"]))
        _fill_detail(z, zh_blk.get("detail") or {}, key)
        # schema completeness after fill
        for store in (e, z):
            base = new_entry(kind, key, name=store.get("name"), aliases=store.get("aliases"))
            for fk, fv in base.items():
                if fk not in store:
                    store[fk] = fv
            for fk, fv in (base.get("detail") or {}).items():
                store.setdefault("detail", {}).setdefault(fk, fv)


def fill_zh_twins(en_domain: dict, zh_domain: dict):
    """Create ZH twins only for keys missing in the ZH file (never touch existing)."""
    for k, e in en_domain.items():
        if k not in zh_domain:
            zh_domain[k] = copy.deepcopy(e)


def sync_twins(en_domain: dict, zh_domain: dict):
    """EN is structure authority; ZH keeps its own names.

    - aliases: union of both sides (written to both)
    - detail: copied EN->ZH, preserving ZH nested record names; display_names
      unioned
    - schema completeness enforced on both sides
    """
    for k, e in list(en_domain.items()):
        z = zh_domain.get(k)
        if not isinstance(z, dict):
            zh_domain[k] = copy.deepcopy(e)
            z = zh_domain[k]
        e["aliases"] = z["aliases"] = sorted(a for a in set(e.get("aliases") or []) | set(z.get("aliases") or []) if a)
        if e.get("kind") in ("move", "event_option"):
            continue
        zd = z.get("detail") if isinstance(z.get("detail"), dict) else {}
        ed = e.get("detail") if isinstance(e.get("detail"), dict) else {}
        new_zd = copy.deepcopy(ed)
        if "display_names" in new_zd:
            dn = list(dict.fromkeys((ed.get("display_names") or []) + (zd.get("display_names") or [])))
            new_zd["display_names"] = dn
            ed["display_names"] = dn
        for nest in ("moves", "options"):
            znest = zd.get(nest) or {}
            for nk, nrec in (new_zd.get(nest) or {}).items():
                zrec = znest.get(nk)
                if isinstance(zrec, dict) and isinstance(nrec, dict):
                    if zrec.get("name"):
                        nrec["name"] = zrec["name"]
                    nrec["aliases"] = sorted(a for a in set(nrec.get("aliases") or []) | set(zrec.get("aliases") or []) if a)
                    if nest in ed and nk in (ed.get(nest) or {}) and isinstance(ed[nest].get(nk), dict):
                        ed[nest][nk]["aliases"] = nrec["aliases"]
        e["detail"] = ed
        z["detail"] = new_zd
        # completeness
        kind = e.get("kind") or ""
        if kind not in ("move", "event_option"):
            base = new_entry(kind, k)
            for fk, fv in base.items():
                if fk not in e: e[fk] = fv
                if fk not in z: z[fk] = copy.deepcopy(fv)
            for fk, fv in (base.get("detail") or {}).items():
                e.setdefault("detail", {}).setdefault(fk, copy.deepcopy(fv))
                z.setdefault("detail", {}).setdefault(fk, copy.deepcopy(fv))
    for k in list(zh_domain):
        if k not in en_domain:
            del zh_domain[k]
