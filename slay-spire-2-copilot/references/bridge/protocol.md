# SpireBridge wire protocol v1

Transport: TCP on localhost (default 127.0.0.1:17612). One JSON object per line
(UTF-8, newline-delimited), both directions. Client = spirectl / Claude skill;
server = spire-copilot-bridge mod inside the game process.

Versioning: every server message carries protocol_version, game_version,
assembly_hash (from the game release_info.json), and mod_version. Clients must
refuse to operate on a major protocol mismatch and surface version drift via doctor.

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

    {
      "type": "state",
      "protocol_version": 1,
      "game_version": "0.107.1",
      "assembly_hash": -1718063421,
      "mod_version": "0.1.0",
      "fingerprint": "<hash of snapshot fields, for change detection>",
      "screen": "menu|combat|map|rewards|card_reward|treasure|event|shop|rest|game_over|other",
      "run": {
        "active": true,
        "character": "...",
        "act_index": 0,
        "act_floor": 3,
        "total_floor": 3,
        "room_type": "Monster",
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
        "relics": [{"id": "...", "name": "..."}],
        "potions": [{"index": 0, "id": "...", "target_type": "AnyEnemy"}],
        "deck": [{"id": "...", "name": "...", "upgraded": false}]
      },
      "combat": null | {
        "round": 2,
        "turn_phase": "Play",
        "creatures": [
          {"combat_id": 0, "side": "Player", "is_player": true,
           "name": "...", "hp": 60, "max_hp": 80, "block": 5,
           "powers": [{"id": "...", "amount": 2}],
           "intent": null | {"id": "...", "damage": 12, "times": 1, "is_attack": true}},
          ...
        ],
        "piles": {
          "hand": [{"index": 0, "id": "...", "name": "...", "cost": 1,
                    "can_play": true, "unplayable_reason": null,
                    "target_type": "AnyEnemy", "upgraded": false}],
          "draw_count": 5, "discard_count": 2, "exhaust_count": 0
        }
      },
      "screen_detail": {
        "options": [{"index": 0, "kind": "card|relic|potion|event_option|map_point|button",
                     "id": "...", "name": "...", "detail": "..."}],
        "extra": { ... screen-specific ... }
      },
      "available_actions": [
        {"action": "play", "args": {"card_index": 0, "target_combat_id": 2}},
        {"action": "end_turn", "args": {}},
        {"action": "choose", "args": {"index": 0}},
        ...
      ]
    }

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
