"""Post-build fixups: curated ZH monster text, move-text canonicalization."""
from .data import MOVE_TEXT_FIXUPS, POST_ZH_FIXUPS


def apply_post_fixups(all_en: dict):
    """Apply ZH fixups + cross-monster move-text canonicalization pre-write."""
    monsters = all_en.get("monsters") or {}
    for key, (zh_name, zh_desc) in POST_ZH_FIXUPS.items():
        ent = monsters.get(key)
        if ent is not None:
            ent["zh_name"] = zh_name
            ent["zh_description"] = zh_desc
            ent["aliases"] = sorted(set(ent.get("aliases") or []) | {zh_name})
    # thin codex-born monster descriptions -> hp/cycle summary
    for key, ent in monsters.items():
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
    apply_move_fixups(all_en)


def apply_move_fixups(all_en: dict):
    """Canonicalize shared/system move texts; richest text wins for thin ones."""
    monsters = all_en.get("monsters") or {}
    # choose canonical rich text per move id across all monsters
    best = {}
    for mon in monsters.values():
        for mk, mv in (mon.get("moves") or {}).items():
            desc = mv.get("description") or ""
            if len(desc) > len(best.get(mk, "")):
                best[mk] = desc
    for mon_key, mon in monsters.items():
        moves = mon.get("moves") or {}
        for mk, (en_desc, zh_desc) in MOVE_TEXT_FIXUPS.items():
            mv = moves.get(mk)
            if mv is None:
                continue
            cur = mv.get("description") or ""
            if len(cur) < len(en_desc) or cur.strip().endswith("→") \
                    or len(cur) < 40:
                mv["description"] = en_desc
                mv["zh_description"] = zh_desc
                mv["source"] = (mv.get("source") or "") + "; curated:move-fixup"
        for mk, mv in moves.items():
            if mk in MOVE_TEXT_FIXUPS:
                continue
            cur = mv.get("description") or ""
            # thin/codex-fragment text loses to the richest text found anywhere
            thin = (len(cur) < 60 or cur.strip().endswith("→")
                    or cur.strip().lower().startswith("codex:"))
            if thin and best.get(mk) and len(best[mk]) > len(cur) + 20:
                mv["description"] = best[mk]
    return
