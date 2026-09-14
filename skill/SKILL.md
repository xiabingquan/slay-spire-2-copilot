---
name: spire
description: Play Slay the Spire 2 autonomously via the SpireBridge mod (spirectl CLI). Use when the user asks to play STS2, check game state, continue a run, or run/iterate an AI game session on this machine.
---

# Spire — AI plays Slay the Spire 2

You control the locally installed Slay the Spire 2 through the mimo-spire-bridge
mod. All decisions are yours: play fully autonomously, never ask the user which
card to pick.

## Session start

1. Read memory before doing anything else:
   - skill/memory/MEMORY.md (index)
   - skill/memory/lessons.md (playing lessons)
   - skill/memory/changelog.md (recent tool/strategy changes)
2. Run the environment check:
   `python3 bridge/spirectl.py doctor`
   Paths are relative to the mimo-spire repo root (this skill lives in
   <repo>/skill). If doctor fails on mod files, run `bash setup/install-mod.sh`.
   If the game is not running, `python3 bridge/spirectl.py launch` starts it via
   Steam and waits for the bridge. The first modded launch shows an in-game mod
   warning — the user must click accept once; wait for the handshake after that.
3. Confirm handshake versions in doctor output. Game version drift vs the mod's
   min_game_version is a hard stop: report it, do not improvise.

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

When the run ends (game_over screen, or abandon):

1. Write a postmortem to skill/memory/runs/<YYYY-MM-DD>-<character>-floor<N>.md
   covering: result, key decisions, what worked, what killed the run, one lesson.
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
