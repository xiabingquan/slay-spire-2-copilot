# slay-spire-2-copilot

> 中文版：[README_ZN.md](README_ZN.md)

Claude Code / Codex skill and tooling that let an AI agent play Slay the Spire 2
on a local machine. The agent reads live game state, makes fully autonomous
decisions, and drives the game through a self-written communication mod, with a
persistent memory and self-iteration loop across sessions and runs.

## Layout

    slay-spire-2-copilot/                  (repo root)
      README.md
      .gitignore
      slay-spire-2-copilot/                (skill folder — all runtime files)
        SKILL.md                           (skill definition / invocation contract)
        bridge/spirectl.py                 (Python CLI: state/act/wait/sl/…)
        bridge/watchdog-external.sh        (crontab liveness watchdog)
        mod/SpireBridge/                   (C# communication mod source + manifest)
        setup/install-mod.sh               (build + install mod into the game)
        docs/                              (protocol spec + API research notes)
        doc/                               (playing knowledge: cards/potions/…)
        memory/                            (lessons, changelog, run postmortems)
        references/commands.md             (CLI + state cheat sheet)

The Claude Code skill symlink points at the skill folder:

    ~/.claude/skills/slay-spire-2-copilot -> <repo>/slay-spire-2-copilot/slay-spire-2-copilot

Runtime artifacts never live in the repo: run logs are written under
`SPIREBRIDGE_LOG_DIR` (a user-supplied **folder**, files named
`run-<timestamp>-<hash>.log`), watchdog/notify state under
`~/.local/share/slay-spire-2-copilot/`.

## How it fits together

    Claude Code session (skill `slay-spire-2-copilot`)
        -> bridge/spirectl.py (TCP JSONL, 127.0.0.1:17612)
        -> spire-copilot-bridge mod inside the STS2 process
        -> MegaCrit.Sts2 game APIs (CardCmd/PlayerCmd/UI nodes)

## Architecture: client–server roles

Server = the SpireBridge mod inside the game process. It monitors game state
and returns snapshots, accepts operation commands and applies them to the game.
It makes no decisions.

Client = spirectl plus the decision layer (Claude via the skill). It reads
state snapshots, makes all decisions, and sends operation requests. It never
touches game internals directly.

Completeness rule: if play encounters a screen or component the server does
not support yet, implement it immediately (rebuild mod + restart game) and
continue — never skip or work around it.

## Setup

All commands below run from the skill folder `slay-spire-2-copilot/slay-spire-2-copilot`:

1. Build and install the mod: `bash setup/install-mod.sh`
   (requires .NET SDK 9+; game assemblies are referenced from the Steam install)
2. Launch the game: `python3 bridge/spirectl.py launch`
   First modded launch shows an in-game mod warning — accept it once.
3. Verify: `SPIREBRIDGE_LOG_DIR=<log-folder> python3 bridge/spirectl.py doctor`

## Playing via Claude Code

Open a Claude Code session and invoke the skill, e.g. "用 Claude Code 打一局杀戮尖塔2"
or "play Slay the Spire 2 via Claude Code or Codex", passing an absolute **log
folder** path. The skill instructs Claude to load memory, run doctor, arm the
watchdog, then loop: state -> decide -> act -> wait.

## Memory and self-iteration

- `slay-spire-2-copilot/memory/lessons.md` — generalizable playing lessons
- `slay-spire-2-copilot/memory/runs/` — per-run postmortems
- `slay-spire-2-copilot/memory/changelog.md` — ledger of tool fixes and strategy
  corrections; tool bugs are fixed in this repo and recorded there

## Deferred (TODO)

- Headless unattended auto-run runner (batch games for iteration data)
- STS1 CommunicationMod adapter (protocol is game-agnostic by design)
- Push-style events from the mod (v1 is poll-based)

## Reference docs

- `slay-spire-2-copilot/docs/protocol.md` — wire protocol v1
- `slay-spire-2-copilot/docs/research/game-api-findings.md` — game API surface
- `slay-spire-2-copilot/references/commands.md` — action and state cheat sheet
