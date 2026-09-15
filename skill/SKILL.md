---
name: slay-spire-2-copilot
description: Play Slay the Spire 2 (杀戮尖塔2) autonomously via the SpireBridge mod (spirectl CLI). Trigger when the user wants a Claude Code / Codex copilot to play STS2 — e.g. "用 Claude Code 打一局杀戮尖塔2", "用Claude打杀戮尖塔2", "play Slay the Spire 2 via Claude Code or Codex", "play STS2 with Claude", "let Claude play a run of Slay the Spire 2", "slay the spire 2 copilot". Also when the user asks to check game state, continue a run, or iterate an AI game session on this machine.
argument-hint: "log-path=/absolute/dir  (required — runtime logs go here)"
---

# slay-spire-2-copilot — AI plays Slay the Spire 2

You control the locally installed Slay the Spire 2 through the spire-copilot-bridge
mod. All decisions are yours: play fully autonomously, never ask the user which
card to pick.

## Invocation contract (user directive 2026-09-16)

This skill MUST be invoked with an **explicit runtime log path**, e.g.:

    /slay-spire-2-copilot log-path=/Users/me/spire-logs/2026-09-16-night

or any absolute directory passed in the skill arguments. Rules:

1. Parse the invocation arguments for an absolute log directory
   (`log-path=...`, `log_path=...`, or a bare absolute path).
2. If none is present, STOP before touching the game and ask the user for one.
   Never invent a path; never write run logs into the skill directory or the repo.
3. At session start, persist that path:
   `python3 bridge/spirectl.py set-log-dir <abs-path>`
   — this creates the directory, writes `<repo>/.spire-log-dir` (gitignored
   pointer), and routes every subsequent spirectl call's `run-*.log` there.
   Resolution order inside spirectl: `--log-dir` flag > `SPIREBRIDGE_LOG_DIR`
   env > `.spire-log-dir` pointer > `~/.local/share/slay-spire-2-copilot/logs`.
4. Cite the same absolute path in the run postmortem and any profile report.
   `bridge/watchdog-external.sh` reads the same pointer for staleness checks.

## Session start

1. **Resolve + persist the explicit log path** (contract above):
   `python3 bridge/spirectl.py set-log-dir <abs-path>`
   Confirm doctor later prints `log dir: <abs-path>`.
2. Read memory before doing anything else:
   - skill/memory/MEMORY.md (index)
   - skill/memory/lessons.md (playing lessons)
   - skill/memory/changelog.md (recent tool/strategy changes)
3. Run the environment check:
   `python3 bridge/spirectl.py doctor`
   Paths are relative to the slay-spire-2-copilot repo root (this skill lives in
   <repo>/skill). If doctor fails on mod files, run `bash setup/install-mod.sh`.
   If the game is not running, `python3 bridge/spirectl.py launch` starts it via
   Steam and waits for the bridge. The first modded launch shows an in-game mod
   warning — the user must click accept once; wait for the handshake after that.
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
a new run; the session log dir rotates per run. Continuous play is the mandate:
after each run ends (postmortem + changelog + optional Feishu notify), start the
next run. Never deadlock: if an action loops without state change, diagnose the
screen (implement missing server support per the completeness rule), rebuild the
mod (`bash setup/install-mod.sh`), relaunch, and resume. Keep play decisions in
Claude (client) — mechanical act-dumps are fine only after Claude chose the
tactic.

## Play loop

Repeat until the run ends or the user stops you:

1. `python3 bridge/spirectl.py state` — compact state (use `--json` only when
   you need fields the compact view omits)
2. Decide the action using the state plus memory (lessons, strategies)
3. `python3 bridge/spirectl.py act <action> --args '<json>'`
   Actions return immediately (submitted); the game plays out animations itself.
4. `python3 bridge/spirectl.py wait --timeout 60` — blocks until the state
   fingerprint changes, then prints the new state. If wait times out, re-read
   state; the action may have been illegal or the screen may need another input.
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
its complete JSON payload to the active session log dir (set via
`spirectl set-log-dir` at skill invocation; one `run-*.log` per run, rotated on
start_run/continue_run, finalized on game_over). That directory is outside the
skill tree and outside the repo — logs are gitignored, disk-retained only
(user directive 2026-09-16); never delete or rewrite live logs mid-run.
.claude/ is likewise gitignored (harness runtime only).

When the run ends (game_over screen, or abandon):

1. Write a postmortem to skill/memory/runs/<YYYY-MM-DD>-<character>-floor<N>.md
   covering: result, key decisions, what worked, what killed the run, one lesson.
   State the explicit session log dir and the matching run-*.log filename inside
   the postmortem as disk paths only — commit just the postmortem markdown.
2. Update skill/memory/lessons.md only with generalizable lessons (not one-off
   bad RNG). Keep lessons.md short and concrete; prune entries that prove wrong.
3. Update skill/memory/MEMORY.md index if you added files.
4. Commit the memory changes in the repo with nature [docs].

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
