# doctor.md — Documentation Health Check

A checklist for keeping this repository's documentation where it belongs. The
agent executes it against the working tree: walk every section, report
violations with file paths, then fix what the rules settle unambiguously.

## How to run

Ask the agent in the current session to execute this checklist, e.g.:

    run doctor.md

The agent goes through each check below and, for every violation:

- **relocates or deletes** content that clearly breaks a rule — e.g. run
  residue inside `spirectl_lib/data/` is deleted, run memory found outside
  `memory/runs/` is moved into the matching runs note;
- **reports, without touching**, anything ambiguous (frozen-file edits,
  borderline README wording) so the user decides.

## When to run

- **After a run ends**, once the run's memory note has been written — catches
  notes that landed outside `memory/runs/` and overview drift.
- **Before committing any documentation change.**
- **Whenever the layout looks off** — a markdown file appeared in a code
  directory, a reference doc mentions a date, etc.

Do not run it mid-run for reorganization; mid-run the only applicable check is
that additions to `spirectl_lib/data/` stay static (check 4).

## Checks

### 1. README is a project overview only

Files: `README.md`, `README_EN.md`

Rule: the READMEs describe what the project is, how the repository is laid
out, and how to load the skill. They must not contain skill-run content — no
play narratives, run dates, per-run outcomes, lessons learned, or experience
notes. That material belongs in the skill's `memory/` (check 3) or, if static,
in code-adjacent homes (`bridge/docs/`, `bridge/spirectl_lib/data/`).

Violation → move the material into the appropriate `memory/runs/` note (or
drop it if it duplicates one) and restore overview-only wording.

### 2. mod/ and bridge/ are code-only

Paths: `slay-spire-2-copilot/mod/`, `slay-spire-2-copilot/bridge/`

Rule: these are code directories — the in-game communication mod and the
`spirectl` CLI. Canonical companions only: `bridge/docs/` (tool usage and
protocol) and `bridge/spirectl_lib/data/` (game reference data). No other
non-code content: no stray `.md` notes, design write-ups, or run logs.

Violation → delete if redundant; otherwise relocate: bridge/mod development
notes → `bridge/docs/` or `proposal.md`; run narratives →
`memory/runs/`.

### 3. memory/ and code-adjacent docs have separate duties

`memory/` records what happened in runs; code-adjacent homes hold material
the agent consults while playing — `bridge/docs/` (tooling usage/protocol)
and `bridge/spirectl_lib/data/` (game reference data). Content never
crosses between them.

#### 3a. Per-run memory lives only in memory/runs/

All run memory is written to the run's own markdown file(s) under
`slay-spire-2-copilot/memory/runs/` — and nowhere else. Not in
`bridge/docs/`, not in `SKILL.md`, not in the READMEs, not in `mod/`,
`bridge/`, or `scripts/`.

Violation → move the content into the matching `memory/runs/` note, then
remove it from the wrong location.

#### 3b. template.md and user_guide.md are frozen mid-run

`memory/template.md` and `memory/user_guide.md` define how run notes are
recorded. They must not be modified while a run is in progress.

Violation → revert the mid-run edit; surface the proposed change to the user
instead of keeping it.

#### 3c. overview.md is post-run; the run table is meta-only

`memory/overview.md` is updated only after a run ends. Its run table records
only meta information — 对局序号 (chronological run number), character, date,
ascension, floor, outcome, SL count, and a one-line outcome/death remark.
No narrative and no lessons inside the table cells.

Diagnostics for the table:

- **Column order** is 对局序号 | 角色 | 日期 | 进阶 | 到达楼层 | 胜负 | SL 次数 |
  备注; the 进阶 cell holds a **bare number** (0, 1, 2, …) only — no
  prefixes, no extra text.
- **Row order**: the newest run sits at the **TOP** with the highest 对局序号
  (reverse chronological order). New runs are inserted at the top —
  appending at the bottom is a violation.
- **备注 cells hold only the simplest outcome facts** — at most one clearance
  clause plus one death clause:
  - Win: `ActX 全清 → 到达建筑师（optional milestone tag）` — e.g.
    `Act3 全清 → 到达建筑师（本存档首次 Act3 通关）`
  - Loss: `死于 ActX <Boss/精英/走廊> <敌人>（剩 x/y 或入场 HP）` — e.g.
    `死于 Act2 Boss 知识恶魔（剩 91/379）`; a short clearance summary may
    precede it — e.g. `Act1+Act2 双章全清；死于 Act3 电球头 T3（16HP 入场）`
  - Parenthetical holds simple numbers/milestones only: enemy remaining HP,
    entry HP, kill turn, first-kill / ascension / run-first tags
- **备注 violations**: process-debt tallies, death-cause analysis or
  lessons, run-XXX cross-references, card/relic names, shop-sink
  percentages, mechanics commentary — any of these inside a cell.

Phased reflections do NOT live in overview.md: reflection output is written
into memory/lessons/ category files as dated unordered-list items
(user_guide.md 写入时机); overview.md holds only overall run results.

Violation → move narrative content out of the table cells into that run's
`memory/runs/` note (or, if it is reflection material, into the matching
`## 反思` subsection); rewrite 备注 cells that fail the format down to
simplest outcome facts; fix column/row-order violations in place.

### 4. spirectl_lib/data/ is static reference material

Files: `slay-spire-2-copilot/spirectl_lib/data/*.json` + `*_zh.json` — EN and
`_zh` pairs for cards, relics, powers, potions, afflictions, monsters, events,
intents, and characters. (Schema: `bridge/spirectl_lib/schema.py`.)

Rule: purely programmatic reference data — humans never read these files.
Every entry is `id / kind / name / aliases / detail`; the per-kind `detail`
shapes are defined as dataclasses in `bridge/spirectl_lib/schema.py` and
enforced strictly by `--check` (no defaults; missing/extra/mistyped keys
hard-fail). spire-codex.com is the authoritative structure source: lookup
misses fold structure in directly. Prose (descriptions, play notes,
doctrine) never lives here — it belongs in memory/lessons and run notes.
EN and ZH twins share id/kind/aliases/detail; only `name` differs by
language. Entries must never contain run records, dates, or session notes.

Violation → delete the run-specific content; it belongs in `memory/runs/`,
not here.

### 5. No user-conversation content

Rule: documentation must not record anything from user conversations — the
user's comments, requests, improvement asks, or any paraphrase of what was
said in a session. Docs describe the project, the game, and what happened in
runs; they never describe the dialogue that produced them. This holds
everywhere: READMEs, SKILL docs, `memory/`, `bridge/docs/`.

Violation → strip the conversational framing. Keep an underlying fact only if
it already belongs under that doc's duty (checks 1–4); delete pure dialogue
residue.

### 6. No language mixing

Rule: every document has one working language and should stay in it. Chinese
docs (`README.md`, `SKILL_zh.md`, `*_zh.md`) stay Chinese; English docs
(`README_EN.md`, `SKILL.md`, `doctor.md`, non-`_zh` counterparts) stay
English. Prose must not drift mid-document — no English sentences inside a
Chinese doc, no Chinese paragraphs inside an English one.

Exempt (may stay in source form inside either language): code identifiers,
game ids and proper nouns (e.g. `IRONCLAD`, `BURNING_BLOOD`, card names that
must match game data), file paths, and CLI output. The rule governs prose,
not terminology that has to stay canonical.

Violation → translate the stray prose into the doc's working language; leave
identifiers, game names, and code references untouched.
