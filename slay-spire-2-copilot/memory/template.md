# Run memory template

Every run writes one bilingual pair under `memory/runs/`:
`<character>_<YYYYmmdd-HHMMSS>_<hash8>.md` (English) +
`<character>_<YYYYmmdd-HHMMSS>_<hash8>_zh.md` (Chinese), content-aligned.

How to fill this template (applies to every section):

- Prose sections use Markdown unordered lists only (`- item`). No paragraphs,
  no numbered lists.
- Each prose section holds at most 5 bullets. When more exist, merge or drop —
  keep only what has forward reference value for future runs.
- The two tables (Summary facts, Run overview) are fixed format: fill the
  cells, never free-write around them.
- Bullet lines marked `e.g.` are format examples — replace them with this
  run's content, matching the same granularity.

## Summary

Core facts table (fill every row):

| Field | Value |
|---|---|
| Character | e.g. IRONCLAD |
| Date | e.g. 2026-09-20 |
| Floor reached | e.g. 33 |
| Score | e.g. — (EA build has no score field) |
| Ascension | e.g. 2 |
| Fixed seed used | e.g. no |
| Seed | e.g. E77FN3DSSY |
| SL count | e.g. 0 |

Then exactly two bullets — the run's single biggest gain and single biggest
loss:

- e.g. Biggest gain: Act1 A2 spine fully cleared — all three elites killed per archive doctrine, boss fell T11.
- e.g. Biggest loss: died Act2 Boss KaiserCrab T8 — Crusher STR ramp met an exhausted block package.

## Run overview

Act-by-act FACTS ONLY. No analysis, no lessons, no mechanics commentary —
those belong in the sections below. Fixed table, one row per Act reached
(later Act rows stay `—` until reached). Names come from live state /
references; live Chinese names are fine.

| Act | 结局 | 精英（数量：名单） | Boss | 本 Act 获得遗物 |
|---|---|---|---|---|
| 1 | e.g. ✅ 全清 | e.g. 3：异蛙寄生虫、旧日雕像、多尼斯异鸟 | e.g. 墨影幻灵（T11 击杀） | e.g. 金色珍珠、灯笼、Vambrace |
| 2 | e.g. ❌ 死于 Boss T8 | e.g. 3：感染棱柱、蜂群术士、残杀千足虫 | e.g. 皇蟹（Crusher 剩 97/209） | e.g. Sozu、茶具、MoltenFist |
| 3 | — | — | — | — |

Cell rules:

- 结局: one line only — ✅ 全清 / ❌ 死于 <地点+敌人+回合> / ⏸️ 中止.
- 精英: count first, then the elite enemy names actually fought this act.
- Boss: boss name + kill turn, or remaining HP at death.
- 遗物: relics GAINED during that act (Neow/shop/event/elite/boss drops).

This per-run act table is not `memory/overview.md` — that file keeps the
cross-run index table (对局序号 rows) described in the user guide.

## What went well

Unordered list, at most 5 items — unexpectedly powerful plays worth
repeating; decisions AND objective factors.

- e.g. Decision: route draft executed 1:1 — shop sink 275g before Elite①, 80/80 entry HP.
- e.g. Card×relic: Vambrace first-block doubling live-verified across four fights (Defend 5→10).
- e.g. Objective: draws stayed smooth all act — engine online by T2 in every fight.

## What went poorly

Unordered list, at most 5 items — decision-level reflections and objective
losses; each item states what to reconsider next run.

- e.g. Decision: chained bash calls drifted indices — unplanned Whirlwind fired in the centipede fight.
- e.g. Build gap: no AoE vs INFESTED wave — deck shape lost the fight, not map geometry.
- e.g. Objective: 120g stranded — the last act shop sat off the chosen spine.

## Key moments

Unordered list, at most 5 items — the turning points of THIS run. One line
each, format `ActN (地点/楼层) — 事件：后果`. Cover the kinds that changed
the run's course:

- e.g. HP-costly decision: Act2 (9,1) — entered Prism elite at 34 HP, skipping the rest node: died T4 to tax stacking.
- e.g. Engine relic: Act2 (2,1) shop — bought Vambrace 232g: first-block doubling completed the block engine.
- e.g. Key card: Act2 (12,1) shop — bought Fiend Fire 147g: hand-scaled burst answered every multi-elite window.
- e.g. Run-ending fight: Act2 Boss (15,3) T8 — KaiserCrab Crusher STR 8 turn: 28 damage met 5 block.
