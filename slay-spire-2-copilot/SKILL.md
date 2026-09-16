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

2. **Read memory** (before anything else). Memory under memory/ is
   version-controlled and serves as a standing play reference for the whole
   session:
   - Mandatory before each run:
     - the Summary sections of all recorded runs (memory/runs/*.md — core
       facts plus the biggest gain/loss of each past run)
     - the accumulated key playstyles for the character about to play
       (gleaned from that character's run notes, <character>_*.md)
   - Optional: read full earlier run notes as needed.
   - During play: memory may be consulted at any time — past summaries and
     character playstyle notes are live reference for in-run decisions.

3. **Environment check and mod self-install / self-heal** (cwd = this skill
   folder `<repo>/slay-spire-2-copilot`, which holds all runtime files):
   `SPIREBRIDGE_LOG_DIR=<abs-folder> python3 bridge/spirectl.py doctor`
   - doctor reports mod files MISSING, or the installed dll is older than any
     source under mod/SpireBridge `*.{cs,csproj,json}` (first run, or code
     changed since the last install) → run `bash scripts/install-mod.sh`
     (dotnet build; copies spire-copilot-bridge into the game's mods folder),
     then re-run doctor.
   - Game process not running → `spirectl launch` (starts the game via Steam
     and waits for the bridge). The first modded launch shows a one-time
     in-game mod warning; the user clicks accept inside the game — the only
     thing the user ever does beyond invoking the skill.

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
rebuild the mod (`bash scripts/install-mod.sh`), relaunch, and resume. Card-play
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

### Game loop

Repeat until the run ends or the user stops you. Every spirectl call carries
`SPIREBRIDGE_LOG_DIR=<abs-folder>`:

1. `... state` — compact state (use `--json` only for fields the compact view
   omits)
2. Decide the action from the state plus memory (user guide, recent runs)
3. `... act <action> --args '<json>' --wait` — actions return immediately once
   submitted; `--wait` polls until the state settles (stable fingerprint) then
   prints it. For a chosen tactic spanning several acts, dump them in one
   `batch --acts '[...]'` call (settle-polls between acts, high-to-low
   card_index discipline on you)
4. Wait model is change-polling, never a timeout deadline (user directive
   2026-09-16): `wait --quiet 3` returns within ~3s — immediately on
   fingerprint change, or right away with the current state when idle. Do
   NOT use long blocking waits; if an act does not change the screen, re-read
   state and diagnose — the action may have been illegal, or the screen needs
   a different input
5. If act returns ok=false: read the message, re-read state, retry with a
   corrected action — do not blind-retry the same call

Before acting each turn, check at least: enemy intents, your HP/block, energy,
and whether the hand is playable. Keep a brief running commentary in your
replies. Memory is consultable mid-run at any moment — when a decision would
benefit from past runs (boss patterns, route choices, card evaluations),
re-read the relevant run summaries or the character's notes. Decision
lessons and card/potion/relic/intent knowledge: see "References" at the end.

## Run end

Detailed run records are automatic: every state/act/wait call appends its
complete JSON payload to the current run file under `SPIREBRIDGE_LOG_DIR`
(one file per run; rotated on start_run/continue_run, finalized on game_over).
That folder lives outside the skill tree and outside the repo — logs are never
committed; never delete or rewrite live logs mid-run. `.claude/` is likewise
gitignored (harness runtime only).

When the run ends (game_over screen, or abandon):

1. Write this run's memory note to memory/runs/<character>_<YYYYmmdd-HHMMSS>_<hash8>.md
   (character id first, then the run log's timestamp and hash, lowercase,
   underscore-separated) and its Chinese twin
   memory/runs/<character>_<YYYYmmdd-HHMMSS>_<hash8>_zh.md — the two files
   must stay content-aligned. Both follow memory/user guide.md and the
   section structure of memory/template.md (Summary table of core run facts /
   Run review / What went well / What went poorly / Key moments). Cite the
   run log by file name only —
   never personal absolute paths.
2. Fold newly observed game facts (card/relic/potion/power/intent effects)
   into the matching references/game/ file and its `_zh` twin as plain
   entries — the English and Chinese files must stay content-aligned. Memory
   holds play insights and run process only, never game base data.
3. Commit the run memory note and its `_zh` twin to the repo — memory is
   version-controlled.
4. If the user has stopped playing: disarm the watchdog (see "Runtime
   conventions").

## Self-iteration

- Tool defect (spirectl/mod/protocol issue): fix the code in this repo on the
  current branch; if C# changed, rebuild the mod (`bash scripts/install-mod.sh`)
  and verify with doctor, then note the cause and fix in the current run's
  memory note (memory/runs/). Commit with nature [fix] or [feature].
- Strategy doc proven wrong in play: correct the doc and note it in the run
  memory.
- Game patch broke hooks (doctor handshake ok but state fields missing/wrong):
  decompile the game assembly if needed, adapt the mod, and note the fix in
  the run memory.

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
- The external watchdog (crontab `scripts/watchdog-external.sh`) reads
  `SPIREBRIDGE_LOG_DIR` from **its own environment** — export the same folder
  on the crontab line to track this session's logs; when the variable is unset
  it skips the log-age check (no fallback there either).
- The watchdog runs checks and writes alert records only while armed; disarm
  when the user stops playing so it exits silently:

      python3 bridge/spirectl.py watchdog enable     # at session start
      python3 bridge/spirectl.py watchdog disable    # when the user stops play
      python3 bridge/spirectl.py watchdog status

## References

Consult the following files as needed for decisions and troubleshooting (paths
are relative to this skill folder):

references/ — consult knowledge:

- `references/README.md` — knowledge index
- `references/bridge/commands.md` — CLI usage, action/state reference,
  log-directory contract
- `references/bridge/protocol.md` — wire protocol v1 (JSON Lines over TCP on
  localhost)
- `references/game/characters.md` — playable characters, starters, archetypes
- `references/game/cards.md` — cards
- `references/game/potions.md` — potion effects
- `references/game/powers.md` — powers
- `references/game/relics.md` — relic effects
- `references/game/intents.md` — reading enemy intents
- `references/game/monsters.md` — enemy move tables and passives
- `references/game/events.md` — event rooms and known branches
- `references/game/afflictions.md` — statuses and debuffs
- `references/game/*_zh.md` — Chinese twins of the game knowledge files

memory/ — run memory (version-controlled):

- `memory/user guide.md` — user-written guidance for what agents should record
- `memory/template.md` — section template for per-run memory notes
- `memory/runs/` — one note per run plus a `_zh` Chinese twin, named
  <character>_<YYYYmmdd-HHMMSS>_<hash8>.md / <character>_<YYYYmmdd-HHMMSS>_<hash8>_zh.md

- `SKILL_zh.md` — Chinese version of this skill doc
