---
name: slay-spire-2-copilot
description: Play Slay the Spire 2 (杀戮尖塔2) autonomously via the SpireBridge mod (spirectl CLI). Trigger when the user wants a Claude Code / Codex copilot to play STS2 — e.g. "用 Claude Code 打一局杀戮尖塔2", "用Claude打杀戮尖塔2", "play Slay the Spire 2 via Claude Code or Codex", "play STS2 with Claude", "let Claude play a run of Slay the Spire 2", "slay the spire 2 copilot". Also when the user asks to check game state, continue a run, or iterate an AI game session on this machine.
argument-hint: "<log-folder-path>  (absolute directory; required)"
---

# slay-spire-2-copilot — AI plays Slay the Spire 2

> Chinese version of this skill doc: SKILL_zh.md. The skill's name/description
> trigger configuration lives in this file.

## Overview

Control the locally installed Slay the Spire 2 through the spire-copilot-bridge
mod. All decisions are made by the AI: play fully autonomously, never ask the
user which card to pick.

The user does two things only: **invoke the skill**, and **provide an absolute
log folder path** (optionally: specify the character for the run). Mod build
and install, game launch, and handshake verification are all performed by the
skill at session start.

## How to invoke

Invoke the skill in Claude Code with an absolute log folder path in the
arguments, e.g.:

    /Users/<name>/spire-logs/session-a

A bare path is equally valid — any absolute directory in the arguments counts;
do not require a `log-path=` key and do not invent a path. Triggers (Chinese
or English): "用 Claude Code 打一局杀戮尖塔2", "play Slay the Spire 2 via
Claude Code or Codex".

The arguments may also explicitly name the character for this run (IRONCLAD /
SILENT / DEFECT / NECROBINDER / REGENT, or their Chinese names): **when the
user specifies one, the user's choice wins**; otherwise follow
"Playing → Character rotation".

How the log directory is resolved, how the environment variable takes effect,
and how log files are named: see "Runtime conventions" at the end.

## Session start

Execute in order; all of the following are the skill's own work:

0. **Check the local Python environment.** `python3 --version` must exist
   and be >= 3.8: spirectl uses the Python standard library only — no pip
   install, no venv. If python3 is missing or too old, stop and report to
   the user; do not proceed with the session setup.

1. **Resolve the log folder and set the environment variable.** Parse the
   absolute path from the invocation arguments:
   - No path in the arguments: stop before touching the game and ask the user
     for an absolute log folder path.
   - Path given but the directory does not exist: create it directly
     (`mkdir -p`) and tell the user explicitly:
     "The path you passed does not exist; it has been created: <path>".
     Only when creation fails (insufficient permissions, invalid path, …),
     ask the user for a workable log folder path.
   - Once the path is settled, set `SPIREBRIDGE_LOG_DIR=<abs-folder>`,
     **valid for the whole session**; every subsequent spirectl call carries:

         SPIREBRIDGE_LOG_DIR=<abs-folder> python3 bridge/spirectl.py <subcommand>

2. **Read memory** (before anything else). The memory system is a standing
   play reference for the whole session:
   - **Mandatory at session/run start**: `memory/overview.md` (run table +
     statistics crosstabs — the standing cross-run picture) plus the general
     lessons categories — combat principles, synergies, character spines
     (`memory/lessons/`).
   - **Before every decision**: consult only the MINIMAL necessary content —
     the single lessons entry or `spirectl lookup` result directly relevant
     to that decision (relic pick -> lessons/relics.md; entering a fight ->
     lessons/enemies.md + lookup; route -> lessons/route.md; full routing in
     memory/user_guide.md). Never browse wholesale.
   - **On demand**: a single run note under memory/runs/ — the file-name
     prefix equals the 对局序号 in overview.md; look the number up there
     first, then open the file.

