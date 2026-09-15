# slay-spire-2-copilot

> 中文版：[README_ZN.md](README_ZN.md)

An AI copilot that lets Claude Code / Codex play Slay the Spire 2 autonomously
on your machine. Say "play Slay the Spire 2 via Claude Code" and the agent
reads the run, decides, acts, pushes the map, fights the boss — then writes a
postmortem and starts the next run.

## What this project is

- **Autonomous runs**: live game state (HP, hand, enemy intents, map…) is read
  every turn; the AI chooses cards, rewards, and routes, driving the game
  through a communication mod
- **Continuous operation**: run end → postmortem + memory update → next run;
  an optional external watchdog script can periodically check that the game,
  bridge and run logs are alive
- **Compounding skill**: cross-run persistent memory (lessons, tool-fix
  ledger); tool bugs are fixed in this repo and take effect immediately

## How to use

1. **Build the mod** (.NET SDK 9+; game assemblies referenced from the local
   Steam install):

       cd slay-spire-2-copilot/slay-spire-2-copilot
       bash setup/install-mod.sh

2. **Launch and verify** (accept the in-game mod warning once on first launch):

       python3 bridge/spirectl.py launch
       SPIREBRIDGE_LOG_DIR=<log-folder> python3 bridge/spirectl.py doctor

3. **Start a run**: invoke the skill in Claude Code, passing an absolute **log
   folder** path:

       play Slay the Spire 2 via Claude Code  /Users/me/spire-logs/tonight

   Triggers include: "用 Claude Code 打一局杀戮尖塔2", "play Slay the Spire 2
   via Claude Code or Codex".

4. **Run logs** land in your folder as `run-<timestamp>-<hash>.log`
   (e.g. `run-20260916-013052-a3f9c012.log`).

## Directory layout

    slay-spire-2-copilot/                  (repo root)
      README.md / README_ZN.md
      .gitignore
      slay-spire-2-copilot/                (skill folder — all runtime files)
        SKILL.md                           (skill definition / invocation contract)
        bridge/                            (spirectl.py CLI, watchdog script)
        mod/SpireBridge/                   (in-game communication mod source)
        setup/                             (mod build/install script)
        docs/                              (protocol spec, API research notes)
        doc/ memory/ references/           (play knowledge, run memory, CLI cheat sheet)

Skill symlink: `~/.claude/skills/slay-spire-2-copilot` → the skill folder above.
Runtime logs and watchdog state live outside the repo in user directories.

## Technical approach

Client–server over JSON Lines on localhost TCP (127.0.0.1:17612):

    Claude Code (decision client)
      → bridge/spirectl.py (CLI: state / act / wait / sl / profile …)
      → spire-copilot-bridge mod (Godot .NET mod inside the game process)
      → game APIs (cards, turns, map, rewards, …)

- **Server (mod)**: only exports full state snapshots and applies commands
  (play / end_turn / choose / map_select / shop / …) — **zero decisions**.
  Missing screen support is implemented immediately, mod rebuilt, game
  restarted (completeness rule)
- **Client (spirectl + Claude)**: read snapshot → decide from memory → send
  ops → wait for fingerprint change → loop. Acts are submitted via
  `act --wait` / `batch`; decisions stay in the AI, logs stay in the tooling
- **Speed & stability**: in-game `FastMode=Instant` + `NonInteractiveMode`
  skip animations; content-hashed state fingerprints drive waits;
  combat-end / RINGING freezes have server-side force-advance; `sl` reloads
  the room-entry save (~18s) to replay fights with foreknowledge
- **Memory & iteration**: `memory/` lessons, postmortems and changelog update
  every run and reload next session; tool fixes land in this repo

Protocol details: `slay-spire-2-copilot/docs/protocol.md`. CLI cheat sheet:
`slay-spire-2-copilot/references/commands.md`.
