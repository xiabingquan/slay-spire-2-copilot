# Run memory template

Every run writes one bilingual pair under `memory/runs/`:
`<run-number-4-digit-padded>_<CHARACTER>_<YYYYmmdd-HHMMSS>_<hash8>.md`
(English) +
`<run-number-4-digit-padded>_<CHARACTER>_<YYYYmmdd-HHMMSS>_<hash8>_zh.md`
(Chinese), content-aligned. The run-number prefix equals the run's 对局序号
in memory/overview.md — the lookup key for this pair.

How to fill this template (applies to every section):

- All content sections are fixed tables — fill the cells, never free-write
  around them. The only list in a run note is Summary's two gain/loss bullets.
- Each table holds at most 7 data rows. When more exist, DROP the weaker
  ones — never merge rows to combine items. Concise only: keep the strongest
  items with forward reference value for future runs.
- What went well / What went poorly / Key moments share one 类型 enum:
  - 决策 — route, shop buys, in-combat choices, potion timing (incl. acting
    before verifying available information)
  - 卡牌 — single-card picks and in-fight performance
  - 遗物 — relic acquisition and value delivered
  - 构筑 — deck/engine shape and synergy (card×relic×character), incl.
    deck preparedness for known mechanics
  - 过程 — execution discipline and tooling (one card per call, full state
    re-reads, fail-loud hits, SL usage; incl. available info unused against
    discipline)
  - 客观 — non-decision factors: draws, drops, map geometry, economy luck
- System-side gaps (incomplete state info, mechanics that contradict the
  data/skill) are defects of skill/mod/data — fix them there when found;
  never record them as run factors.
- Cells marked `e.g.` are format examples — replace them with this run's
  content, matching the same granularity. Type cells may only use the enum
  words above.

## Summary

Core facts table (fill every row):

| Field | Value |
|---|---|
| Character | e.g. IRONCLAD |
| Date | e.g. 2026-09-20 |
| Floor reached | e.g. 33 |
| Score | e.g. 1234 |
| Ascension | e.g. 2 |
| Fixed seed used | e.g. no |
| Seed | e.g. E77FN3DSSY |
| SL count | e.g. 0 |

Then exactly two unordered-list bullets — the run's single biggest gain and
single biggest loss:

- e.g. Biggest gain: Act1 A2 spine fully cleared — all three elites killed per archive doctrine, boss fell T11.
- e.g. Biggest loss: died Act2 Boss KaiserCrab T8 — Crusher STR ramp met an exhausted block package.

## Run overview

Act-by-act FACTS ONLY. No analysis, no lessons, no mechanics commentary —
those belong in the tables below. Fixed table, one row per Act reached
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

Plays and outcomes worth repeating — decisions and objective factors. Prefer
items with forward reference value for future runs over routine good
outcomes. 代价/收益 column = the gain (numbers first). 下次参考 = how to
reuse it next run.

| # | 类型 | 内容 | 代价/收益 | 下次参考 |
|---|---|---|---|---|
| 1 | e.g. 决策 | e.g. 路线草稿 1:1 执行 | e.g. 商店沉淀 275g；Elite① 以 80/80 入场 | e.g. 沉淀口继续放在精英走廊之前 |
| 2 | e.g. 遗物 | e.g. Vambrace 首挡翻倍入手并兑现 | e.g. live：Defend 5→10（四场战斗） | e.g. 挡引擎遗物优先于边际攻击牌 |
| 3 | e.g. 客观 | e.g. 全程抽牌顺畅 | e.g. 每战 T2 前引擎上线 | e.g. —（客观因素仅作参考） |

## What went poorly

Decision-level reflections and objective losses. 代价/收益 column = the
cost. 下次参考 = one advisory line for next run (never a binding pattern).

| # | 类型 | 内容 | 代价/收益 | 下次参考 |
|---|---|---|---|---|
| 1 | e.g. 过程 | e.g. 链式 bash 调用 | e.g. 千足虫战误触 Whirlwind | e.g. 一调用一动作，调用间重读 state |
| 2 | e.g. 构筑 | e.g. 单体向牌组撞 INFESTED 波次 | e.g. 波次战败，对局结束 | e.g. 波次类精英进草稿构筑检查点 |
| 3 | e.g. 决策 | e.g. 信息未核实即进战斗 | e.g. 多付税，HP 白损 | e.g. 进战前完成 lookup/档案核对 |

## Key moments

The run's turning points — HP-costly decisions, engine relics, key cards,
run-ending fights. Rows are chronological by 时机. 时机 format:
`ActN (地点/楼层)` + optional turn for elite/boss fights. 代价/收益 = the
consequence (HP swing, engine online, run over).

| # | 时机 | 类型 | 内容 | 代价/收益 | 下次参考 |
|---|---|---|---|---|---|
| 1 | e.g. Act2 (2,1) 商店 | e.g. 遗物 | e.g. 232g 买下 Vambrace | e.g. 首挡翻倍，挡引擎成型 | e.g. 挡引擎遗物优先于边际攻击牌 |
| 2 | e.g. Act2 (9,1) Elite | e.g. 决策 | e.g. 34HP 入场棱柱、跳过休息 | e.g. T4 死亡，对局结束 | e.g. 税/波次类精英前休息是硬参考线 |
| 3 | e.g. Act2 Boss (15,3) T8 | e.g. 构筑 | e.g. 力量 8 回合 28 伤 vs 5 挡 | e.g. 挡密度缺口暴露，阵亡 | e.g. 力量爬升型 Boss 需弱化免疫挡循环 |
