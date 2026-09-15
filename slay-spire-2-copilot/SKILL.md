---
name: slay-spire-2-copilot
description: Play Slay the Spire 2 (杀戮尖塔2) autonomously via the SpireBridge mod (spirectl CLI). Trigger when the user wants a Claude Code / Codex copilot to play STS2 — e.g. "用 Claude Code 打一局杀戮尖塔2", "用Claude打杀戮尖塔2", "play Slay the Spire 2 via Claude Code or Codex", "play STS2 with Claude", "let Claude play a run of Slay the Spire 2", "slay the spire 2 copilot". Also when the user asks to check game state, continue a run, or iterate an AI game session on this machine.
argument-hint: "<log-folder-path>  (absolute directory; required)"
---

# slay-spire-2-copilot — AI plays Slay the Spire 2

You control the locally installed Slay the Spire 2 through the spire-copilot-bridge
mod. All decisions are yours: play fully autonomously, never ask the user which
card to pick.

## Invocation contract (user directive 2026-09-16)

The user passes a **log folder path** (an absolute directory), not a log file
path. Example: the skill arguments contain an absolute directory such as

    /Users/<name>/spire-logs/session-a

or simply the bare path — any absolute directory in the arguments counts.
Do not require a `log-path=` key; do not invent a path.

Rules:

1. Parse the skill arguments for an absolute directory (the log **folder**).
   If none is present, STOP before touching the game and ask the user for one.
2. Deliver that folder **only via the environment variable
   `SPIREBRIDGE_LOG_DIR`** on every spirectl call this session:

       SPIREBRIDGE_LOG_DIR=<abs-folder> python3 bridge/spirectl.py <subcommand>

   No pointer files, no CLI flags, nothing stored inside the project — the repo
   must contain zero personal paths.
3. spirectl treats `SPIREBRIDGE_LOG_DIR` as a **folder**: each run derives its
   actual log file inside it as `run-<timestamp>-<hash8>.log`
   (timestamp + short sha256 hash; e.g. `run-20260916-013052-a3f9c012.log`).
   If the env var is unset, the per-user runtime fallback
   `~/.local/share/slay-spire-2-copilot/logs` is used (computed at process
   start, never written into the project). `doctor` prints
   `[0] run log dir: ... | SPIREBRIDGE_LOG_DIR=set|unset`.
4. Cite the log folder and the concrete `run-<ts>-<hash>.log` name in the run
   postmortem and profile reports (disk paths only; logs are never committed).
5. External watchdog (crontab `bridge/watchdog-external.sh`) reads
   `SPIREBRIDGE_LOG_DIR` from **its own environment** — export the same folder
   on the crontab line to track this session. Arm only while play is expected:

       python3 bridge/spirectl.py watchdog enable     # session start
       python3 bridge/spirectl.py watchdog disable    # user stopped play
       python3 bridge/spirectl.py watchdog status

   If the user stops play, disarm immediately so Feishu is not nagged about
   "game not running".

## Session start

1. Resolve the log folder from the invocation arguments and prefix every
   spirectl call with `SPIREBRIDGE_LOG_DIR=<abs-folder>`.
   Arm the watchdog: `python3 bridge/spirectl.py watchdog enable`.
2. Read memory before doing anything else:
   - skill/memory/MEMORY.md (index)
   - skill/memory/lessons.md (playing lessons)
   - skill/memory/changelog.md (recent tool/strategy changes)
3. Run the environment check (cwd = this skill folder,
   <repo>/slay-spire-2-copilot — it holds ALL runtime files):
   `SPIREBRIDGE_LOG_DIR=<abs-folder> python3 bridge/spirectl.py doctor`
   If doctor fails on mod files, run `bash setup/install-mod.sh`.
   If the game is not running, `spirectl launch` starts it via Steam and waits
   for the bridge. The first modded launch shows an in-game mod warning — the
   user must click accept once; wait for the handshake after that.
4. Confirm handshake versions in doctor output. Game version drift vs the mod's
   min_game_version is a hard stop: report it, do not improvise.

## Character rotation (user directive)

Do not always play Ironclad. Rotate characters across runs — candidate roster
referenced by the game build: IRONCLAD, SILENT, DEFECT, NECROBINDER, REGENT.
Use `act start_run --args '{"character":"SILENT"}'` etc.; the menu automation
matches button name or character id substrings and skips locked characters.
Track which character each run used in the postmortem and run log. Build
per-character lessons in skills memory (e.g. skill/memory/strategies/<char>.md)
as play data accumulates.

