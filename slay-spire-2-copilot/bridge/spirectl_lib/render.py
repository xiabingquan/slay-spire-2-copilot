"""Compact human-readable rendering of bridge state snapshots."""
import json
import os

from . import refs
from .client import format_intent_bits


def fmt_power(p):
    """Compact power label: ID or ID:amount (kill-timer amounts must be visible)."""
    pid = p.get("id", "?")
    amt = p.get("amount")
    return f"{pid}:{amt}" if amt is not None else pid


def ref_tags_enabled(explicit=None):
    """True when compact auto-lookup tags should render.

    Args:
        explicit: Optional override (e.g. from --no-ref-tags); None reads env.

    Returns:
        False when explicitly disabled or SPIREBRIDGE_REF_TAGS is falsy;
        otherwise True when the reference index loaded successfully.
    """
    if explicit is not None:
        return explicit
    env = os.environ.get("SPIREBRIDGE_REF_TAGS", "").strip().lower()
    if env in ("0", "false", "off", "no"):
        return False
    return bool(refs.load_reference_index(os.environ.get("SPIREBRIDGE_REF_LANG", "en")))


def print_state(state, as_json=False):
    """Print a state snapshot as compact text or full JSON.

    Args:
        state: Bridge state snapshot.
        as_json: Print indented full JSON instead of compact lines.
    """
    if as_json:
        print(json.dumps(state, indent=2, ensure_ascii=False))
    else:
        print(render_compact(state))


def _render_header(state):
    """Screen/run header line: screen, type, floor, act, room, asc, seed, pos."""
    run = state.get("run") or {}
    parts = [f"screen={state.get('screen', '?')}"]
    if state.get("screen_type"):
        parts.append(f"type={state['screen_type']}")
    if run:
        parts.append(f"floor={run.get('total_floor')}")
        parts.append(f"act={(run.get('act_index') or 0) + 1}")
        parts.append(f"room={run.get('room_type')}")
        if run.get("ascension") is not None:
            parts.append(f"asc={run.get('ascension')}")
        if run.get("seed"):
            parts.append(f"seed={run.get('seed')}")
        if run.get("map_coord"):
            c = run["map_coord"]
            parts.append(f"pos=({c.get('row')},{c.get('col')})")
    return " | ".join(parts)


def _render_boon_room(run):
    """Loud line while an act-start boon room is still unvisited.

    Act-start boon rooms (Ancient/Neow-family) are easy to skip: the game
    lands on the row-1 map and available_map_points historically omitted the
    start room. The Ancient-typed check is defensive for stale mod builds.
    """
    start_room = run.get("act_start_room") or {}
    if start_room and not start_room.get("visited") and (
        start_room.get("is_boon_room") or start_room.get("point_type") in ("Ancient", "Neow", "NeowBoon")
    ):
        return (
            f"ACT-START BOON ROOM UNVISITED: ({start_room.get('row')},{start_room.get('col')})"
            f"={start_room.get('point_type')} — map_select it BEFORE any row-1+ point"
        )
    return None


def _render_player(state):
    """Player block lines: hp/gold, combat powers, relics, potions."""
    player = state.get("player") or {}
    if not player:
        return []
    lines = []
    gold = player.get("gold")
    gold_s = f" gold={gold}" if gold is not None else ""
    char_s = f" char={player.get('character')}" if player.get("character") else ""
    lines.append(f"player hp={player.get('hp')}/{player.get('max_hp')} block={player.get('block')}{gold_s}{char_s}")
    # player powers/debuffs mirror creature powers during combat
    combat_p = state.get("combat") or {}
    me = next((c for c in (combat_p.get("creatures") or []) if c.get("is_player")), None)
    if me and me.get("powers"):
        lines.append("player powers: " + ", ".join(fmt_power(p) for p in me["powers"]))
    relics = player.get("relics") or []
    if relics:
        relic_bits = []
        for r in relics:
            rid = r.get("id", "?")
            counter = r.get("counter")
            if counter is not None:
                rid = f"{rid}:{counter}"
            relic_bits.append(rid)
        lines.append("relics: " + ", ".join(relic_bits))
    potions = [p for p in (player.get("potions") or []) if p]
    if potions:
        lines.append("potions: " + ", ".join(f"[{p['index']}]{p.get('id')}" for p in potions))
    return lines


def _render_move_graph(creature):
    """One move-graph summary line for an enemy creature, or None."""
    graph = creature.get("move_graph")
    if not graph or creature.get("is_player"):
        return None
    gbits = [f"id{creature.get('combat_id')} {creature.get('name')}"]
    log = graph.get("state_log") or []
    if log:
        gbits.append("log=[" + ",".join(str(x) for x in log) + "]")
    current = graph.get("current_move_id")
    if current:
        gbits.append(f"current={current}")
    states = graph.get("states") or []
    follow_map = {
        s.get("id"): s.get("follow_up_id")
        for s in states
        if s.get("kind") == "move" and s.get("follow_up_id")
    }
    if current and follow_map:
        cycle = [current]
        nxt = follow_map.get(current)
        seen_cycle = {current}
        while nxt and nxt not in seen_cycle and len(cycle) < 12:
            cycle.append(nxt)
            seen_cycle.add(nxt)
            nxt = follow_map.get(nxt)
        if len(cycle) > 1:
            gbits.append("cycle=" + "→".join(str(x) for x in cycle))
    for s in states:
        if s.get("kind") == "random_branch":
            rbits = []
            for b in s.get("branches") or []:
                w = b.get("effective_weight", b.get("weight"))
                wtxt = f" w={w:.2f}" if isinstance(w, (int, float)) else ""
                rbits.append(f"{b.get('state_id')}{wtxt}")
            gbits.append(f"branch@{s.get('id')}: " + " ".join(rbits))
        elif s.get("kind") == "conditional_branch":
            cbits = []
            for b in s.get("branches") or []:
                met = b.get("condition_met")
                tag = "[ok]" if met is True else "[no]" if met is False else ""
                cbits.append(f"{b.get('state_id')}{tag}")
            gbits.append(f"cond@{s.get('id')}: " + " ".join(cbits))
    return "  " + " ".join(gbits)


