<div align="center">

https://github.com/user-attachments/assets/6eae44a2-312d-4a1c-abc3-f5617fe23f21

</div>

> Chinese (default README): [README.md](README.md)

# slay-spire-2-copilot

A skill that loads directly into agent harnesses like Claude Code or Codex,
letting the agent play Slay the Spire 2 autonomously on your machine. Once
the skill is triggered, the agent reads the run state, makes decisions, and
operates the game until the run ends — then writes the run's memory note
(Summary + review) and starts the next run.

## Current best records

| Character | Record |
|---|---|
| <img src="assets/characters/character_icon_ironclad.webp" alt="IRONCLAD" width="28"> | Ascension 0 ✅ |
| <img src="assets/characters/character_icon_silent.webp" alt="SILENT" width="28"> | N.A. |
| <img src="assets/characters/character_icon_defect.webp" alt="DEFECT" width="28"> | N.A. |
| <img src="assets/characters/character_icon_necrobinder.webp" alt="NECROBINDER" width="28"> | N.A. |
| <img src="assets/characters/character_icon_regent.webp" alt="REGENT" width="28"> | N.A. |

## What this project is

- **Autonomous runs**: live game state (HP, hand, enemy intents, map, …) is
  read every turn; the AI chooses cards, rewards, and routes, operating the
  game through a communication mod
- **Continuous operation**: after a run ends it automatically writes the
  run's memory note and starts the next run; the bundled external watchdog
  script can periodically check that the game process, bridge, and logs are
  alive
- **Cross-run memory**: run memory notes under `memory/` (summaries,
  per-character playstyles) auto-load in later sessions; tool defects are
  fixed in this repo and take effect on the next run

## How to use

Invoke the skill in Claude Code with an absolute log folder path:

    play Slay the Spire 2 via Claude Code  /Users/me/spire-logs/nightly

Triggers (Chinese or English): "用 Claude Code 打一局杀戮尖塔2", "play Slay the
Spire 2 via Claude Code or Codex".

Run logs are written to the given folder as `run-20260916-013052-a3f9c012.log`
(timestamp + hash).

## Directory layout

    slay-spire-2-copilot/                  (repo root)
      README.md / README_EN.md
      doctor.md                            (documentation health-check checklist)
      .gitignore
      slay-spire-2-copilot/                (skill folder — all runtime files)
        SKILL.md                           (skill definition / invocation contract)
        bridge/                            (spirectl.py CLI)
        scripts/                           (shell scripts: mod install, watchdog)
        mod/SpireBridge/                   (in-game communication mod source)
        references/bridge/                 (CLI cheat sheet, wire protocol)
        spirectl_lib/data/                   (characters/cards/powers/relics/potions/afflictions/intents/monsters/events — EN+ZH JSON pairs keyed by live game ids; markdown twins retired after verification)
        memory/                            (run memory: user guide, per-run notes)

Skill symlink: `~/.claude/skills/slay-spire-2-copilot` → the skill folder above.

Doc health check: [doctor.md](doctor.md) at the repo root is a
documentation-organization checklist — README stays a project overview;
`mod/` and `bridge/` stay code-only; run memory is written only under
`memory/runs/`; `spirectl_lib/data/` keeps static material only; docs carry no
user-conversation content (comments, requests, improvement asks); docs don't
mix languages (Chinese docs stay Chinese, English docs stay English). How to
run: have the agent execute the checklist (e.g. "run doctor.md") and fix
violations. When to run: after each run ends, before committing documentation
changes, or whenever files look misplaced.

## Acknowledgements

Modding projects (community reference implementations):

- [BaseLib-StS2](https://github.com/Alchyr/BaseLib-StS2) — Alchyr's Slay the Spire 2 modding base library; reference for mod loading and game API conventions
- [CombatSolver](https://github.com/Torch1230/CombatSolver) — combat route solver mod; structured data reference for card/relic/power effects
- [STS2-Agent](https://github.com/CharTyr/STS2-Agent) — in-game AI companion mod; monster behaviors, events, and game-knowledge extraction reference
- [slay-the-streamer-2](https://github.com/Surfinite/slay-the-streamer-2) — Twitch chat voting mod; modding API and UI-flow research reference
- [sts2-game-mod](https://github.com/AI-Ascension/sts2-game-mod) (AI-Ascension) — Rust-interop mod; game interface and experiment records reference

Databases and wikis (reference-doc data sources):

- [Spire Codex](https://spire-codex.com) — card/relic database (577 cards, 296 relics)
- [slaythespire2.net](https://slaythespire2.net) — CN/EN codex for cards/relics/potions/monsters/events (main source for Simplified Chinese names)
- [sts2.gg](https://sts2.gg) — per-character card database (CN names)
- [stratgg.com](https://www.stratgg.com) — per-character card and potion databases
- [mobalytics](https://mobalytics.gg/slay-the-spire-2) — card wiki
- [sts2-wiki.org](https://sts2-wiki.org) / [sts2.wiki](https://sts2.wiki) — status-effect numerics
- [gamerblurb](https://gamerblurb.com) — status-card list
- [untapped.gg](https://sts2.untapped.gg) — card costs and rarities
- [sts2guide.com](https://sts2guide.com), [IGN wiki](https://www.ign.com/wikis/slay-the-spire-2/), [Gamersky](https://www.gamersky.com/z/slaythespire2/), [huijiwiki](https://sts.huijiwiki.com), [namu.wiki](https://namu.wiki) — guides and name references
