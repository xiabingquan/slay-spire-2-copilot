# User guide

User-written guidance for the agent's memory practice — consult this when
recording run memory.

## What to cover when recording memory

Start from these aspects:

- Character traits
- Card traits
- Relic traits
- ... and similar game elements

Pay special attention to the interactions among them:

- Card × card combinations
- Card × relic combinations
- ... and similar cross-element synergies

Such synergies can make an entire deck extremely powerful — they are the
focus of recording.

## Information awareness in review

When reviewing a run, pay special attention to information awareness —
information that was available but never utilized:

- e.g. the current floor's available map routes (all selectable paths shown
  on the map)
- ... and similar state information the bridge exposed but the run failed to
  leverage

## Accumulating beneficial experience

The core goal of run memory is to accumulate correct experience that supports
decisions in later runs. Emphasize these two sections:

In "What went well", focus on unexpectedly powerful plays:

- e.g. a card that played an unexpected role
- e.g. a relic that delivered unexpected value
- ... and similar positive outcomes worth repeating

In "What went poorly", focus on decision-level reflections:

- e.g. which card was picked (and why it underperformed)
- e.g. which route was taken (and what it cost)
- ... and similar choices to reconsider next run

## Decisions and objective factors

"What went well" and "What went poorly" are not limited to subjective
decisions — they should objectively reflect both the decisions made and the
run's circumstances:

- Objective positives belong in "What went well" — e.g. draws were smooth
  all run
- Objective negatives belong in "What went poorly" — e.g. relic offerings
  were poor, or draws never came together
- Decision-level items (picks, routes) belong there as well, per the
  previous section

## Per-character core playstyles

Accumulate the core playstyle of each distinct character, along with the key
relics and cards that character wants:

- The character's core playstyle — how it wins fights
- Key relics the character is looking for
- Key cards the character is looking for
- ... and similar per-character build knowledge

## Summary contents

In the Summary section of each run note, besides the core-facts table, write
one or two sentences covering the run's biggest gain and biggest loss:

- The single biggest win of the run
- The single biggest loss of the run

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

Every run note MUST record the run's SL (save/load) count — the number of
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

- Mandatory before each run: the Summary sections of all recorded runs, plus
  the accumulated key playstyles of the character about to play
- Optional before the run: full earlier run records, as needed
- Any time during play: consult past summaries and character notes mid-run —
  e.g. to compare with previous runs when facing a decision
