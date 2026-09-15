# Commands and state reference

spirectl speaks JSON-lines TCP to the spire-copilot-bridge mod (default
127.0.0.1:17612). Run all commands from the slay-spire-2-copilot repo root.

## Runtime log path (skill invocation contract)

Skill `slay-spire-2-copilot` requires an explicit log path at invocation
(`log-path=/abs/dir`). Session start persists it:

    python3 bridge/spirectl.py set-log-dir /abs/dir   # writes <repo>/.spire-log-dir
    python3 bridge/spirectl.py --log-dir /abs/dir state   # one-off override
    SPIREBRIDGE_LOG_DIR=/abs/dir python3 bridge/spirectl.py state  # env override

Resolution: `--log-dir` > `SPIREBRIDGE_LOG_DIR` > `.spire-log-dir` pointer >
`~/.local/share/slay-spire-2-copilot/logs`. Runtime `run-*.log` / `.current_run` land in
the resolved dir — never in the skill tree, never committed to git.
`doctor` prints the active dir as `[0] log dir:`. `bridge/watchdog-external.sh`
reads the same pointer for staleness checks.

## CLI

    python3 bridge/spirectl.py doctor
    python3 bridge/spirectl.py set-log-dir /abs/dir
    python3 bridge/spirectl.py launch
    python3 bridge/spirectl.py state [--json]
    python3 bridge/spirectl.py act <action> [--args '{"k":v}'] [--wait|--wait-play] [--json]
    python3 bridge/spirectl.py batch --acts '[{"action":"play","args":{"card_index":2}},{"action":"end_turn"}]'
    python3 bridge/spirectl.py wait [--timeout 60] [--interval 0.2]
    python3 bridge/spirectl.py profile [--log /abs/dir/run-*.log] [--budget 30]

## Fast path (speed mandate)

- `act --wait` — act, then poll until fingerprint settles (~0.35s stable), print
  the settled state. One process, one decision cycle.
- `act --wait-play` — after `end_turn`, poll until player Play phase resumes
  (or screen leaves combat / game_over). Default wait mode for `end_turn`.
- `batch --acts '[...]'` — mechanical act dump after Claude chose the tactic.
  Settles between acts, aborts on `ok=false`. Use **high-to-low** `card_index`
  so earlier plays don't invalidate later indices.
- Exit code 3 = STALL (fingerprint frozen > `--stall-timeout`, default 18s) —
  run the stop/launch/continue_run recovery ladder.
- Every command prints `[rtt=… srv=… queue=… settle=…]` profiling bits and logs
  them into `logs/run-*.log`. Summarize with `spirectl profile`.
- Game-side: mod sets `FastMode=Instant`, FTUE off, `NonInteractiveMode` on
  hello/start_run (see SpeedHooks.cs). `doctor` prints `speed=` from handshake.

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

All actions respond `submitted` immediately; `--wait` / `--wait-play` / `batch`
observe the outcome in the same process.

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

## Timing profile (per run)

`spirectl profile` decomposes run-log timestamps + instrumented metrics:

- bridge instrumentation: act/state rtt, server handle, dispatch queue,
  tcp connect, game settle (animation/resolution), command total
- wall-clock gaps: all / before act / after end_turn
- estimated client decision time = gap − previous settle − previous rtt
- budget check vs `--budget` minutes (default 30 = user mandate)

External liveness: `bridge/watchdog-external.sh` (crontab, 5-min) notifies
Feishu when game/bridge is down or run-log activity is stale >10min.
