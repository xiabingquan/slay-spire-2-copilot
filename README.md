# mimo-spire

Claude Code skill and tooling that let an AI agent play Slay the Spire 2 on a
local machine. The agent reads live game state, makes fully autonomous decisions,
and drives the game through a self-written communication mod, with a persistent
memory and self-iteration loop across sessions and runs.

## Layout

- mod/SpireBridge — C# communication mod for STS2 (Godot 4 .NET, game v0.107.1):
  state export + command input over localhost TCP JSONL
- bridge/spirectl.py — Python CLI connecting Claude sessions to the mod
- skill/ — Claude Code skill: play loop, references, persistent memory
  (symlinked to ~/.claude/skills/slay-spire-2-copilot)
- setup/install-mod.sh — build + install the mod into the game mods folder
- docs/ — protocol spec and reverse-engineering research notes

## How it fits together

    Claude Code session (skill `slay-spire-2-copilot`)
        -> spirectl.py (TCP JSONL, 127.0.0.1:17612)
        -> mimo-spire-bridge mod inside the STS2 process
        -> MegaCrit.Sts2 game APIs (CardCmd/PlayerCmd/UI nodes)

## Architecture: client–server roles

Server = the SpireBridge mod inside the game process. It monitors game state
and returns snapshots, accepts operation commands and applies them to the game.
It makes no decisions.

Client = spirectl plus the decision layer (Claude via the spire skill). It
reads state snapshots, makes all decisions, and sends operation requests. It
never touches game internals directly.

Completeness rule: if play encounters a screen or component the server does
not support yet, implement it immediately (rebuild mod + restart game) and
continue — never skip or work around it.

## Setup

1. Build and install the mod: `bash setup/install-mod.sh`
   (requires .NET SDK 9+; game assemblies are referenced from the Steam install)
2. Launch the game: `python3 bridge/spirectl.py launch`
   First modded launch shows an in-game mod warning — accept it once.
3. Verify: `python3 bridge/spirectl.py doctor`

## Playing via Claude Code

Open a Claude Code session in this repo (the spire skill is auto-available via
the symlink) and ask it to play, e.g. "打一局杀戮尖塔2". The skill instructs
Claude to load memory, run doctor, then loop: state -> decide -> act -> wait.

## Memory and self-iteration

- logs/ — one file per run, full JSON records of every spirectl state/act/wait
  call (auto-written, rotated per run, committed as the permanent play record)
- skill/memory/lessons.md — generalizable playing lessons, pruned when wrong
- skill/memory/runs/ — per-run postmortems written after every run
- skill/memory/changelog.md — ledger of tool fixes and strategy corrections
- Tool bugs are fixed in this repo and recorded in changelog.md; the skill
  reloads the latest memory at the start of every session

## Deferred (TODO)

- Headless unattended auto-run runner (batch games for iteration data)
- STS1 CommunicationMod adapter (protocol is game-agnostic by design)
- Push-style events from the mod (v1 is poll-based)

## Reference docs

- docs/protocol.md — wire protocol v1
- docs/research/game-api-findings.md — game API surface + community-validated symbols
- skill/references/commands.md — action and state cheat sheet
