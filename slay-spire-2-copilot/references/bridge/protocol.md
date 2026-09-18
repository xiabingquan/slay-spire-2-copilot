# SpireBridge wire protocol v1

> **protocol v1.1 additive — clients must ignore unknown fields;
> ModVersion >= 0.2.0.** Wire `protocol_version` stays 1; the state snapshot
> gained structured fields (see below) that earlier docs never listed.

Transport: TCP on localhost (default 127.0.0.1:17612). One JSON object per line
(UTF-8, newline-delimited), both directions. Client = spirectl / Claude skill;
server = spire-copilot-bridge mod inside the game process.

Versioning: every server message carries protocol_version, game_version,
assembly_hash (from the game release_info.json), and mod_version. Clients must
refuse to operate on a major protocol mismatch and surface version drift via
doctor. v1.1 changes are additive only: unknown fields must be ignored, never
treated as errors.

## Client -> server

    {"type": "hello"}
    {"type": "ping"}
    {"type": "state"}
    {"type": "act", "action": "<name>", "args": { ... }}

## Server -> client

    {"type": "hello_ok", "protocol_version": 1, "game_version": "...",
     "assembly_hash": ..., "mod_version": "..."}
    {"type": "pong"}
    {"type": "state", ...snapshot...}
    {"type": "act_result", "ok": true, "action": "...", "message": "...",
     "state": {...snapshot...}}
    {"type": "error", "message": "...", "detail": "..."}

State is poll-based in v1. spirectl wait polls until screen/fingerprint changes.
No unsolicited server pushes in v1 (may be added later as protocol v2).

## State snapshot