def _render_combat(state, ref_index):
    """Combat block lines: header, creatures, graphs, history, piles, hand."""
    combat = state.get("combat") or {}
    lines = [
        f"combat round={combat.get('round')} side={combat.get('current_side')} "
        f"phase={combat.get('turn_phase')} energy={combat.get('energy')}/{combat.get('max_energy')}"
    ]
    graph_lines = []
    for c in combat.get("creatures") or []:
        mark = "*" if c.get("is_player") else "-"
        line = (
            f" {mark} id{c.get('combat_id')} {c.get('name')} "
            f"hp={c.get('hp')}/{c.get('max_hp')} block={c.get('block')}"
        )
        powers = c.get("powers") or []
        if powers:
            line += " powers=[" + ",".join(fmt_power(p) for p in powers) + "]"
        # move_id prints unconditionally — identity must never be dropped.
        move = c.get("move_id")
        if move:
            line += f" move={move}"
        intents = c.get("intents") or []
        if intents:
            line += " intent=" + "; ".join(format_intent_bits(intents, move_id=move))
        if move and ref_index:
            hit = ref_index.get(move) or ref_index.get(str(move).upper())
            if hit:
                snippet = _ref_snippet(hit[1])
                if snippet:
                    line += f" [{move}: {snippet}]"
        lines.append(line)
        graph_line = _render_move_graph(c)
        if graph_line:
            graph_lines.append(graph_line)
    if graph_lines:
        lines.append("move graphs:")
        lines.extend(graph_lines)
    history = combat.get("history") or []
    if history:
        tail = history[-6:]
        lines.append("history: " + " | ".join(
            str(h.get("text") or h.get("kind")) for h in tail
        ))
    piles = combat.get("piles") or {}
    play_count = piles.get("play_count")
    play_s = f" play={play_count}" if play_count is not None else ""
    lines.append(
        f"piles draw={piles.get('draw_count')} discard={piles.get('discard_count')} "
        f"exhaust={piles.get('exhaust_count')}{play_s}"
    )
    for card in piles.get("hand") or []:
        playable = "ok" if card.get("can_play") else f"no({card.get('unplayable_reason')})"
        lines.append(
            f" [{card.get('index')}] {card.get('id')} cost={card.get('cost')} "
            f"target={card.get('target_type')} {playable}"
        )
    return lines


def _render_options(state):
    """Screen-detail option lines."""
    detail = state.get("screen_detail") or {}
    options = detail.get("options") or []
    if not options:
        return []
    lines = ["options:"]
    for opt in options:
        desc = opt.get("description")
        desc_s = ""
        if desc:
            flat = " ".join(str(desc).split())[:80]
            desc_s = f" — {flat}"
        lines.append(f" [{opt.get('index')}] {opt.get('kind')}:{opt.get('id')} {opt.get('name') or ''}{desc_s}")
    return lines


def _render_actions(state):
    """Available-actions summary line, or None."""
    actions = state.get("available_actions") or []
    if not actions:
        return None
    summaries = []
    for a in actions:
        name = a.get("action")
        args = a.get("args") or {}
        if name in ("play", "choose", "map_select", "use_potion", "rest", "smith", "shop_buy"):
            summaries.append(f"{name}({','.join(f'{k}={v}' for k, v in args.items())})")
        else:
            summaries.append(name)
    return "actions: " + ", ".join(summaries)


def render_compact(state):
    """Render a bridge state snapshot as compact human-readable lines.

    Always prints move_id for monsters (dropping it on numeric intent labels
    was the root cause of "intent=11" information loss). Structured intent
    fields (damage/hits/base_damage/card_count) take priority over the label
    string; reference-DB snippets append when available.
    """
    use_tags = ref_tags_enabled(None)
    ref_index = refs.load_reference_index(os.environ.get("SPIREBRIDGE_REF_LANG", "en")) if use_tags else {}
    lines = []
    run = state.get("run") or {}
    lines.append(_render_header(state))
    boon = _render_boon_room(run)
    if boon:
        lines.append(boon)
    lines.extend(_render_player(state))
    if state.get("combat"):
        lines.extend(_render_combat(state, ref_index))
    lines.extend(_render_options(state))
    actions = _render_actions(state)
    if actions:
        lines.append(actions)
    lines.append(f"fingerprint={state.get('fingerprint')}")
    return "\n".join(lines)


def _ref_snippet(entry):
    """Compact structured summary for a referenced entry (no prose fields)."""
    if not isinstance(entry, dict):
        return ""
    if entry.get("kind") == "move" or "intents" in entry:
        parts = []
        for it in entry.get("intents") or []:
            if not isinstance(it, dict):
                continue
            d, h = it.get("base_damage"), it.get("hits")
            if d is not None:
                parts.append(f"{d}x{h}" if h and h > 1 else str(d))
            elif it.get("class"):
                parts.append(str(it["class"]))
        bd = entry.get("base_damage")
        if not parts and bd is not None:
            parts.append(str(bd))
        return "; ".join(parts)[:60]
    detail = entry.get("detail") if isinstance(entry.get("detail"), dict) else {}
    hp = detail.get("hp")
    if isinstance(hp, dict) and hp.get("min") is not None:
        return f"HP {hp['min']}-{hp.get('max')}"
    if detail.get("rarity"):
        return str(detail["rarity"])
    return ""
