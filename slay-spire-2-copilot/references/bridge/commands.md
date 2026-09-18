# Commands and state reference

spirectl speaks JSON-lines TCP to the spire-copilot-bridge mod (default
127.0.0.1:17612). Run all commands from the skill folder
`<repo>/slay-spire-2-copilot` (holds bridge/, mod/, scripts/, references/, memory/).

## Runtime log folder (env-only)

The skill invocation takes a **log folder** (absolute directory), not a file.
Deliver it only via environment variable — no pointer files, no CLI flags, no
personal paths inside the repo:

    SPIREBRIDGE_LOG_DIR=/abs/folder python3 bridge/spirectl.py state
    SPIREBRIDGE_LOG_DIR=/abs/folder python3 bridge/spirectl.py act play --args '{...}'

`SPIREBRIDGE_LOG_DIR` is the only source for the run-log folder — there is
no fallback directory; commands that write run logs fail fast if it is unset.
Inside the folder each run derives a unique file name:

    run-<YYYYmmdd-HHMMSS>-<hash8>.log     # timestamp + short sha256

e.g. `run-20260916-013052-a3f9c012.log`. A `.current_run` pointer in the same
folder tracks the active file across rotation (start_run/continue_run rotates,
game_over finalizes). `doctor` prints `[0] run log dir: ... | SPIREBRIDGE_LOG_DIR=set|unset`.

External liveness watchdog (crontab `scripts/watchdog-external.sh`) reads
`SPIREBRIDGE_LOG_DIR` from **its own environment** (set it on the crontab line
to track the active session folder; when unset it skips the log-age check —
no fallback). Alert logging fires only while ARMED:

    python3 bridge/spirectl.py watchdog enable    # session start
    python3 bridge/spirectl.py watchdog disable   # user stopped play
    python3 bridge/spirectl.py watchdog status

## CLI

    python3 bridge/spirectl.py doctor
    python3 bridge/spirectl.py watchdog enable|disable|status
    python3 bridge/spirectl.py launch
    python3 bridge/spirectl.py state [--json] [--no-ref-tags]

State notes:

- `run.available_map_points` = only the currently selectable row.
- `run.map.rows[]` = the full act map: every point with `point_type` plus
  `children` connectivity — use it for route planning (elite/rest/shop/boss
  look-ahead) instead of the single-row view.
- `run.act_start_room` = the act map's lowest-row point with
  `{row, col, point_type, visited, is_boon_room}`. Ancient/Neow-family
  starts (先古移民 and kin — HP-restore and other boons) must be selected
  FIRST while `visited=false`; unvisited boon starts are re-injected at the
  head of `available_map_points` with `act_start_boon: true`. The compact
  view prints `ACT-START BOON ROOM UNVISITED: ...` while that holds.
- Enemy intents are structured (mod >= 0.2.0, protocol v1.1 additive):
  every intent carries `type`/`class`/`label` plus `damage`/
  `total_damage`/`hits`/`base_damage` (Attack intents), `card_count`
  (Status intents), and `description` — full schema in
  references/bridge/protocol.md. Loc leaks like `intents:FORMAT_EMPTY` are
  replaced server-side with the intent type. The compact view always prints
  `move=<move_id>` per monster (label content irrelevant — the structured
  fields are the source of truth), renders intent bits as `atk:8` /
  `multi:7x2` / `status:2c` / lowercase intent type, a move-graph section
  per alive monster (state_log, cycle via `follow_up_id`, branch weights,
  `current=`), a history tail (last 6 of `combat.history`), pile counts
  plus `play=N`, relic counters (`HAPPY_FLOWER:2`), and event option
  descriptions (<=80 chars).
- `--json` exposes the rest: full `move_graph` (intents for EVERY move in
  the machine, random/conditional branch detail), pile id-arrays
  (`draw_card_ids`/`discard_card_ids`/`exhaust_card_ids`/`play_card_ids`;
  `+` suffix marks an upgraded copy — strip before lookup), `combat.history[]`
  (last 20 `{kind,text}` entries, excluded from the fingerprint), encounter
  fields (`encounter_id`/`should_give_rewards`/`min_gold_reward`/
  `max_gold_reward`/`hittable_enemy_combat_ids`/
  `escaped_creature_combat_ids`), `run.seed`/`game_mode`/`modifiers`, relic
  `counter`/`stack_count`/`is_used_up`, potion `rarity`/`usage`, event
  option `description`/`event_id`/`relic_id`.