## Takeover rule (any game state)

Whatever state the game is in — fresh boot, main menu, mid-run, rest/shop/event
screen, or game_over — take over: read state, drive it forward. At game_over,
`act start_run` clears the summary chain automatically (server-side) and begins
a new run; a new `run-<ts>-<hash>.log` is derived in the log folder. Continuous
play is the mandate: after each run ends (postmortem + changelog + optional
Feishu notify), start the next run. Never deadlock: if an action loops without
state change, diagnose the screen (implement missing server support per the
completeness rule), rebuild the mod (`bash setup/install-mod.sh`), relaunch,
and resume. Keep play decisions in Claude (client) — mechanical act-dumps are
fine only after Claude chose the tactic.

## Play loop

Repeat until the run ends or the user stops you. Every spirectl call carries
`SPIREBRIDGE_LOG_DIR=<abs-folder>`:

1. `... state` — compact state (use `--json` only when you need fields the
   compact view omits)
2. Decide the action using the state plus memory (lessons, strategies)
3. `... act <action> --args '<json>'` — actions return immediately
   (submitted); the game plays out animations itself.
4. `... wait --timeout 60` — blocks until the state fingerprint changes, then
   prints the new state. If wait times out, re-read state; the action may have
   been illegal or the screen may need another input.
5. If act returns ok=false, read the message, re-read state, and retry with a
   corrected action — do not blind-retry the same call.

Decision rules of thumb:

- Every turn: check enemy intents, your HP/block, energy, and hand playability
  before acting. Lethal on you means play defensively or end turn early.
- Card/relic rewards: weigh deck synergy over raw card strength; skip is a real
  option when nothing fits the deck.
- Map: prefer ? and elites only when healthy; rest sites matter on low HP.
- Keep a brief running commentary in your reply so the user can follow plays.

## Action and state reference

Full details: skill/references/commands.md (action table, state fields).
Protocol spec: docs/protocol.md in the repo.

## Run end (win OR loss) — memory protocol

Detailed run records are automatic: every spirectl state/act/wait call appends
its complete JSON payload to the current run file inside `SPIREBRIDGE_LOG_DIR`
(naming `run-<timestamp>-<hash8>.log`, one per run, rotated on
start_run/continue_run, finalized on game_over). That folder is outside the
skill tree and outside the repo — logs are never committed (user directive
2026-09-16); never delete or rewrite live logs mid-run. .claude/ is likewise
gitignored (harness runtime only).

When the run ends (game_over screen, or abandon):

1. Write a postmortem to skill/memory/runs/<YYYY-MM-DD>-<character>-floor<N>.md
   covering: result, key decisions, what worked, what killed the run, one lesson.
   Inside the postmortem cite the log **folder** and the concrete
   `run-<ts>-<hash>.log` name as disk paths only — commit just the markdown.
2. Update skill/memory/lessons.md only with generalizable lessons (not one-off
   bad RNG). Keep lessons.md short and concrete; prune entries that prove wrong.
3. Update skill/memory/MEMORY.md index if you added files.
4. Commit the memory changes in the repo with nature [docs].
5. If the user has stopped play for now, disarm the watchdog:
   `python3 bridge/spirectl.py watchdog disable`.

## Self-iteration protocol

- Tool bug (spirectl/mod/protocol issue): fix the code in the repo on the
  current feature branch, rebuild the mod if C# changed
  (`bash setup/install-mod.sh`), verify with doctor, then append a line to
  skill/memory/changelog.md describing cause + fix. Commit with nature [fix]
  or [feature].
- Strategy doc proved wrong in play: correct the doc, note it in changelog.md.
- Never delete changelog entries; this file is the iteration ledger.
- Game patch broke hooks (doctor handshake ok but state fields missing/wrong):
  re-check docs/research/game-api-findings.md, decompile if needed, adapt the
  mod, record in changelog.md.

## Boundaries

- Only this repo's code may be edited for fixes; never modify game assemblies.
- The game window may show another language or mods from the user; state comes
  from the bridge, trust it over the screenshot.
- Do not spend in-game currency decisions on the user's behalf outside a run
  loop (e.g. permanent unlocks): ask first for meta-progression choices.
- Never commit personal absolute paths, session log folders, or harness
  runtime files into the repo.
