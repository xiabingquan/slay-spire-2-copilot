# slay-spire-2-copilot

> 中文版：[README_ZN.md](README_ZN.md)

An AI copilot that lets Claude Code / Codex play Slay the Spire 2 autonomously
on your machine. Once the skill is triggered, the agent reads the run state,
makes decisions, and operates the game until the run ends — then writes a
postmortem and starts the next run.

## What this project is

- **Autonomous runs**: live game state (HP, hand, enemy intents, map, …) is
  read every turn; the AI chooses cards, rewards, and routes, operating the
  game through a communication mod
- **Continuous operation**: after a run ends it automatically writes a
  postmortem, updates the experience store, and starts the next run; the
  bundled external watchdog script can periodically check that the game
  process, bridge, and logs are alive
- **Cross-run memory**: play data lives under `memory/` as local, untracked
  files and auto-loads in later sessions; tool defects are fixed in this repo
  and take effect on the next run

## How to use

Invoke the skill in Claude Code with an absolute log folder path:

    play Slay the Spire 2 via Claude Code  /Users/me/spire-logs/tonight

Triggers (Chinese or English): "用 Claude Code 打一局杀戮尖塔2", "play Slay the
Spire 2 via Claude Code or Codex".

After the skill starts it prepares the environment and begins the run: it checks
whether the mod is installed, builds and installs it when missing or when
sources are newer than the installed dll (dotnet build; output copied into the
game's mods folder), launches the game via Steam if it is not running, and
completes the bridge handshake through doctor before entering the play loop.
On the first modded launch, the game shows a one-time in-game mod warning that
must be accepted inside the game.

Run logs are written to the given folder as `run-20260916-013052-a3f9c012.log`
(timestamp + hash).

Manual commands for troubleshooting and intervention:

    cd slay-spire-2-copilot/slay-spire-2-copilot
    bash scripts/install-mod.sh                     # build/install mod
    python3 bridge/spirectl.py launch               # launch the game
    SPIREBRIDGE_LOG_DIR=<log-folder> python3 bridge/spirectl.py doctor

## Directory layout

    slay-spire-2-copilot/                  (repo root)
      README.md / README_ZN.md
      .gitignore
      slay-spire-2-copilot/                (skill folder — all runtime files)
        SKILL.md                           (skill definition / invocation contract)
        bridge/                            (spirectl.py CLI)
        scripts/                           (shell scripts: mod install, watchdog)
        mod/SpireBridge/                   (in-game communication mod source)
        references/                        (CLI cheat sheet, wire protocol, play knowledge)
        memory/                            (run memory — local, untracked)

Skill symlink: `~/.claude/skills/slay-spire-2-copilot` → the skill folder above.
Runtime logs and watchdog state are written to user directories outside the
repo and are not committed.

## Technical approach

The architecture is client–server; the protocol is JSON Lines over TCP on
localhost (127.0.0.1:17612):

    Claude Code (decision client)
      → bridge/spirectl.py (CLI: state / act / wait / sl / profile …)
      → spire-copilot-bridge mod (Godot .NET mod inside the game process)
      → game APIs (cards, turns, map, rewards, …)

- **Server (mod)**: does only two things — export complete state snapshots
  and apply commands issued by the client (play / end_turn / choose / shop, …);
  it makes no decisions. If a screen is unsupported, support is implemented on
  the spot, the mod rebuilt, and the game restarted
- **Client (spirectl + Claude)**: read snapshot → decide from memory → send
  ops → wait for state change → loop; acts are submitted in batches via
  `act --wait` / `batch`, keeping decisions decoupled from logging
- **Speed & stability**: in-game `FastMode=Instant` + `NonInteractiveMode`
  skip animations; waits are driven by state fingerprint hashes; combat-end /
  RINGING freezes have server-side forced advance, plus `sl` save reload
  (~18s, used to replay a fight with foreknowledge)
- **Memory & iteration**: lessons, postmortems, and changelog under `memory/`
  update with each run and auto-load next session; memory stays local and
  untracked, while tool fixes land directly in this repo

For the detailed protocol see `slay-spire-2-copilot/references/protocol.md`;
for the CLI cheat sheet see `slay-spire-2-copilot/references/commands.md`.

## Acknowledgements

- [BaseLib-StS2](https://github.com/Alchyr/BaseLib-StS2) — Alchyr's Slay the
  Spire 2 modding base library; consulted as a community reference for mod
  loading and game API conventions while developing SpireBridge