- Compact auto-reference tags (default on when references/game/*.json
  exists): a resolvable move_id gets a ` [MOVE_ID: <=60-char summary]`
  snippet after the intent. Opt out per call with `--no-ref-tags`
  (state/act/batch/wait) or session-wide with env `SPIREBRIDGE_REF_TAGS=0`.
  Env `SPIREBRIDGE_REF_LANG=en|zh` picks the language for auto tags and is
  the default for `lookup --lang`.
- Resolve every unfamiliar move_id/power_id/relic_id/card_id/potion_id/event
  id on the wire via `spirectl lookup <key>` before it informs a decision.
  The reference DB is references/game/*.json + *_zh.json (key = live game
  id); markdown twins are pending retirement — cite the JSON files.
- AllEnemies/AnyPlayer potions must be sent via `use_potion` WITHOUT
  `target_combat_id` (AnyEnemy potions may pass one); a stray target is
  ignored and logged.

Lookup (reference resolution):

    python3 bridge/spirectl.py lookup <key> [--json] [--lang en|zh] [--domain D] [--all]

- `<key>` = a live game id exactly as state emits it — e.g. `GLOMP_MOVE`,
  `RAVENOUS_POWER`, `BURNING_BLOOD`,
  `NEOW.pages.INITIAL.options.NEOWS_TALISMAN`, `SingleAttackIntent`,
  `STUNNED`. Resolution reads references/game/*.json (or *_zh.json) via a
  fail-loud ladder: exact key (top-level, aliases, flattened
  monsters[*].moves[*] and events[*].options[*]) → event-option textKey →
  case-insensitive → upgrade-suffix probes (`X+`→`X`; bare `STRIKE` lists
  the `STRIKE_*` family).
- Flags: `--json` prints the raw entry; `--lang en|zh` selects the EN or ZH
  file pair (default: env `SPIREBRIDGE_REF_LANG`, else `en`); `--domain D`
  restricts to move|power|relic|card|potion|event|affliction|intent|
  character|monster; `--all` prints every domain match (bare keys otherwise
  resolve by domain priority: move → power → relic → card → potion →
  event_option/event → affliction/status_card → intent_class/intent_type →
  character → monster; conflicts list the rest in a footer).
- Miss pipeline (never silent): a key absent from the JSON DB falls through
  to https://spire-codex.com research (URL pattern
  `https://spire-codex.com/{category}/{lowercase_id}`; categories:
  cards/relics/monsters/powers/potions/events/characters/reference). A
  codex hit is folded into the matching references/game/*.json + *_zh.json
  pair as a `curated:false` stub and returned; refine it (perplexity-search
  / decomp facts), set `curated:true` bilingual, then re-run
  `python3 scripts/build_game_reference_json.py --check`. If codex has no
  page, lookup exits 1 with a loud perplexity-search research trigger —
  a lookup miss is a research trigger, never permission to guess.
- Coverage gate: `python3 scripts/extract_live_ids.py --logs "$SPIREBRIDGE_LOG_DIR"`
  harvests live ids from run logs;
  `python3 scripts/build_game_reference_json.py --check` must exit 0
  (every live id resolvable, EN+ZH descriptions non-empty) before commits.

    python3 bridge/spirectl.py act <action> [--args '{"k":v}'] [--wait|--wait-play] [--stall-timeout 3] [--json] [--no-ref-tags]
    python3 bridge/spirectl.py batch --acts '[{"action":"play","args":{"card_index":2}},{"action":"end_turn"}]' [--stall-timeout 3] [--no-ref-tags]
    python3 bridge/spirectl.py wait [--quiet 3.0] [--interval 0.2] [--no-ref-tags]
    python3 bridge/spirectl.py profile [--log /abs/folder/run-<ts>-<hash>.log] [--budget 30]
    python3 bridge/spirectl.py sl [--json]
    python3 bridge/spirectl.py stop


- **Information-completeness contract (mod 0.3.0, 2026-09-19)**: every state
  payload carries `info_complete:bool`, `missing_info:[...]`,
  `notify_user:bool`. The server must return exactly what a player can read
  in-game — no fallbacks (no invented `option_N` names, no silent null
  move_graphs, no unverified card-reward presses). Card-reward `choose`
  resolves the requested option id BEFORE pressing (refuses with
  `ok=false, "info incomplete: ..."` when unresolvable) and verifies the
  applied card against the deck delta on the next state — result stamped as
  `last_choose_verification {verify: pending|applied|applied_upgrade|unresolved}`.
  Conditional move-graph branches with empty tables, unreadable decks/rewards,
  and unresolved option ids all raise `missing_info` entries. Client gate
  (spirectl): any payload with `notify_user:true` / `info_complete:false` /
  `message` starting `info incomplete` → prints `[INFO-INCOMPLETE]`, sends a
  Feishu notification once per stop fingerprint, writes
  `~/.local/share/slay-spire-2-copilot/info-incomplete-stop`, exits **78**.
  Subsequent `act`/`batch`/`sl` calls refuse while the stop flag exists —
  clear with `rm <stop flag>` after the gap is fixed.

Action notes:

- `timeline_sync` (main menu only, no args): runs the Timeline reveal drain
  without starting a run — the mod visits the Timeline screen and clicks every
  Obtained epoch slot through the game's native inspect/unlock UI so
  QueueUnlocks side effects (character unlocks, timeline expansions) fire as
  they do in manual play. A repair step first places EARNED character epochs
  at ObtainedNoSlot+UnlockSlot (the states the game's own QueueUnlocks
  writes); nothing unearned is granted. start_run runs the same drain
  automatically before character select. Verify via progress.save epoch
  states / `pending_character_unlock`, or the `timeline:` lines in godot.log.
- `start_run` args: `character` (optional substring match on Character.Id.Entry
  / button name), `seed` (optional), `ascension` (optional int >= 0). When
  `ascension` is present it is fail-loud validated against the profile's
  `CharacterStats.MaxAscension` for that character (levels unlock via wins;
  nothing unearned is granted) — missing stats, unloaded progress, or a level
  above max all return ok=false before any UI work, and an explicit character
  arg is required. Application writes profile `PreferredAscension` before
  character Select, then `NAscensionPanel.SetAscensionLevel` +
  `StartRunLobby.SyncAscensionChange` (plus reflection fallback to the game's
  private singleplayer path); godot.log `start_run:` lines record each path.
  Verify post-embark via `run.ascension` (RunState.AscensionLevel — authority),
  `player.character` / `player.character_id`,
  `player.ascension_max_at_start`, and compact state `asc=` / `char=`.
- Card play targeting: Self/AoE/random-target cards
  (Defend, Shrug It Off, Bloodletting, Armaments, Whirlwind, Sword Boomerang,
  …) must **omit** `target_combat_id` — the game silently no-ops
  PlayCardAction when a creature target is passed to them (card stays in hand,
  energy unchanged). The bridge now fail-loud rejects `target_combat_id` on
  any card whose TargetType is not AnyEnemy/AnyAlly/AnyPlayer. Only
  AnyEnemy/AnyAlly/AnyPlayer consume an explicit target id.
- X-cost cards: `play` with no extra args submits
  Whirlwind-class X-cost cards at **full current energy as X** (3 energy →
  X=3, three hits per enemy). Omit `target_combat_id` (AllEnemies). An explicit
  `"x":N` argument is **accepted syntactically but silently ignored** — the
  game still spends full current energy as X (`x:2` at 3 energy
  still plays X=3). Do not plan around partial-X Whirlwind; treat the card
  as always-all-energy.
- After any overlay confirm (hand_select/deck_select `proceed`, Headbutt
  pile choices), **re-read state before computing follow-up play indices** —
  hand reindexes and a computed index hits the wrong card (e.g. an Armaments
  confirm followed by play(index) can hit Bludgeon instead of the upgraded
  Defend).
- Treasure rooms: the chest is opened with `treasure_open` (no args) — `choose`
  on the chest button returns `use treasure_open for it`. After opening, the
  relic holder is claimed with `choose(index=<holder>)`; gold credits
  automatically. Then `proceed` leaves the room.
- Overlay screens that select-then-confirm (deck_select for smith/enchant/
  removal, hand_select for discards: Dagger Throw / Survivor / Tools of the
  Trade turn-start prompts): `choose(index=N)` marks the pick (fingerprint may
  not change), **`proceed` confirms** — always follow choose with proceed.
  hand_select prompts that open at `phase=Start` (start-of-turn discard
  powers) must be answered before any Play-phase acts.
- After `use_potion`, remaining potions reindex to fill the empty slot —
  re-read state before the next `use_potion` (stale index → "empty or out of
  range").
- Killing all enemies does not always auto-transition: if combat screen lingers
  with no enemies, `end_turn` fires the mod's win-condition force path into
  rewards.
- Crystal-sphere minigame (CRYSTAL_SPHERE event): all 121 cells surface in
  state as unnamed `crystal_cell` nodes — revealed contents are visual-only,
  so the agent picks blind; rewards grant on minigame proceed.

## Wait model (change-polling, no timeout deadlines)

Play-loop waits never block on a deadline.

- `wait` polls the fingerprint every `--interval` (0.2s): returns the new
  state immediately on change; if unchanged for `--quiet` (3.0s default)
  it returns the current state right away with a "no change" note.
- `act --wait` / `batch` settle between acts the same way: poll until the
  fingerprint is stable (0.35s) or Play phase resumes; a FROZEN fingerprint
  for `--stall-timeout` (3.0s default) returns/aborts as STALL so the caller
  can re-read and decide. Polling continues without limit while state keeps
  changing — real progress (animations, enemy turns) is worth waiting through.
- Lifecycle waits keep bounded caps on purpose: `launch --timeout` (120s,
  Steam boot + handshake) and `sl --menu-timeout` (45s, boot to menu).