Schema below matches ModVersion >= 0.2.0 (protocol v1.1 additive — clients
must ignore unknown fields). The old fictional singular
`intent:{id,damage,times,is_attack}` is gone; intents are a structured array.
`combat.history` is excluded from the fingerprint input.

    {
      "type": "state",
      "protocol_version": 1,
      "game_version": "0.107.1",
      "assembly_hash": -1718063421,
      "mod_version": "0.2.0",
      "fingerprint": "<hash of snapshot fields (combat.history excluded), for change detection>",
      "screen": "menu|combat|map|rewards|card_reward|relic_choice|card_choice|deck_select|hand_select|treasure|event|shop|rest|crystal_sphere|game_over|other",
      "run": {
        "active": true,
        "act_index": 0,
        "act_floor": 3,
        "total_floor": 3,
        "room_type": "Monster",
        "is_game_over": false,
        "gold": 99,
        "ascension": 0,
        "seed": "<run RNG seed string>",
        "game_mode": "<RunState.GameMode>",
        "modifiers": ["<modifier id entry>", "..."],
        "map_coord": {"row": 2, "col": 1},
        "visited_coords": [{"row": 0, "col": 0}],
        "available_map_points": [{"row": 3, "col": 0, "point_type": "Monster"}],
        "act_start_room": {"row": 0, "col": 3, "point_type": "Ancient",
                           "visited": false, "is_boon_room": true},
        "map": {
          "rows": [
            {"row": 1, "points": [
              {"row": 1, "col": 0, "point_type": "Monster",
               "children": [{"row": 2, "col": 0}, {"row": 2, "col": 2}]}
            ]}
          ]
        }
      },
      "player": {
        "hp": 60, "max_hp": 80, "gold": 99,
        "character": "IRONCLAD", "character_id": "...",
        "ascension_max_at_start": 0,
        "relics": [{"id": "...", "name": "...",
                    "counter": 2, "stack_count": 1, "is_used_up": false}],
        "potions": [{"index": 0, "id": "...", "name": "...",
                     "target_type": "AnyEnemy", "rarity": "Common",
                     "usage": "CombatOnly"}],
        "deck": [{"index": 0, "id": "...", "name": "...", "upgraded": false}]
      },
      "combat": null | {
        "round": 2,
        "current_side": "Player",
        "turn_phase": "Play",
        "turn_number": 2,
        "energy": 3, "max_energy": 3,
        "encounter_id": "...",
        "should_give_rewards": true,
        "min_gold_reward": 10, "max_gold_reward": 20,
        "hittable_enemy_combat_ids": [1, 2],
        "escaped_creature_combat_ids": [],
        "history": [{"kind": "<HistoryEntry class name>", "text": "..."}],
        "creatures": [
          {"combat_id": 0, "side": "Player", "is_player": true,
           "name": "...", "hp": 60, "max_hp": 80, "block": 5,
           "is_alive": true, "is_hittable": true,
           "model_id": "...", "slot_name": "...",
           "is_primary_enemy": false, "is_secondary_enemy": false,
           "is_stunned": false,
           "powers": [{"id": "...", "name": "...", "amount": 2,
                       "type": "Buff", "stack_type": "...",
                       "is_visible": true,
                       "applier_combat_id": 0, "applier_name": "..."}],
           "move_id": "GLOMP_MOVE",
           "intents": [
             {"type": "Attack", "class": "SingleAttackIntent",
              "label": "8", "damage": 8, "total_damage": 8, "hits": 1,
              "base_damage": 8, "card_count": null, "description": "..."}
           ],
           "move_graph": {
             "current_move_id": "GLOMP_MOVE",
             "state_log": ["<move id>", "..."],
             "states": [ ... see move_graph shapes below ... ]
           }},
          ...
        ],
        "piles": {
          "hand": [{"index": 0, "id": "...", "name": "...", "cost": 1,
                    "can_play": true, "unplayable_reason": null,
                    "target_type": "AnyEnemy", "upgraded": false}],
          "draw_count": 5, "discard_count": 2, "exhaust_count": 0,
          "play_count": 0,
          "draw_card_ids": ["..."], "discard_card_ids": ["..."],
          "exhaust_card_ids": ["..."], "play_card_ids": ["..."]
        }
      },
      "screen_detail": {
        "options": [{"index": 0, "kind": "card|relic|potion|event_option|map_point|button|...",
                     "id": "...", "name": "...", "detail": "...",
                     "description": "...", "event_id": "NEOW", "relic_id": "..."}],
        "extra": { ... screen-specific ... }
      },
      "available_actions": [
        {"action": "play", "args": {"card_index": 0, "target_combat_id": 2}},
        {"action": "end_turn", "args": {}},
        {"action": "choose", "args": {"index": 0}},
        ...
      ]
    }

### intents[] (per creature, monsters only)

Structured since ModVersion 0.2.0 — field names are exact:

- `type` — IntentType enum string (`Attack`, `Buff`, `Debuff`, `Status`, ...)
- `class` — intent CLR class name (`SingleAttackIntent`, `MultiAttackIntent`, ...)
- `label` — live loc preview text (FORMAT_EMPTY leaks already cleaned server-side)
- `damage` — live single-hit damage, game modifiers applied (Attack intents;
  fail-soft omitted)
- `total_damage` — damage x hits for multi-hit attacks
- `hits` — repeat count (Single = 1)
- `base_damage` — raw pre-hook damage (for comparison against references/game/intents.json)
- `card_count` — Status intents: cards applied
- `description` — full resolved intent description (fail-soft omitted)

### move_id and move_graph (per alive monster)

- `creature.move_id` — always present on monsters: the current `NextMove.Id`
  (e.g. `GLOMP_MOVE`, `STUNNED`). Resolve via `spirectl lookup <move_id>`.
- `creature.move_graph` — emitted only while the monster is alive:
  `{current_move_id, state_log, states}`. `state_log` = recent performed move
  ids (capped at 12). `states[]` covers the monster's full move machine, one
  entry per state, kinds:

  - `move`: `{id, kind:"move", is_current, must_perform_once?, follow_up_id?,
    intents?[]}` — `intents` is the same structured intents[] shape, emitted for
    EVERY move in the machine, not just the current one (the full move table)
  - `random_branch`: `{id, kind:"random_branch", branches:[{state_id, weight?,
    effective_weight?, cooldown, repeat_type, max_times}]}` — weights are
    read-only state reads; the mod never calls RNG-consuming methods
  - `conditional_branch`: `{id, kind:"conditional_branch", branches:[{state_id,
    condition_met?}]}`
  - `other`: `{id, kind:"other"}` — future/unknown state types; clients ignore

