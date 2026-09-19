# User guide

User-written guidance for the agent's memory practice — consult this when
recording run memory.

## What to cover when recording memory

Start from these aspects — each maps to a lessons/ category file:

- Character traits → `memory/lessons/characters.md`
- Card traits → `memory/lessons/cards.md`
- Relic traits → `memory/lessons/relics.md`
- Cross-element synergies (card×card, card×relic, …) → `memory/lessons/synergies.md`
- Enemy doctrines, events, economy, combat principles → the matching
  lessons file

Pay special attention to interactions among elements — such synergies can
make an entire deck powerful; they are the focus of recording.

Mechanics facts (what a card/relic/enemy DOES) live in the programmatic
store `bridge/spirectl_lib/data/`: resolve any id via
`spirectl lookup <id>` — the store carries structured fields only
(schema: `bridge/spirectl_lib/schema.py`, codex is the authoritative
structure source). Doctrine, usage notes and prose never go into the store;
they belong in lessons.

## Information awareness in review

Information questions route by nature — they are not a standalone run-note
dimension:

- Information genuinely missing or unclear in state → skill/mod/data
  defect: fix it where it lives (same session); never record it as a run
  factor
- Information available but unused (data/lookup, state fields, archive
  notes) → classify by what failed:
  - process: discipline violations — pre-fight lookup not done, state not
    re-read before acting (goes in the run note's What went poorly table,
    类型 = 过程)
  - decision: acting before verifying available information (类型 = 决策)
- Structured facts always resolve via lookup first; a lookup miss is a
  research trigger — fold codex structure into data (schema-strict) —
  never permission to guess

## Accumulating beneficial experience

The core goal of run memory is accumulating experience that supports later
runs' decisions. The note format is fixed by `memory/template.md`:
What went well / What went poorly / Key moments are tables —
`# | [时机 |] 类型 | 内容 | 代价/收益 | 下次参考` — each at most 7 rows;
over the cap, DROP the weaker rows, never merge rows to combine items.
Type cells use the shared enum only:

- 决策 — route, shop buys, in-combat choices, potion timing (incl. acting
  before verifying available information)
- 卡牌 — single-card picks and in-fight performance
- 遗物 — relic acquisition and value delivered
- 构筑 — deck/engine shape and synergy (card×relic×character), incl.
  deck preparedness for known mechanics
- 过程 — execution discipline and tooling (one card per call, full state
  re-reads, fail-loud hits, SL usage; incl. in-hand info unused against
  discipline)
- 客观 — non-decision factors: draws, drops, map geometry, economy luck

In "What went well", record plays and outcomes worth repeating — prefer
items with forward reference value over routine good outcomes; the
代价/收益 column holds the gain.
In "What went poorly", record decision-level reflections and objective
losses; 代价/收益 holds the cost, and 下次参考 is one advisory line for
next run.

## Decisions and objective factors

Both tables cover decisions AND objective factors — objective positives
(e.g. smooth draws all run) go to What went well, objective negatives
(e.g. poor relic offerings) to What went poorly; classify each row under
the shared enum (决策 / 客观 / others as content dictates).

## Per-character core playstyles

Character-level accumulation lives in `memory/lessons/characters.md` — one
H1 heading per character; experience written as unordered bullets under
each heading: win condition, key relics/cards the character wants, build
spines. Run notes do not carry this standing knowledge; lessons is its home.

## Summary contents

In the Summary section of each run note, besides the core-facts table, write
exactly two bullets covering the run's biggest gain and biggest loss:

- The single biggest win of the run
- The single biggest loss of the run

The facts-table format itself (fields incl. Date) is defined in
`memory/template.md`.

## Overview table rules

Every run must also be recorded in `memory/overview.md`, following these
rules:

- Column order: **对局序号** | 角色 | 日期 | **进阶** | 到达楼层 | 胜负 | SL 次数 | 备注
- The **对局序号** column numbers runs chronologically from 1; the newest run
  sits at the TOP of the table and carries the highest number
- The 进阶 (Ascension) column holds a **bare number only** (0, 1, 2, …) —
  the ascension level the run was actually played at
- **Newest run goes at the TOP of the table** (reverse chronological
  order); when appending a new run, insert its row at the top — never at
  the bottom
- The 备注 cell stays meta: one line of outcome/death cause. Narrative and
  lessons go in the run's memory/runs/ note, or in the `# 阶段性反思`
  section — never in the table cells
- 备注只写最简单的信息，范例：`Act3 全清 → 到达建筑师（本存档首次 Act3 通关）`、`死于 Act2 Boss 知识恶魔（剩 91/379）`
- The ascension recorded in the run note's Summary table, the memory
  remark, and the overview row must all match

