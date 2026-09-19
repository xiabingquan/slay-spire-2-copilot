# User guide

Memory-writing guidance — four points: formats, when to write, when to
consult, and remarks.

## 格式 Formats

- Per-run notes (the EN+`_zh` pair under `memory/runs/`): format per
  `memory/template.md`
- Cross-run overview (`memory/overview.md`): two sections — `## 对局表`
  (run table; rules in its 表格规则 block) and `## 统计` (crosstab
  statistics, recounted from the run table)

## 写入时机 When to write

- **Run note + overview row + statistics**: written immediately at every
  run end — the note pair under `memory/runs/`, one row inserted at the TOP
  of the overview.md run table, and the `## 统计` crosstabs (战绩总览 /
  进阶进度) recounted from the table
- **Phased reflection**: cadence unchanged — the first one covers ALL runs
  recorded so far; every later one covers the 20 runs since the previous
  (36–55, 56–75, …), fired when the cumulative run count reaches the
  boundary. Output goes DIRECTLY into the matching `memory/lessons/*.md`
  category files — never into overview.md — and **every entry carries its
  date**. overview.md holds only overall run results (the table); no
  experience content lives there
- **lessons/**: forward-valuable experience from the run and from phased
  reflections is written into the matching category file — an item that maps
  one-to-one to an inventory-table row goes INTO that row's experience cell
  (still as a `- (date) …` list item); anything without a unique row stays
  as an unordered-list item after the table. Reflection-derived items are
  dated per entry

## 查阅时机 When to consult

- **At session/run start — general experience**: read `overview.md`
  (cross-run picture) plus the general lessons categories — combat
  principles, synergies, character spines
- **Before EVERY decision — that decision's past experience**: consult the
  matching lessons file (and lookup for mechanics numbers) before acting:
  - Relic pick → `lessons/relics.md` — does this relic have known tricks
  - Route choice → `lessons/route.md`
  - Event-room choice → `lessons/events.md`
  - Shop / economy decision → `lessons/economy.md`
  - Entering a fight → `lessons/enemies.md` (that enemy's doctrine) +
    `spirectl lookup <id>` (mechanics: moves/intents/hp — structured facts)
  - Card pick / build pivot → `lessons/cards.md`, `lessons/synergies.md`,
    `lessons/characters.md`
- **Single run note on demand**: file-name prefix equals the 对局序号 column
  in overview.md — look the number up, then open the note
- Principle: every decision starts with a lookup of prior experience; never
  decide from impressions alone. Consult only the MINIMAL necessary content:
  before each decision open just the one lessons entry / lookup directly
  relevant to it — never browse wholesale

## 备注 Remarks

- Experience is advisory, not binding: word lessons as 建议 / 参考, never
  as 强烈建议 / 强烈建议不要
- All past runs are reference only — in-run measures follow the current
  run's live state (HP, deck, hand, enemy, map geometry); live always wins.
  When consulting mid-run, read past experience as data and adapt; never
  replay another run's script
- Only forward-valuable content is recorded or distilled: revenge narrative
  and process/mod-fix logs never enter memory
- Mechanics facts are not memorized anywhere: resolve via
  `spirectl lookup <id>` (the data store is programmatic, codex
  authoritative). System-side defects get fixed where they live — never as
  run factors