3. **Environment check and mod self-install / self-heal** (cwd = this skill
   folder `<repo>/slay-spire-2-copilot`, which holds all runtime files):
   `SPIREBRIDGE_LOG_DIR=<abs-folder> python3 bridge/spirectl.py doctor`
   - doctor reports mod files MISSING, or the installed dll is older than any
     source under mod/SpireBridge `*.{cs,csproj,json}` (first run, or code
     changed since the last install) → run `bash scripts/install_mod.sh`
     (dotnet build; copies spire-copilot-bridge into the game's mods folder),
     then re-run doctor.
   - Game process not running → `spirectl launch` (starts the game via Steam
     and waits for the bridge). The first modded launch shows a one-time
     in-game mod warning; the user clicks accept inside the game — the only
     thing the user ever does beyond invoking the skill.
   - Window placement (policy 2026-09-19): every graceful stop (`spirectl
     stop` / `sl`) records the game window's current screen+position; the
     next launch RESTORES the window to that record. No record or failed
     restore → fallback: launching terminal's screen + fixed offset
     (2026-09-18 preference). Cosmetic only — never blocks launch. The game
     may run fullscreen or windowed — mode is not constrained.

4. **Handshake check**: confirm the versions in doctor output. Game version
   drift versus the mod's min_game_version is a hard stop: report it
   truthfully; do not improvise.

5. **Arm the watchdog**: `python3 bridge/spirectl.py watchdog enable`
   (see "Runtime conventions").

## Playing

### Takeover rule

Whatever state the game is in — fresh boot, main menu, mid-run, rest/shop/event
screen, or game_over — take it over: read state and push it forward. On
game_over, `act start_run` clears the summary chain automatically (server-side)
and begins a new run; a new run file is derived in the log folder.

Continuous play is the mandate: after every run ends (run memory written),
start the next run immediately. Never deadlock: if an action loops without a
state change, diagnose the screen (implement the missing server-side support),
rebuild the mod (`bash scripts/install_mod.sh`), relaunch, and resume. Card-play
decisions stay in the AI client — mechanical act-dumps are allowed only after
the AI has chosen the tactic.

### Character rotation

**When the user explicitly specifies a character, the user's choice wins** —
if a character name appears in the skill arguments or the conversation
(IRONCLAD / SILENT / DEFECT / NECROBINDER / REGENT, or Chinese names such as
铁甲战士 / 寂静), start the run with that character; do not rotate.

Rotate only when the user did not specify one: do not always play the same
character; try the candidate roster referenced by the game build in turn —
IRONCLAD, SILENT, DEFECT, NECROBINDER, REGENT. Use
`act start_run --args '{"character":"SILENT"}'` etc.; the menu automation
matches button names / character-id substrings and skips locked characters.
Record the character used in each run's memory note and run log;
character-specific observations belong in that run's memory note.

Modded-profile facts: runs live on the game's **modded save profile**
(`.../modded/profile1/`), separate from the user's vanilla profile and
starting near-fresh — a locked roster there is **by design, not a defect**.
Never copy or merge vanilla save progress into the modded namespace; never
flag the lock as a bug. Character unlocks are Timeline-epoch-gated, not
run-count-gated: `start_run` drains the Timeline automatically; if a
character is unexpectedly locked, run `spirectl act timeline_sync` at the
main menu and re-check.

### Game loop

Repeat until the run ends or the user stops you. Every spirectl call carries
`SPIREBRIDGE_LOG_DIR=<abs-folder>`:

1. `... state` — compact state (use `--json` only for fields the compact view
   omits). Compact always prints `move=<move_id>` per monster, structured
   intent bits (`atk:8` / `multi:7x2` / `status:2c` / lowercase type), and a
   move-graph section per alive monster (state_log, cycle, branch weights,
   `current=`) — resolve any id for its full entry via
   `python3 bridge/spirectl.py lookup <id>`. Routing decisions: `run.map.rows[]` in the JSON state carries the
   full act map (every point's `point_type` + `children` connectivity) —
   weigh elite/rest/shop/boss paths from it, not just the current row.
   **Route draft at act start (hard rule)**:
   before entering ANY room of a new act, read the full map and write an
   explicit route draft in the reply: number/positions of elites, shops (and
   whether gold earned by then can actually be spent there), rest geometry —
   is there a rest BEFORE each elite and BEFORE the boss, treasure placement —
   then pick the spine that satisfies the checklist. Note variance points
   (Unknown rooms). Revise the draft mid-act when a fork or major event
   changes the calculus. Act-transition full-HP assumptions break under fight
   attrition — if entry HP for a no-pre-rest elite lands below ~50%, potions
   ARE the reserve plan; spend gold at the latest shop BEFORE elite corridors,
   not after.
   **Boon rooms (run start + act transitions)**: every act begins with an
   Ancient/Neow-family boon room. Act 1's is **Neow** (relic choices —
   typically positive relics vs curse-cost relics); `start_run` reveals the
   profile's NeowEpoch first so the room spawns, and the game then auto-enters
   the Neow event at run start — pick a positive boon, never a curse-cost
   option without cause. Later acts place 先古移民-style start rooms. On every
   act transition check `run.act_start_room` — while `visited=false` /
   `is_boon_room=true` (or `point_type` Ancient), that point must be
   map_select'd FIRST; state re-injects it at the head of
   `available_map_points` and the compact view prints an ACT-START BOON ROOM
   UNVISITED warning. Never jump to row-1+ points while that flag is live —
   skipping the boon is a permanent loss (no backtracking)
2. Decide the action from the state plus the minimal relevant memory (the
   matching `memory/lessons/` entry and/or `spirectl lookup <id>` result —
   only what that decision needs)
3. `... act <action> --args '<json>' --wait` — actions return immediately once
   submitted; `--wait` polls until the state settles (stable fingerprint) then
   prints it. **One card per call — hard rule**:
   combat card plays are NEVER batched. Play exactly one card per `act play`
   call, re-read state, then decide the next card from the fresh indices —
   no multi-card `batch` dumps, no precomputed play chains. This kills card
   index drift at the source — batched or precomputed chains reindex the hand
   and can silently play the wrong card. `end_turn` is its own call, issued only after a
   fresh state read shows no further plays wanted. `batch` remains allowed
   only for non-card sequences that cannot reindex the hand (e.g. a lone
   map_select); even then, prefer separate calls. An index is valid only for
   the single act it was computed for, straight from the latest state print.
   Mid-combat choose-card overlays (boss Curse of Knowledge, potion card
   picks) now surface as screen=card_choice via the mod's overlay scan —
   answer them with `choose` like any other card screen.
4. Wait model is change-polling, never a timeout deadline:
   `wait --quiet 3` returns within ~3s — immediately on
   fingerprint change, or right away with the current state when idle. Do
   NOT use long blocking waits; if an act does not change the screen, re-read
   state and diagnose — the action may have been illegal, or the screen needs
   a different input
5. If act returns ok=false: read the message, re-read state, retry with a
   corrected action — do not blind-retry the same call
6. Post-act verification (settle-lag class): acts can resolve 1-3s after the
   call returns — a state read taken immediately may show the pre-act hand, and
   follow-up acts computed from it silently no-op. After any `act`/`batch`,
   re-read state (twice if the first read still looks pre-act) before computing
   indices for follow-ups. Overlay screens (smith/enchant/removal deck_select,
   discard hand_select, Tools-of-the-Trade style phase=Start prompts) work
   choose(index) THEN `proceed` — choose alone does not confirm. Treasure
   chests open with `treasure_open`, not choose. After `use_potion`, potion
   slots reindex — re-read before the next potion call.

### Mechanic-first combat (hard rule)

Failures here come from key mechanics missing from decisions, not from weak
decks. Every fight is played mechanic-first:

1. **Before the first turn of every combat against an unfamiliar enemy, and
   every elite/boss without exception**: resolve every unfamiliar
   move_id/power_id/relic_id via `python3 bridge/spirectl.py lookup <id>`
   (or read bridge/spirectl_lib/data/monsters.json / powers.json directly) — move
   cycle, every passive Power, every debuff/buff it applies. Every
   power/intent the live state shows must be one you can explain from
   references. Any unknown → perplexity-search → fold the answer into
   references EN+ZH → only then play.
2. **No identifier guessing**: every move_id, power_id, relic_id, card_id,
   potion_id, and event id in live state that is not already in working
   memory MUST be resolved with `spirectl lookup` before it informs a
   decision. Deriving effects from archive memory without a lookup is
   forbidden; a lookup miss is a loud research trigger (codex fallback runs
   automatically; if codex also misses, use perplexity-search then fold the
   fact into the JSON pair), never permission to guess.
3. **Counter-class powers are kill timers, not flavor**: SANDPIT (devour at
   0 — block does not save you), RINGING (1 card/turn), ESCAPE_ARTIST,
   HATCH, TIME_LIMIT, HardToKill caps, Plating thresholds. Track their
   Amount every turn; the compact state prints `POWER:amount` — read it.
   Build the turn plan around the counter (damage race vs extension cards),
   not just around incoming attack intents.
4. **Never dismiss unexplained lethal as a "display bug".** If something
   kills you through mathematically sufficient block, the mechanic you
   haven't researched is the cause: research it before the next attempt.
5. Archive data can be wrong. Live state + researched sources outrank
   one-line reference summaries; correct references the same session the
   wrongness is discovered.

Before acting each turn, check: ALL enemy powers/debuffs/buffs with amounts,
enemy intents, your HP/block, energy, and whether the hand is playable.
Keep a brief running commentary in your replies. Memory is consultable
mid-run at any moment — before each decision, open only the minimal relevant
content: the matching `memory/lessons/` category entry (enemy doctrine,
relic tricks, synergies…) and/or `spirectl lookup <id>` for structured
mechanics facts; per-run notes on demand via the overview 对局序号.

## Run end

Detailed run records are automatic: every state/act/wait call appends its
complete JSON payload to the current run file under `SPIREBRIDGE_LOG_DIR`
(one file per run; rotated on start_run/continue_run, finalized on game_over).
That folder lives outside the skill tree and outside the repo — logs are never
committed; never delete or rewrite live logs mid-run. `.claude/` is likewise
gitignored (harness runtime only).

When the run ends (game_over screen, or abandon):

1. Write this run's memory note to memory/runs/<run-number-4-digit-padded>_<CHARACTER>_<YYYYmmdd-HHMMSS>_<hash8>.md
   (run number = the 对局序号 this run will carry in overview.md — newest
   number + 1; then character id, run log timestamp and hash, underscore-
   separated) and its Chinese twin
   memory/runs/<run-number-4-digit-padded>_<CHARACTER>_<YYYYmmdd-HHMMSS>_<hash8>_zh.md — the two files
   must stay content-aligned. Both follow memory/user_guide.md and
   memory/template.md (formats defined there). Cite the run log by file name
   only — never personal absolute paths.
2. Fold newly observed game STRUCTURE (card/relic/potion/power/intent
   mechanics as structured fields) into the matching bridge/spirectl_lib/data/*.json
   and its `_zh` twin, entries keyed by live game id — schema is
   bridge/spirectl_lib/schema.py (envelope + per-kind detail; codex is the
   authoritative structure source, prose doctrine goes to memory/lessons) —
   then run `python3 scripts/build_game_reference_json.py --check`; it must
   exit 0 before any commit. Memory holds play insights and run process only,
   never game base data. Elite/boss entries get the full treatment: complete
   move cycles with numbers, every passive Power with amount/threshold, every
   applied status with values — thin one-line summaries are not enough for
   these classes; kill-window play doctrine goes to memory/lessons, not into
   the data store. ZH `name` values are web-sourced canonical names (codex /
   wikis) — never fabricated translations.
3. Update `memory/overview.md`: insert one row at the TOP of the run table,
   then recount the `## 统计` crosstabs (战绩总览 / 进阶进度) from the table.
4. Distill this run's forward-valuable experience into the matching
   `memory/lessons/` category files — items mapping one-to-one to an
   inventory-table row go into that row's experience cell; others stay as
   unordered-list items after the table.
5. Commit the run note, its `_zh` twin, the overview update, and the lessons
   changes — memory is version-controlled.
6. If the user has stopped playing: disarm the watchdog (see "Runtime
   conventions").
7. **Phased reflection**: reflection content never enters `overview.md` —
   it is written directly into the matching `memory/lessons/*.md` category
   files as dated unordered-list items (each entry carries its date).
   Cadence: the **first** reflection covers **all runs recorded so far**;
   every reflection after that covers the **10 runs** since the previous one
   (e.g. 36–45, 46–55, 56–65, … — fire when the cumulative run count reaches
   that boundary). Source material is the run notes under
   `memory/runs/`. overview.md holds only overall run results (its table
   with the leading **对局序号** column, newest run on top).

## Info-incomplete & anomaly contract

Any phenomenon that does not match expectations — bridge `INFO-INCOMPLETE` /
`info_complete=false`, printed state ≠ applied effect, silent no-ops,
deadlocks, unexplained combat outcomes — follows one contract:

- **Transient** (immediate re-read shows `info_complete`): auto-recover and continue — no special flow.
- **Everything else**: do NOT hard-stop the session and do NOT start a new
  run. Instead:
  1. **Root-cause it**: mod defect (StateBuilder reflection miss? reward
     mapping ghost nodes? unsupported screen type? version drift?) /
     strategy error (against memory doctrine?) / mechanic misunderstanding
     (resolve via lookup/perplexity?) / process debt (stale indices?
     batched calls?).
  2. Fix it (client/mod code; rebuild with `bash scripts/install_mod.sh` when
     C# changed; strategy/mechanic findings fold into data/lessons per their
     zoning).
  3. When the fix needs the mod loaded: **SL restore path** (in-game menu →
     main menu → `act continue_run`) — **continue the SAME run; never
     `start_run` to replace it.**
  4. **Feishu-notify** the user: what broke, root cause, what was changed.
  5. Record the cause and fix in the current run's memory note.

Fail-loud still governs illegal act submits (immediate `ok=false`
rejection); this contract governs what happens after an anomaly appears —
the two do not conflict.

## Self-iteration

- Tool defect (spirectl/mod/protocol issue): fix the code in this repo on the
  current branch; if C# changed, rebuild the mod (`bash scripts/install_mod.sh`)
  and verify with doctor, then note the cause and fix in the current run's
  memory note (memory/runs/). Commit with nature [fix] or [feature].
- Strategy doc proven wrong in play: correct the doc and note it in the run
  memory.
- Game patch broke hooks (doctor handshake ok but state fields missing/wrong):
  decompile the game assembly if needed, adapt the mod, and note the fix in
  the run memory.
- Mod features that touch progression/unlocks: **parity rule** — replay
  normal-play flows through the game's own UI/commands; never hard-grant
  roster or unlocks; repair steps may only write save states the game
  itself would write for earned progress (no extra buffs, no detriments).

## Notes

- Fixes may only touch this repo's code; never modify game assemblies.
- The game window may show another language or the user's other mods; state
  from the bridge is authoritative — trust it over screenshots.
- Do not spend in-game currency on the user's behalf outside the run loop
  (e.g. permanent unlocks): ask first for meta-progression choices.
- Never commit personal absolute paths, session log folders, or harness
  runtime files into the repo.
- proposal.md at the skill folder root is the agent's local scratchpad for
  play-process suggestions: if any part of the flow (Summary, memory
  consultation, references organization, ...) feels unsuited during or
  around a run, record the concern and a concrete proposal there. It is
  gitignored — the user reviews it; do not commit it.

## Runtime conventions

- **The only source for the run-log directory is the environment variable
  `SPIREBRIDGE_LOG_DIR`**: no pointer files, no CLI flags, no fallback
  directory. When the variable is unset, spirectl commands that write run logs
  fail fast with an error; the skill resolves it per "Session start" step 1 —
  set the variable if a path is available, otherwise ask the user.
- The variable is **valid for the whole session**. If it is missing at call
  time, treat it as a process error: stop and fix it immediately; never switch
  to another directory.
- spirectl treats the variable as a **folder**: each run derives a file inside
  it as `run-<timestamp>-<hash8>.log` (timestamp + short sha256, e.g.
  `run-20260916-013052-a3f9c012.log`).
- `doctor` prints `[0] run log dir: ... | SPIREBRIDGE_LOG_DIR=set|unset`;
  on unset, fix first, then continue.
- The external watchdog (crontab `scripts/watchdog_external.sh`) reads
  `SPIREBRIDGE_LOG_DIR` from **its own environment** — export the same folder
  on the crontab line to track this session's logs; when the variable is unset
  it skips the log-age check (no fallback there either).
- The watchdog runs checks and writes alert records only while armed; disarm
  when the user stops playing so it exits silently:

      python3 bridge/spirectl.py watchdog enable     # at session start
      python3 bridge/spirectl.py watchdog disable    # when the user stops play
      python3 bridge/spirectl.py watchdog status

- **SL restore path**: when an SL (save/load
  restore) is needed mid-run — deadlock recovery, mod rebuild, wedged screen —
  return to the game's **main menu inside the running game process**, then
  `continue_run` from there. **Never quit/kill the game process and relaunch
  for an SL.** In-game path: pause menu (top-bar pause button →
  `NPauseMenu`) → `Save And Quit` (`_saveAndQuitButton` /
  `OnSaveAndQuitButtonPressed`) → main menu → `act continue_run`. Only a real
  game crash (process gone) justifies `spirectl launch`; `spirectl sl`'s
  stop→launch flow is superseded by this rule and must not be used for
  routine SLs.
- **Hard-wedge exception (crash-class only)**: the game process alive but
  the main thread stuck in an internal loop — bridge handshake dead,
  `state` returns `screen=?`, AND the in-game pause menu physically
  unprocessable — means the in-game SL path does not exist in that moment.
  Only this class, or a mod DLL rebuild (mods load at game boot, so a
  rebuild needs one process restart), justifies `spirectl sl` stop→launch.
  Routine wedges (slow state, stuck overlay, illegal action) still use the
  in-game menu path. Always report which class you are in and why.

## References

Consult the following files as needed for decisions and troubleshooting (paths
are relative to this skill folder):

bridge/ — tooling docs and game data:

- `bridge/docs/commands.md` — CLI usage, action/state reference,
  log-directory contract
- `bridge/docs/protocol.md` — wire protocol v1 (JSON Lines over TCP on
  localhost)
- `bridge/spirectl_lib/data/characters.json` + `characters_zh.json` — playable
  characters, starters, archetypes
- `bridge/spirectl_lib/data/cards.json` + `cards_zh.json` — cards
- `bridge/spirectl_lib/data/potions.json` + `potions_zh.json` — potion effects
- `bridge/spirectl_lib/data/powers.json` + `powers_zh.json` — powers
- `bridge/spirectl_lib/data/relics.json` + `relics_zh.json` — relic effects
- `bridge/spirectl_lib/data/intents.json` + `intents_zh.json` — reading enemy intents
- `bridge/spirectl_lib/data/monsters.json` + `monsters_zh.json` — enemy move tables
  and passives (moves nested under each monster)
- `bridge/spirectl_lib/data/events.json` + `events_zh.json` — event rooms and known
  branches (options nested under each event)
- `bridge/spirectl_lib/data/afflictions.json` + `afflictions_zh.json` — statuses and
  debuffs
- JSON reference DB: purely programmatic store (envelope + per-kind detail,
  schema: bridge/spirectl_lib/schema.py); entries keyed by live game ids;
  resolve any id with `python3 bridge/spirectl.py lookup <key>` (flags
  `--json/--lang/--domain/--all`; miss path folds STRUCTURE from
  spire-codex.com directly — codex is authoritative). Doctrine/prose lives in
  memory/lessons, never in the data store.

memory/ — run memory (version-controlled):

- `memory/user_guide.md` — memory-writing guidance: formats, when to write,
  when to consult, remarks
- `memory/template.md` — section template for per-run memory notes
- `memory/overview.md` — cross-run table (`## 对局表`) + statistics crosstabs
  (`## 统计`); results only, no experience content
- `memory/lessons/` — standing cross-run experience, one file per category
  (characters / cards / relics / synergies / combat / economy / route /
  enemies / events), each EN + `_zh` twin
- `memory/runs/` — one note per run plus a `_zh` Chinese twin, named
  <run-number-4-digit-padded>_<CHARACTER>_<YYYYmmdd-HHMMSS>_<hash8>.md / _zh.md — the run
  number prefix equals the 对局序号 in memory/overview.md (lookup key)

- `SKILL_zh.md` — Chinese version of this skill doc