## Phased reflection (阶段性反思)

`memory/overview.md` carries a top-level `# 阶段性反思` section; each
reflection is one `## 反思 (yyyy-mm-dd)` subsection under it.

- **First reflection**: covers ALL runs recorded so far
- **Every reflection after that**: covers the 20 runs since the previous one
  (second covers runs 36–55, third 56–75, …) — fire it when the cumulative
  run count reaches that boundary
- Source material: the run notes under memory/runs/ for the covered runs —
  read them, then reflect on gains and losses in structured form (markdown
  tables, ordered/unordered lists)
- This is the only place in overview.md where lessons may appear

## SL count

Every run note should record the run's SL (save/load) count — the number of
times the run was restored via `continue_run` / game relaunch mid-run (0 if
the game process held the whole run). Record it in BOTH places:

- The run note's Summary table (`SL count` field) — plus a one-line note of
  what was SL'd and why when the count is > 0
- The overview.md table (`SL 次数` column) for that run's row

Count rule: each `continue_run` after a game-process interruption = +1. A
fresh `start_run` begins a new count. For runs recorded before this rule
existed, mark the overview cell 未记录 unless a memory note already documents
the number.

## When to consult memory

Memory is consulted throughout the whole play process — it is a standing
reference for the game, not only a session-start artifact:

- **Mandatory at session/run start: `overview.md` only** — the table, stats
  and phased reflections give the standing cross-run picture; full per-run
  notes are generally NOT needed at start
- **`lessons/` is the standing experience layer** — consult mid-run whenever
  a decision benefits: enemy doctrines (lessons/enemies.md), synergies
  (lessons/synergies.md), character spines (lessons/characters.md), etc.
  Mechanism numbers still resolve via `spirectl lookup <id>` first
- **On demand**: to read one run's complete record, open that single note —
  files carry a run-number prefix (`0051_IRONCLAD_...`) equal to the 对局序号
  column in overview.md; look the number up there, then read the file
- Any time during play: consult specific run notes or character accumulations
  mid-run when a decision would benefit from them

## Experience is advisory, not binding

When recording run memory, frame lessons for future runs as **suggestions /
reference observations**, not as binding patterns:

- Wording: prefer "建议… / 参考… / run-X observed…" over "强烈建议 / 强烈建议不要"
- **All past runs are reference only.** Concrete in-run measures must be decided
  from the **current run's live state** (HP, deck, hand, enemy, map geometry),
  not copied wholesale from earlier run notes or lessons
- Past experience is one input to the decision; live situation always wins
- The same applies when consulting memory mid-run: read past notes and
  lessons as data, then adapt — do not replay another run's script

## Phased reflection must cover frequent-death enemies

In the 阶段性反思 section of `memory/overview.md`, in addition to existing
gains/losses analysis:

- Identify **high-frequency failure enemies** (enemies that killed multiple runs)
  within the covered run range
- For each: summarize the **root cause** of the deaths (mechanic misunderstanding?
  HP-entry math? draw/deck issue? process debt?)
- Think through **countermeasures** — framed as advisory suggestions for future
  runs (not binding patterns), to be adapted per live situation; standing
  conclusions graduate into `memory/lessons/enemies.md`

## Only forward-valuable content in memory

Overarching rule for run notes and overview: **record only what has reference
value for FUTURE runs**.

- **Delete revenge-type narrative** ("run-X killer now killed", 复仇 items) —
  beating a previously-fatal enemy carries no forward reference value
- **Delete mod-fix/process-reload narrative** (版本号、重建、工具缺陷重载过程) —
  engineering log, not play reference
- overview table 备注 and reflections: same standard — only future-valuable
  facts
- What survives: verified mechanics as structured facts (live in
  spirectl_lib/data via lookup), cost/HP economy data, synergies,
  decision-quality observations, advisory suggestions — the latter groups
  belong in lessons and run-note tables

## Play principles for future reference

Advisory principles for future runs — adapt to live situation per run:

- **HP is a premier resource, and its priority value shifts by turn/phase.**
  Treat HP as the scarcest currency whose exchange rate changes over the
  fight: early/low-threat turns HP is cheap to spend; razor turns and
  boss-tax windows it is priceless. Weigh every HP payment against what
  that specific turn buys (建议性 — live HP line, incoming intents and
  remaining fight length decide the rate each turn).
- **Early turns: engine-online is the top priority.** In the opening
  turns of a fight, getting powers/engines equipped (Inferno, Vicious,
  poison, Inflame-class, block engines) outranks marginal damage or
  minor HP conservation — engines compound over the whole fight, early
  chip damage does not. Spending early HP to land engine pieces is often
  the right trade; the exact amount remains a live judgment.
