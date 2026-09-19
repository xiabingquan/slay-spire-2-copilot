# User guide

Memory-writing guidance: where the formats are defined, what to record, and
the standing directives for reflection timing / advisory framing / when to
consult memory.

## Formats

Formats are not restated here — follow the designated documents:

- Per-run notes (the EN+`_zh` pair under `memory/runs/`): format per
  `memory/template.md` — Summary facts table, Run overview act table, and
  the What went well / What went poorly / Key moments tables
- Cross-run overview table, phased reflections, SL column: rules per
  `memory/overview.md` itself (its 表格规则 block and 阶段性反思 section)

## What to record

- Forward value only: content that helps future runs' decisions — revenge
  narrative and process/mod-fix logs never belong in memory
- In the run-note tables: worth-repeating plays, decision-level losses, and
  turning points — decisions and objective factors both
- In `memory/lessons/`: standing cross-run experience — character spines,
  enemy doctrines, synergies, events/economy/combat notes (one file per
  category; experience cells filled as advisory bullets)
- Mechanics facts are not recorded anywhere: resolve them via
  `spirectl lookup <id>` — the data store is programmatic (codex
  authoritative). System-side defects get fixed where they live; they are
  never run factors

## Phased reflection timing (阶段性反思触发时机)

- The **first** reflection covers ALL runs recorded so far
- **Every reflection after that** covers the 20 runs since the previous one
  (second covers runs 36–55, third 56–75, …) — fire it when the cumulative
  run count reaches that boundary

## Experience is advisory, not binding

- Wording: prefer 建议 / 参考 / run-X observed… over 强烈建议 / 强烈建议不要
- **All past runs are reference only.** In-run measures must be decided from
  the current run's live state (HP, deck, hand, enemy, map geometry), never
  copied wholesale from earlier notes or lessons
- Past experience is one input; the live situation always wins — when
  consulting memory mid-run, read past notes as data and adapt, do not
  replay another run's script

## When to consult memory

- **Mandatory at session/run start: `overview.md` only** — the table, stats
  and phased reflections give the standing cross-run picture; per-run notes
  are generally not needed at start
- **`lessons/` mid-run** whenever a decision benefits — enemy doctrines,
  synergies, character spines; mechanism numbers resolve via
  `spirectl lookup <id>` first
- **Single run note on demand**: file names carry the 对局序号 prefix
  (`0051_IRONCLAD_...`) matching the overview.md column — look the number
  up there, then open the file
- Any time during play when a decision would benefit from historical records