### powers[] (enriched)

`{id, name, amount, type, stack_type, is_visible, applier_combat_id?,
applier_name?}` — `type` = PowerType (Buff/Debuff/...), `stack_type` =
stacking rule, applier_* = who applied it. Power descriptions are NOT on the
wire; resolve `power_id` via `spirectl lookup` against
references/game/powers.json.

### piles (combat)

- `hand[]` — full CardDto per card (index/id/name/cost/target_type/can_play/
  unplayable_reason/upgraded)
- id-arrays: `draw_card_ids`, `discard_card_ids`, `exhaust_card_ids`,
  `play_card_ids` — id strings only; a `+` suffix marks an upgraded copy
  (strip before lookup). `play_count` mirrors the play-pile size.
- counts `draw_count`/`discard_count`/`exhaust_count` unchanged

### combat.history, encounter, run, relics, event options

- `combat.history` — last 20 entries `{kind, text}` (kind = history entry
  class name; text = HumanReadableString). Excluded from fingerprint inputs —
  enemy animation traffic never stalls settle-polling.
- `combat.encounter_id`, `should_give_rewards`, `min_gold_reward`,
  `max_gold_reward`, `hittable_enemy_combat_ids`,
  `escaped_creature_combat_ids` — encounter identity and reward geometry.
- `run.seed` / `run.game_mode` / `run.modifiers` — RNG seed string, game mode,
  active modifier id entries. Character id lives on `player.character` /
  `player.character_id`; `run.ascension` is the authority for ascension level.
- `player.relics[]` — adds `counter` (DisplayAmount when the relic shows a
  counter), `stack_count`, `is_used_up`. `player.potions[]` adds `rarity` and
  `usage` (CombatOnly/AnyTime/Automatic).
- `screen_detail.options[]` event options (`kind:"event_option"`) carry
  `description` (resolved option text), `event_id` (textKey prefix before
  `.pages.`), and `relic_id` when the option grants a relic.

Full reference entries for any id on the wire: `spirectl lookup <key>`
(references/bridge/commands.md).

## Actions v1

| action | args | behavior |
|---|---|---|
| start_run | character?, seed? | main-menu automation to a fresh run |
| proceed | — | click current proceed / continue / next |
| map_select | row, col | click map point at coordinates |
| play | card_index, target_combat_id? | CardCmd.AutoPlay on hand card |
| end_turn | — | PlayerCmd.EndTurn |
| use_potion | potion_index, target_combat_id? | potion EnqueueManualUse. target_combat_id only for TargetType AnyEnemy potions; AllEnemies/AnyPlayer potions must be sent WITHOUT target — a creature target made the use a silent no-op pre-fix (mod now forces null) |
| choose | index | pick option on current overlay screen (reward/relic/event/select) |
| skip | — | skip current reward/selection when available |
| treasure_open | — | open chest |
| rest | — | rest-site rest option |
| smith | — | rest-site smith/upgrade option |
| shop_buy | index | buy shop slot |
| shop_leave | — | leave shop |
| abandon_run | — | abandon current run (iteration speed) |

Unknown action or illegal state -> act_result ok=false with message; state included
when readable. Handlers resolve all references at execution time on the game main
thread from live state; stale indices are rejected with a clear error.

## Error and compatibility rules

- Port busy / game not running -> spirectl doctor reports; no retry storm
- Game version change breaks hooks -> mod still serves hello/state but marks
  "unsupported_game_version": true; doctor fails loudly
- Mod fails to load (manifest error) -> game log only; doctor checks game log for
  "spire-copilot-bridge" load lines and for RUNNING MODDED
