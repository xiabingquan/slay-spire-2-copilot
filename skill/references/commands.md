# Commands and state reference

spirectl speaks JSON-lines TCP to the mimo-spire-bridge mod (default
127.0.0.1:17612). Run all commands from the mimo-spire repo root.

## CLI

    python3 bridge/spirectl.py doctor
    python3 bridge/spirectl.py launch
    python3 bridge/spirectl.py state [--json]
    python3 bridge/spirectl.py act <action> [--args '{"k":v}'] [--json]
    python3 bridge/spirectl.py wait [--timeout 60] [--interval 0.4]

## Actions

| action | args | notes |
|---|---|---|
| play | card_index, target_combat_id? | hand index; target auto-picks first hittable enemy when omitted |
| end_turn | — | only valid in play phase |
| use_potion | potion_index, target_combat_id? | index into potion slots |
| map_select | row, col | from run.available_map_points |
| choose | index | card rewards, relic choice, event options, reward buttons, chest relics, selection screens |
| skip | — | skip button on reward/selection screens |
| treasure_open | — | click the chest |
| proceed | — | enabled proceed/continue button |
| rest / smith | — | rest-site options |
| shop_buy / shop_leave | index | shop inventory |
| start_run | character?, seed? | menu automation; character matches id/name substring |
| abandon_run | — | abandon current run (iteration speed) |

All actions respond `submitted` immediately; poll `wait` for the outcome.

## Compact state fields

- screen: menu | combat | map | rewards | card_reward | relic_choice |
  card_choice | deck_select | treasure | event | rest | shop | game_over | other
- run: act_index (0-based), act_floor, total_floor, room_type, map_coord,
  available_map_points (row/col/point_type), gold
- player: hp/max_hp/block, gold, relics, potions, deck
- combat: round, current_side, turn_phase, energy/max_energy,
  creatures[] (combat_id, name, hp, block, powers, intents with damage/hits),
  piles (hand[] with index/id/cost/target_type/can_play, draw/discard/exhaust counts)
- screen_detail.options[]: kind + index + id/name for the current decision
- available_actions[]: legal actions computed for the current screen
- fingerprint: change token used by wait

Use --json when you need fields missing from the compact view (e.g. visited
coords, deck listing, intent class names).
