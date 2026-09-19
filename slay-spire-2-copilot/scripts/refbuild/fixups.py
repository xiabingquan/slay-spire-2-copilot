"""Post-build fixups: curated ZH monster text, move-text canonicalization.

EN and ZH stores are fixed up independently — each language store's own
texts compete for richest-description; ZH texts come from POST_ZH_FIXUPS /
MOVE_TEXT_FIXUPS zh halves, never from EN fields.
"""
from .data import MOVE_TEXT_FIXUPS, POST_ZH_FIXUPS
from .textutil import has_cjk


def apply_post_fixups(all_en: dict, all_zh: dict):
    """Apply curated ZH monster text + move canonicalization pre-write."""
    monsters = all_en.get("monsters") or {}
    zh_monsters = all_zh.get("monsters") or {}
    for key, (zh_name, zh_desc) in POST_ZH_FIXUPS.items():
        ent = monsters.get(key)
        if ent is not None:
            ent["aliases"] = sorted(set(ent.get("aliases") or []) | {zh_name})
        zh_ent = zh_monsters.get(key)
        if zh_ent is not None:
            zh_ent["name"] = zh_name
            zh_ent["description"] = zh_desc
            zh_ent["aliases"] = sorted(set(zh_ent.get("aliases") or []) | {zh_name})
    # thin codex-born monster descriptions -> hp/cycle summary (per store)
    for store in (monsters, zh_monsters):
        for key, ent in store.items():
            desc = ent.get("description") or ""
            if len(desc) >= 80:
                continue
            hp = ent.get("hp") or {}
            cycle = ent.get("cycle") or []
            moves = ent.get("moves") or {}
            summary_bits = [f"{ent.get('name', key)}"]
            if hp.get("notes"):
                summary_bits.append(hp["notes"])
            elif hp.get("base"):
                summary_bits.append(f"{hp['base']} HP")
            if cycle:
                summary_bits.append("cycle " + " -> ".join(cycle[:8]))
            elif moves:
                summary_bits.append("moves " + ", ".join(sorted(moves)[:8]))
            summary = "; ".join(summary_bits)
            if len(summary) > len(desc):
                ent["description"] = summary + (
                    f" | {desc}" if desc.strip() and not desc.startswith("Monster ")
                    else " — resolve move ids via spirectl lookup; live intent "
                         "fields are authoritative.")
    apply_move_fixups(all_en, all_zh)


def apply_move_fixups(all_en: dict, all_zh: dict):
    """Canonicalize shared/system move texts per language store."""
    monsters = all_en.get("monsters") or {}
    zh_monsters = all_zh.get("monsters") or {}
    for store, fix_index in ((monsters, 0), (zh_monsters, 1)):
        best = {}
        for mon in store.values():
            for mk, mv in (mon.get("moves") or {}).items():
                desc = mv.get("description") or ""
                if len(desc) > len(best.get(mk, "")):
                    best[mk] = desc
        for mon_key, mon in store.items():
            moves = mon.get("moves") or {}
            for mk, fix_text in MOVE_TEXT_FIXUPS.items():
                mv = moves.get(mk)
                if mv is None:
                    continue
                text = fix_text[fix_index]
                cur = mv.get("description") or ""
                if len(cur) < len(text) or cur.strip().endswith("→") \
                        or len(cur) < 40:
                    mv["description"] = text
            for mk, mv in moves.items():
                if mk in MOVE_TEXT_FIXUPS:
                    continue
                cur = mv.get("description") or ""
                thin = (len(cur) < 60 or cur.strip().endswith("→")
                        or cur.strip().lower().startswith("codex:"))
                if thin and best.get(mk) and len(best[mk]) > len(cur) + 20:
                    if fix_index == 1 and not has_cjk(best[mk]):
                        continue  # EN placeholder in ZH file: leave until curated
                    mv["description"] = best[mk]
    return
